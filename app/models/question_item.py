"""问题卡片数据模型"""
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    """单个问题的完整信息，是报告的核心组成单元"""

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

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "view_role": "技术面试官",
                "tag": "分布式系统",
                "question": "你的简历中提到'设计并实现了分布式爬虫系统'，请详细描述你如何解决爬虫任务的分发与调度问题？用了什么消息队列？如何保证任务不重复、不丢失？",
                "rationale": "这个问题考察候选人对分布式系统核心问题（任务分发、一致性、容错）的理解深度。简历只写了'分布式爬虫'，但没有具体技术细节，需要验证是否真正参与设计，还是仅仅部署了现成框架。对于后端工程师岗位，分布式系统能力是核心要求。",
                "baseline_answer": "一个好的回答应包含：1) 任务分发架构（如Master-Worker模式）；2) 使用的消息队列（如RabbitMQ/Kafka）及选型理由；3) 去重策略（如布隆过滤器、Redis Set）；4) 容错机制（如任务重试、心跳检测）；5) 遇到的坑和优化点（如队列堆积、消费者性能瓶颈）。",
                "support_notes": "关键概念：消息队列（RabbitMQ, Kafka, Redis Stream）、分布式一致性、幂等性、布隆过滤器。推荐阅读：《设计数据密集型应用》第11章、Scrapy-Redis源码。搜索关键词：'distributed task queue', 'deduplication in crawlers'。",
                "prompt_template": "我在简历中写了'分布式爬虫系统'，面试官问我如何解决任务分发与调度问题。我的实际情况是：{your_experience}。请帮我组织一个结构清晰、有技术深度的回答，重点说明架构设计、技术选型、遇到的难点和解决方案。"
            }
        }
