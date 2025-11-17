"""
Technical Interviewer Agent

Evaluates CS fundamentals, system design, and technical depth
"""
from typing import List, Optional, Dict, Any
import logging

from app.agents.base_agent import BaseAgent, AgentConfig, DraftQuestion
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class TechnicalInterviewerAgent(BaseAgent):
    """
    Technical Interviewer Agent

    Focuses on:
    - CS fundamentals (algorithms, data structures)
    - System design thinking
    - Technical depth and breadth
    - Project technical complexity
    """

    def __init__(self, llm_client):
        config = AgentConfig(
            name="technical_interviewer",
            display_name="技术面试官",
            role_description="Evaluates CS fundamentals, system design, technical depth, and engineering skills",
            temperature=0.7,
            max_tokens=2500,
            timeout=30,
            min_questions=3,
            max_questions=5
        )
        super().__init__(config, llm_client)

    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """
        Generate 3-5 technical questions

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context

        Returns:
            List of draft technical questions
        """
        prompt = self._build_technical_prompt(resume_text, user_config, context)

        try:
            response = await self._call_llm_structured(prompt)
            draft_questions = []

            for q in response.get("questions", []):
                if not isinstance(q, dict):
                    continue

                draft = DraftQuestion(
                    question=q.get("question", ""),
                    rationale=q.get("rationale", ""),
                    role_name=self.config.name,
                    role_display=self.config.display_name,
                    tags=q.get("tags", []),
                    confidence=q.get("confidence", 0.8),
                    metadata={
                        "complexity": q.get("complexity", "medium"),
                        "category": q.get("category", "general")
                    }
                )

                if self.validate_draft_question(draft):
                    draft_questions.append(draft)

            self.logger.info(f"Generated {len(draft_questions)} technical questions")
            return draft_questions[:self.config.max_questions]

        except Exception as e:
            self.logger.error(f"Failed to propose technical questions: {e}")
            return []

    def _build_technical_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """Build technical interviewer prompt"""
        # Truncate resume if too long
        resume_snippet = resume_text[:2500] if len(resume_text) > 2500 else resume_text

        prompt = f"""你是资深技术面试官。根据候选人简历和目标岗位，生成 {self.config.min_questions}-{self.config.max_questions} 个技术问题。

## 候选人简历
{resume_snippet}

## 目标岗位
- 职位: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}
- 级别: {user_config.level or '未指定'}
- 模式: {user_config.mode}

## 你的评估重点
1. **CS基础** - 算法、数据结构、计算机系统原理
2. **系统设计** - 架构思维、可扩展性、权衡取舍
3. **项目深度** - 技术难点、实际贡献、问题解决能力
4. **技术广度** - 技术栈掌握、学习能力、最佳实践

## 问题生成原则
- 优先针对简历中提到的具体项目和技术
- 问题要有深度，避免纯概念题
- 结合目标岗位要求
- 每个问题都要能暴露候选人的真实水平

## 输出格式（严格JSON）
{{
    "questions": [
        {{
            "question": "具体的技术问题文本",
            "rationale": "为什么问这个问题，考察哪个维度",
            "tags": ["标签1", "标签2"],
            "confidence": 0.85,
            "complexity": "high|medium|low",
            "category": "cs_fundamentals|system_design|project_depth|tech_stack"
        }}
    ]
}}

请生成 {self.config.min_questions}-{self.config.max_questions} 个高质量技术问题。
"""
        return prompt
