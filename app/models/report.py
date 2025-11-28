"""报告数据模型"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .question_item import QuestionItem, RawQuestionItem


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
    difficulty_distribution: Optional[dict] = None
    question_categories: Optional[List[str]] = None


class RawReport(BaseModel):
    """LLM初步解析的报告对象，允许宽松的校验"""
    summary: str = Field(..., description="总体评估", min_length=1)
    mode: str = Field(..., description="报告模式")
    target_desc: str = Field(..., description="目标岗位")
    highlights: Optional[str] = Field(default="", description="候选人亮点")
    risks: Optional[str] = Field(default="", description="关键风险点")
    questions: List[RawQuestionItem] = Field(..., description="问题列表", min_length=1)
    meta: Optional[Dict[str, Any]] = None  # Allow raw dict for meta or missing


class Report(BaseModel):
    """最终生成的grilling报告，包含总结 + 问题列表 (Strict Validation)"""

    summary: str = Field(
        ...,
        description="总体评估：候选人的优势、风险点、准备建议",
        min_length=30
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
        description="候选人亮点",
        min_length=20
    )

    risks: str = Field(
        ...,
        description="关键风险点",
        min_length=20
    )

    questions: List[QuestionItem] = Field(
        ...,
        description="问题列表",
        min_length=10,
        max_length=50
    )

    meta: ReportMeta = Field(
        ...,
        description="元数据"
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
