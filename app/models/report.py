"""报告数据模型"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .question_item import QuestionItem


class ReportMeta(BaseModel):
    """报告元数据"""
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="生成时间（ISO 8601格式）"
    )
    model: str = Field(
        default="claude-sonnet-4",
        description="使用的LLM模型"
    )
    config_version: str = Field(
        default="v1.0",
        description="配置版本"
    )
    num_questions: int = Field(
        ...,
        description="问题总数",
        ge=1
    )


class Report(BaseModel):
    """最终生成的grilling报告，包含总结 + 问题列表"""

    summary: str = Field(
        ...,
        description="总体评估：候选人的优势、风险点、准备建议。语气略带grilling但建设性强",
        min_length=100
    )

    mode: str = Field(
        ...,
        description="报告模式：job / grad / mixed",
        pattern="^(job|grad|mixed)$"
    )

    target_desc: str = Field(
        ...,
        description="用户的目标岗位/方向"
    )

    highlights: str = Field(
        ...,
        description="候选人亮点：从简历和问题设计中推断出的优势",
        min_length=50
    )

    risks: str = Field(
        ...,
        description="关键风险点：简历暴露的薄弱环节",
        min_length=50
    )

    questions: List[QuestionItem] = Field(
        ...,
        description="问题列表，通常10-20个",
        min_length=10,
        max_length=20
    )

    meta: ReportMeta = Field(
        ...,
        description="元数据：生成时间、LLM模型版本、配置参数等"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "作为一名后端开发候选人，你的简历展示了较好的工程实践经验...",
                "mode": "job",
                "target_desc": "字节跳动 - 抖音推荐后端研发工程师（校招）",
                "highlights": "1. 有分布式爬虫和微服务项目经验...",
                "risks": "1. 项目描述缺少量化指标...",
                "questions": [],
                "meta": {
                    "generated_at": "2025-11-17T14:30:00Z",
                    "model": "claude-sonnet-4",
                    "config_version": "v1.0",
                    "num_questions": 15
                }
            }
        }
