"""
Base Agent Abstract Class

All specialized agents inherit from this base class,
ensuring consistent interface and behavior.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import asyncio
import logging
import time

from app.models.user_config import UserConfig
from app.agents.models import DraftQuestion


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str = Field(..., description="Agent identifier (snake_case)")
    display_name: str = Field(..., description="Human-readable agent name")
    role_description: str = Field(..., description="Agent's role and responsibility")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2000, ge=100, le=16000)
    timeout: int = Field(default=30, description="Timeout in seconds")
    min_questions: int = Field(default=2, description="Minimum questions to generate")
    max_questions: int = Field(default=5, description="Maximum questions to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "technical_interviewer",
                "display_name": "技术面试官",
                "role_description": "Evaluates CS fundamentals, system design, technical depth",
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 30,
                "min_questions": 3,
                "max_questions": 5
            }
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents

    All specialized agents (TechnicalInterviewer, HiringManager, etc.)
    inherit from this class and implement the propose_questions method.
    """

    def __init__(self, config: AgentConfig, llm_client):
        """
        Initialize agent

        Args:
            config: Agent configuration
            llm_client: LLM client for making API calls
        """
        self.config = config
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"Agent.{self.__class__.__name__}")

    @abstractmethod
    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """
        Generate initial questions from this agent's perspective

        This is the core method that each agent must implement.

        Args:
            resume_text: Candidate's resume
            user_config: User configuration (mode, domain, etc.)
            context: Additional context (optional)

        Returns:
            List of draft questions with preliminary reasoning

        Raises:
            Exception: If question generation fails
        """
        pass

    def _build_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """
        Build role-specific prompt template

        Override in subclasses to customize prompting strategy.

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context

        Returns:
            Formatted prompt string
        """
        # Default implementation - subclasses should override
        return f"""
你是 {self.config.display_name}。根据候选人简历和目标岗位，生成 {self.config.min_questions}-{self.config.max_questions} 个最想问的问题。

## 简历信息
{resume_text[:2000]}...

## 岗位信息
- 目标: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}
- 模式: {user_config.mode}

## 你的职责
{self.config.role_description}

## 输出格式（JSON）
{{
    "questions": [
        {{
            "question": "具体问题文本",
            "rationale": "为什么问这个问题，考察什么",
            "tags": ["标签1", "标签2"],
            "confidence": 0.85
        }}
    ]
}}
"""

    async def _call_llm_structured(self, prompt: str) -> Dict:
        """
        Call LLM and ensure structured JSON output

        Includes retry logic, JSON parsing, and validation.

        Args:
            prompt: Formatted prompt

        Returns:
            Parsed JSON response

        Raises:
            Exception: If LLM call fails after retries
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Call LLM client (assumes it has a call_json method)
                response = await asyncio.wait_for(
                    self.llm_client.call_json(prompt),
                    timeout=self.config.timeout
                )

                # Validate response structure
                if not isinstance(response, dict):
                    raise ValueError(f"Invalid response type: {type(response)}")

                if "questions" not in response:
                    raise ValueError("Response missing 'questions' field")

                return response

            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                self.logger.error(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

        raise Exception(f"Failed to get valid response after {max_retries} attempts")

    async def generate_with_fallback(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """
        Generate questions with fallback on failure

        Wraps propose_questions with error handling and fallback logic.

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context

        Returns:
            List of draft questions (empty list if all attempts fail)
        """
        try:
            start_time = time.time()
            questions = await self.propose_questions(resume_text, user_config, context)
            elapsed = time.time() - start_time

            self.logger.info(
                f"Generated {len(questions)} questions in {elapsed:.2f}s "
                f"(confidence avg: {sum(q.confidence for q in questions) / len(questions) if questions else 0:.2f})"
            )

            return questions

        except Exception as e:
            self.logger.error(f"Failed to generate questions: {e}")
            # Return empty list rather than raising
            # Orchestrator will handle missing agent contributions
            return []

    def validate_draft_question(self, draft: DraftQuestion) -> bool:
        """
        Validate a draft question

        Checks for basic quality criteria.

        Args:
            draft: Draft question to validate

        Returns:
            True if valid, False otherwise
        """
        # Check minimum lengths
        if len(draft.question) < 10:
            self.logger.warning(f"Question too short: {draft.question}")
            return False

        if len(draft.rationale) < 20:
            self.logger.warning(f"Rationale too short for: {draft.question}")
            return False

        # Check confidence range
        if not (0.0 <= draft.confidence <= 1.0):
            self.logger.warning(f"Invalid confidence: {draft.confidence}")
            return False

        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.config.name}')>"
