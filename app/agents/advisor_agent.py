"""
Advisor Agent - Academic Advisor/Mentor

Evaluates research potential, academic curiosity, and mentorship fit
(primarily for graduate school mode).
"""
from typing import List, Optional, Dict
import logging

from app.agents.base_agent import BaseAgent, AgentConfig
from app.agents.models import DraftQuestion
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class AdvisorAgent(BaseAgent):
    """
    Advisor Agent - Academic Mentor Perspective

    Focus Areas:
    - Research potential and curiosity
    - Independent thinking and problem-solving
    - Academic passion and motivation
    - Mentorship compatibility
    - Long-term research commitment
    """

    def __init__(self, llm_client):
        config = AgentConfig(
            name="academic_advisor",
            display_name="学术导师",
            role_description="Evaluates research potential, academic curiosity, and mentorship fit for graduate studies",
            temperature=0.7,
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
        Generate advisor-focused questions

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context

        Returns:
            List of draft questions focusing on research potential
        """
        self.logger.info(f"Advisor Agent generating {self.config.min_questions}-{self.config.max_questions} questions")

        # For job mode, this agent contributes fewer questions
        if user_config.mode == "job":
            self.logger.info("Job mode detected - Advisor agent will contribute minimally")
            return []

        prompt = self._build_advisor_prompt(resume_text, user_config, context)
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
                    "research_area": q.get("research_area", "general"),
                    "evaluation_level": q.get("eval_level", "potential")
                }
            )

            if self.validate_draft_question(draft):
                draft_questions.append(draft)

        self.logger.info(f"Advisor Agent generated {len(draft_questions)} valid questions")
        return draft_questions[:self.config.max_questions]

    def _build_advisor_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """Build advisor-specific prompt"""

        mode_note = ""
        if user_config.mode == "mixed":
            mode_note = "\n注意：这是混合模式，需要同时评估工程实践和学术研究潜力。"

        return f"""你是 {self.config.display_name}（Academic Advisor）。根据候选人简历和目标项目，从学术导师视角生成 {self.config.min_questions}-{self.config.max_questions} 个面试问题。

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
1. **研究兴趣**: 学术热情、研究动机、领域了解
2. **独立思考**: 批判性思维、问题发现能力
3. **学术潜力**: 阅读习惯、学习能力、创新思维
4. **师生匹配**: 研究方向契合度、沟通风格
5. **长期承诺**: 学术规划、职业目标、研究决心

## 提问策略
- 探索候选人的学术好奇心
- 评估独立研究能力
- 了解研究方法论理解
- 判断是否适合长期研究
- 评估与导师的匹配度

## 示例问题方向
- "你最感兴趣的研究问题是什么？为什么？"
- "描述一次你深入研究某个问题的经历"
- "你如何评价和选择要阅读的论文？"
- "你期望导师提供什么样的指导？"
- "你认为做研究最大的挑战是什么？"

## 输出格式（JSON）
{{
    "questions": [
        {{
            "question": "请描述一个你主动深入研究并解决的学术或技术问题，这个过程中你学到了什么？",
            "rationale": "评估候选人的学术好奇心、独立研究能力和学习深度",
            "tags": ["研究潜力", "独立思考", "学术热情"],
            "confidence": 0.85,
            "research_area": "problem_solving",
            "eval_level": "depth"
        }}
    ]
}}

生成 {self.config.min_questions}-{self.config.max_questions} 个高质量问题，重点评估研究潜力和学术契合度。
"""
