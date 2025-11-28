"""问题卡片数据模型"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class RawQuestionItem(BaseModel):
    """LLM初步解析的问题对象，允许宽松的校验"""
    id: int = Field(..., description="问题编号，从1开始", ge=1)
    view_role: str = Field(..., description="提问角色")
    tag: str = Field(..., description="主题标签")
    question: str = Field(..., description="问题正文", min_length=1)
    rationale: str = Field(..., description="提问理由", min_length=1)
    baseline_answer: str = Field(..., description="基准答案", min_length=1)
    support_notes: str = Field(..., description="支撑材料", min_length=1)
    prompt_template: str = Field(..., description="练习提示词", min_length=1)

    # Optional fields
    dimension: Optional[str] = None
    difficulty: Optional[str] = None
    relevance_score: Optional[float] = None


class QuestionItem(BaseModel):
    """经过验证的单个问题信息，用于业务逻辑"""

    id: int = Field(
        ...,
        description="问题编号，从1开始",
        ge=1
    )

    view_role: str = Field(
        ...,
        description="提问角色，例如：'技术面试官', '导师/PI', 'HR', '[工程视角]', '[学术视角]'"
    )

    tag: str = Field(
        ...,
        description="主题标签，例如：'操作系统', '分布式系统', '图像分割', '研究方法论', '项目真实性风险'"
    )

    question: str = Field(
        ...,
        description="问题正文（简体中文），尽量具体、有针对性",
        min_length=5
    )

    rationale: str = Field(
        ...,
        description="提问理由（2-4句话），说明为什么问这个问题、考察什么能力、与简历/目标的关联",
        min_length=10
    )

    baseline_answer: str = Field(
        ...,
        description="基准答案结构：提供回答框架和关键要点，但不编造用户个人经历",
        min_length=20
    )

    support_notes: str = Field(
        ...,
        description="支撑材料：相关概念、经典技术/论文、推荐阅读、搜索关键词等",
        min_length=10
    )

    prompt_template: str = Field(
        ...,
        description="可复用的练习提示词，用户可复制此提示词喂给任意AI进行深度练习。包含占位符（如{your_experience}）",
        min_length=20
    )

    # Multi-agent enhanced fields
    dimension: Optional[Literal[
        "foundation",       # CS基础
        "engineering",      # 工程实践
        "project_depth",    # 项目深度
        "research_method",  # 研究方法论
        "reflection",       # 反思与软技能
        "soft_skill"        # 软技能与职业规划
    ]] = Field(
        default=None,
        description="问题维度分类"
    )

    difficulty: Optional[Literal["basic", "intermediate", "killer"]] = Field(
        default=None,
        description="问题难度"
    )

    relevance_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="相关性评分（0-5）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "view_role": "技术面试官",
                "tag": "分布式系统",
                "question": "你的简历中提到'设计并实现了分布式爬虫系统'，请详细描述你如何解决爬虫任务的分发与调度问题？",
                "rationale": "这个问题考察候选人对分布式系统核心问题的理解深度。",
                "baseline_answer": "一个好的回答应包含：1) 任务分发架构；2) 使用的消息队列；3) 去重策略；4) 容错机制。",
                "support_notes": "关键概念：消息队列、分布式一致性。推荐阅读：《设计数据密集型应用》。",
                "prompt_template": "我在简历中写了'分布式爬虫系统'，面试官问我如何解决任务分发与调度问题。我的实际情况是：{your_experience}。"
            }
        }
