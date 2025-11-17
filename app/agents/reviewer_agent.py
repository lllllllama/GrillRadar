"""
Reviewer Agent - Academic Peer Reviewer

Evaluates academic rigor, research methodology, and critical analysis skills
(primarily for graduate school mode).
"""
from typing import List, Optional, Dict
import logging

from app.agents.base_agent import BaseAgent, AgentConfig
from app.agents.models import DraftQuestion
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent - Academic Reviewer Perspective

    Focus Areas:
    - Research methodology and rigor
    - Experimental design and validation
    - Critical thinking and paper evaluation
    - Statistical literacy
    - Academic writing and communication
    """

    def __init__(self, llm_client):
        config = AgentConfig(
            name="academic_reviewer",
            display_name="学术评审",
            role_description="Evaluates research methodology, academic rigor, and critical analysis skills",
            temperature=0.65,
            max_tokens=2000,
            timeout=30,
            min_questions=2,
            max_questions=4
        )
        super().__init__(config, llm_client)

    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """
        Generate reviewer-focused questions

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context

        Returns:
            List of draft questions focusing on academic rigor
        """
        self.logger.info(f"Reviewer Agent generating {self.config.min_questions}-{self.config.max_questions} questions")

        # For job mode, this agent contributes fewer questions
        if user_config.mode == "job":
            self.logger.info("Job mode detected - Reviewer agent will contribute minimally")
            return []

        prompt = self._build_reviewer_prompt(resume_text, user_config, context)
        response = await self._call_llm_structured(prompt)

        draft_questions = []
        for q in response.get("questions", []):
            draft = DraftQuestion(
                question=q.get("question", ""),
                rationale=q.get("rationale", ""),
                role_name=self.config.name,
                role_display=self.config.display_name,
                tags=q.get("tags", []),
                confidence=q.get("confidence", 0.8),
                metadata={
                    "rigor_level": q.get("rigor_level", "medium"),
                    "methodology_focus": q.get("methodology", "general")
                }
            )

            if self.validate_draft_question(draft):
                draft_questions.append(draft)

        self.logger.info(f"Reviewer Agent generated {len(draft_questions)} valid questions")
        return draft_questions[:self.config.max_questions]

    def _build_reviewer_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """Build reviewer-specific prompt"""

        mode_note = ""
        if user_config.mode == "mixed":
            mode_note = "\n注意：这是混合模式，需要评估候选人的研究方法论理解和工程实践的严谨性。"

        return f"""你是 {self.config.display_name}（Academic Reviewer）。根据候选人简历和目标项目，从学术评审视角生成 {self.config.min_questions}-{self.config.max_questions} 个面试问题。

## 简历信息
{resume_text[:2500]}

## 目标项目
- 目标: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}
- 模式: {user_config.mode}
{mode_note}

## 你的职责
{self.config.role_description}

## 评估维度
请从以下维度提问：
1. **方法论**: 研究设计、实验方法、数据收集
2. **严谨性**: 对照组设计、变量控制、结果验证
3. **批判性思维**: 论文评估能力、问题发现
4. **统计素养**: 数据分析、统计方法理解
5. **学术诚信**: 引用规范、数据真实性认知

## 提问策略
- 评估研究方法论的理解深度
- 测试实验设计能力
- 考察批判性阅读和评价能力
- 了解统计和数据分析能力
- 评估学术规范和诚信意识

## 示例问题方向
- "如果要验证某个假设，你会如何设计实验？"
- "描述一篇你认为方法论有问题的论文"
- "你如何评估研究结果的可靠性？"
- "解释你在某个项目中的数据分析方法"
- "如何处理实验中的异常数据？"

## 输出格式（JSON）
{{
    "questions": [
        {{
            "question": "请描述你简历中某个项目的研究方法，如果重新设计，你会如何改进来提高结果的可靠性？",
            "rationale": "评估候选人对研究方法论的理解和批判性思维能力",
            "tags": ["研究方法", "批判性思维", "学术严谨性"],
            "confidence": 0.85,
            "rigor_level": "high",
            "methodology": "experimental_design"
        }}
    ]
}}

生成 {self.config.min_questions}-{self.config.max_questions} 个高质量问题，重点评估学术严谨性和方法论理解。
"""
