"""
Hiring Manager Agent

Evaluates role fit, business impact, and career trajectory
"""
from typing import List, Optional, Dict
import logging

from app.agents.base_agent import BaseAgent, AgentConfig, DraftQuestion
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class HiringManagerAgent(BaseAgent):
    """
    Hiring Manager Agent

    Focuses on:
    - Role and position fit
    - Business impact and results
    - Career growth and motivation
    - Team and cultural alignment
    """

    def __init__(self, llm_client):
        config = AgentConfig(
            name="hiring_manager",
            display_name="招聘经理",
            role_description="Evaluates role fit, business impact, career trajectory, and motivation",
            temperature=0.7,
            max_tokens=2000,
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
        """Generate 3-5 hiring manager questions"""
        prompt = self._build_hiring_prompt(resume_text, user_config, context)

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
                        "focus_area": q.get("focus_area", "role_fit")
                    }
                )

                if self.validate_draft_question(draft):
                    draft_questions.append(draft)

            return draft_questions[:self.config.max_questions]

        except Exception as e:
            self.logger.error(f"Failed to propose hiring questions: {e}")
            return []

    def _build_hiring_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """Build hiring manager prompt"""
        resume_snippet = resume_text[:2500] if len(resume_text) > 2500 else resume_text

        return f"""你是招聘经理。根据候选人简历和目标岗位，生成 {self.config.min_questions}-{self.config.max_questions} 个面试问题。

## 候选人简历
{resume_snippet}

## 目标岗位
- 职位: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}

## 你的评估重点
1. **岗位匹配** - 技能与岗位要求的吻合度
2. **业务影响** - 过往工作的实际业务价值
3. **职业发展** - 成长轨迹和未来潜力
4. **动机意愿** - 为什么选择这个岗位/公司

## 问题生成原则
- 关注业务价值和impact，而非纯技术
- 挖掘候选人的动机和职业规划
- 评估沟通能力和团队协作
- 结合岗位要求设计场景题

## 输出格式（严格JSON）
{{
    "questions": [
        {{
            "question": "问题文本",
            "rationale": "考察维度和理由",
            "tags": ["标签1", "标签2"],
            "confidence": 0.85,
            "focus_area": "role_fit|business_impact|career_growth|motivation"
        }}
    ]
}}

请生成 {self.config.min_questions}-{self.config.max_questions} 个问题。
"""
