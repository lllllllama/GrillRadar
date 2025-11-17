"""
HR Agent - Human Resources Specialist

Evaluates soft skills, cultural fit, team collaboration,
and interpersonal competencies.
"""
from typing import List, Optional, Dict
import logging

from app.agents.base_agent import BaseAgent, AgentConfig
from app.agents.models import DraftQuestion
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class HRAgent(BaseAgent):
    """
    HR Agent - Human Resources Perspective

    Focus Areas:
    - Soft skills and emotional intelligence
    - Cultural fit and team collaboration
    - Communication skills
    - Work-life balance and motivation
    - Conflict resolution abilities
    """

    def __init__(self, llm_client):
        config = AgentConfig(
            name="hr_specialist",
            display_name="HR专员",
            role_description="Evaluates soft skills, cultural fit, team collaboration, and interpersonal competencies",
            temperature=0.75,
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
        Generate HR-focused questions

        Args:
            resume_text: Candidate's resume
            user_config: User configuration
            context: Additional context

        Returns:
            List of draft questions focusing on soft skills and cultural fit
        """
        self.logger.info(f"HR Agent generating {self.config.min_questions}-{self.config.max_questions} questions")

        prompt = self._build_hr_prompt(resume_text, user_config, context)
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
                    "soft_skill_category": q.get("category", "communication"),
                    "evaluation_type": q.get("eval_type", "behavioral")
                }
            )

            if self.validate_draft_question(draft):
                draft_questions.append(draft)

        self.logger.info(f"HR Agent generated {len(draft_questions)} valid questions")
        return draft_questions[:self.config.max_questions]

    def _build_hr_prompt(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> str:
        """Build HR-specific prompt"""

        mode_guidance = self._get_mode_guidance(user_config.mode)

        return f"""你是 {self.config.display_name}（HR Specialist）。根据候选人简历和目标岗位，从HR和软技能角度生成 {self.config.min_questions}-{self.config.max_questions} 个面试问题。

## 简历信息
{resume_text[:2500]}

## 岗位信息
- 目标: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}
- 模式: {user_config.mode}

## 你的职责
{self.config.role_description}

{mode_guidance}

## 评估维度
请从以下维度提问：
1. **软技能**: 沟通能力、团队协作、领导力
2. **文化契合**: 价值观匹配、工作风格
3. **情商与应变**: 压力管理、冲突解决
4. **动机与稳定性**: 职业规划、离职原因
5. **学习与成长**: 自我提升、反思能力

## 提问策略
- 使用行为面试法（STAR法则）
- 关注具体案例和实际经历
- 评估候选人的自我认知
- 观察价值观和工作态度

## 输出格式（JSON）
{{
    "questions": [
        {{
            "question": "请描述一次你在团队中遇到意见分歧的经历，你是如何处理的？",
            "rationale": "评估候选人的冲突解决能力和团队协作意识",
            "tags": ["软技能", "团队协作", "冲突解决"],
            "confidence": 0.85,
            "category": "teamwork",
            "eval_type": "behavioral"
        }}
    ]
}}

生成 {self.config.min_questions}-{self.config.max_questions} 个高质量问题，确保覆盖不同的软技能维度。
"""

    def _get_mode_guidance(self, mode: str) -> str:
        """Get mode-specific guidance"""
        if mode == "job":
            return """
## 工作岗位特别关注
- 职业稳定性和离职动机
- 团队协作和企业文化适应
- 抗压能力和工作节奏
- 职业发展规划的清晰度
"""
        elif mode == "grad":
            return """
## 研究生项目特别关注
- 学术团队合作经验
- 导师关系和沟通方式
- 研究压力管理能力
- 学术诚信和道德标准
- 长期研究承诺和动机
"""
        else:  # mixed
            return """
## 混合模式特别关注
- 工程和学术的平衡能力
- 多任务处理和优先级管理
- 适应不同工作环境的灵活性
"""
