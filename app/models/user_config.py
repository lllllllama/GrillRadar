"""用户配置数据模型"""
from typing import Optional
from pydantic import BaseModel, Field


class UserConfig(BaseModel):
    """用户输入的配置信息，驱动报告生成的各个环节"""

    mode: str = Field(
        ...,
        description="模式：job(工程求职) / grad(学术/读研) / mixed(双视角)",
        pattern="^(job|grad|mixed)$"
    )

    target_desc: str = Field(
        ...,
        description="目标描述，例如：'字节跳动LLM应用工程师' 或 '清华大学某实验室图像分割方向硕士'",
        min_length=1
    )

    domain: Optional[str] = Field(
        None,
        description="领域标签，例如：backend, llm_application, cv_segmentation, nlp, rs_recommendation"
    )

    language: str = Field(
        default="zh",
        description="输出语言，默认zh（简体中文），未来支持en"
    )

    level: Optional[str] = Field(
        None,
        description="候选人级别：intern, junior, senior, master, phd。影响问题难度和期望深度",
        pattern="^(intern|junior|senior|master|phd)$"
    )

    resume_text: str = Field(
        ...,
        description="简历原文（纯文本或Markdown格式）",
        min_length=10
    )

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "job",
                "target_desc": "字节跳动 - 抖音推荐后端研发工程师（校招）",
                "domain": "backend",
                "language": "zh",
                "level": "junior",
                "resume_text": "姓名：张三\n教育背景：XX大学 计算机科学与技术 本科\n项目经历：\n1. 分布式爬虫系统..."
            }
        }
