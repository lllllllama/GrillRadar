"""
Advocate Agent - Candidate Advocate

Acts as a quality control layer, ensuring fairness, relevance,
and appropriate difficulty of interview questions.
"""
from typing import List, Optional, Dict
import logging

from app.agents.base_agent import BaseAgent, AgentConfig
from app.agents.models import DraftQuestion
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class AdvocateAgent(BaseAgent):
    """
    Advocate Agent - Quality Control & Fairness Checker

    Focus Areas:
    - Question fairness and relevance
    - Appropriate difficulty level
    - Bias detection and mitigation
    - Coverage gaps identification
    - Candidate experience quality
    """

    def __init__(self, llm_client):
        config = AgentConfig(
            name="candidate_advocate",
            display_name="候选人倡导者",
            role_description="Ensures question fairness, appropriate difficulty, and quality candidate experience",
            temperature=0.7,
            max_tokens=2000,
            timeout=30,
            min_questions=1,
            max_questions=3
        )
        super().__init__(config, llm_client)

    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """
        Generate advocate-focused questions

        This agent primarily acts as quality control, but can also
        suggest additional questions if coverage gaps are detected.

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context (may include existing questions)

        Returns:
            List of draft questions to fill coverage gaps
        """
        self.logger.info(f"Advocate Agent generating {self.config.min_questions}-{self.config.max_questions} questions")

        prompt = self._build_advocate_prompt(resume_text, user_config, context)
        response = await self._call_llm_structured(prompt)

        draft_questions = []
        for q in response.get("questions", []):
            draft = DraftQuestion(
                question=q.get("question", ""),
                rationale=q.get("rationale", ""),
                role_name=self.config.name,
                role_display=self.config.display_name,
                tags=q.get("tags", []),
                confidence=q.get("confidence", 0.75),
                metadata={
                    "purpose": q.get("purpose", "coverage"),
                    "fills_gap": q.get("gap", "unknown")
                }
            )

            if self.validate_draft_question(draft):
                draft_questions.append(draft)

        self.logger.info(f"Advocate Agent generated {len(draft_questions)} valid questions")
        return draft_questions[:self.config.max_questions]

    def _build_advocate_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """Build advocate-specific prompt"""

        return f"""你是 {self.config.display_name}（Candidate Advocate）。你的职责是从候选人角度出发，确保面试问题的公平性、相关性和合理性。

## 简历信息
{resume_text[:2500]}

## 岗位信息
- 目标: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}
- 模式: {user_config.mode}

## 你的职责
{self.config.role_description}

你需要识别可能被其他面试官忽略的关键评估点，并补充 {self.config.min_questions}-{self.config.max_questions} 个问题。

## 评估维度
请从以下角度思考：
1. **公平性**: 问题是否给候选人公平展示机会？
2. **相关性**: 问题是否与岗位/项目真正相关？
3. **难度**: 问题难度是否与候选人背景匹配？
4. **覆盖度**: 是否遗漏了候选人的核心优势？
5. **候选人体验**: 面试流程是否尊重和友好？

## 你的任务
识别其他面试官可能忽略的重要方面，补充关键问题：
- 候选人简历中的亮点是否得到充分评估？
- 是否有偏见或不公平的假设？
- 问题难度是否合理（既能展示能力又不过分刁难）？
- 是否给候选人展示独特价值的机会？

## 提问策略
- 关注候选人的核心优势和亮点
- 提供展示潜力的机会
- 平衡挑战性和可答性
- 避免陷阱式或trick问题
- 确保问题具有建设性

## 示例问题方向
- "你简历中提到的XXX项目，能详细介绍你在其中的创新点吗？"
- "你认为自己最大的优势是什么？请用具体例子说明"
- "除了简历中提到的，你还有哪些相关经验想分享？"
- "如果给你充分的资源和时间，你最想探索什么方向？"

## 输出格式（JSON）
{{
    "questions": [
        {{
            "question": "你简历中最引以为豪的成就是什么？当时面临的最大挑战是什么，你是如何克服的？",
            "rationale": "给候选人机会展示核心优势和问题解决能力，确保其亮点得到充分评估",
            "tags": ["优势展示", "问题解决", "成就感"],
            "confidence": 0.8,
            "purpose": "highlight_strengths",
            "gap": "candidate_highlights"
        }}
    ]
}}

生成 {self.config.min_questions}-{self.config.max_questions} 个问题，重点补充可能被忽略的评估维度，确保候选人得到公平全面的评价机会。
"""
