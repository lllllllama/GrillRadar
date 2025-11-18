"""Models describing structured external information for GrillRadar."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    """职位描述（JD）"""

    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位名称")
    location: Optional[str] = Field(None, description="工作地点")
    salary_range: Optional[str] = Field(None, description="薪资范围")

    requirements: List[str] = Field(
        default_factory=list,
        description="岗位要求列表"
    )

    responsibilities: List[str] = Field(
        default_factory=list,
        description="工作职责列表"
    )

    keywords: List[str] = Field(
        default_factory=list,
        description="提取的关键技能和技术栈"
    )

    source_url: Optional[str] = Field(None, description="来源URL")
    crawled_at: Optional[datetime] = Field(None, description="爬取时间")

    class Config:
        json_schema_extra = {
            "example": {
                "company": "字节跳动",
                "position": "后端开发工程师",
                "location": "北京",
                "salary_range": "30k-50k",
                "requirements": [
                    "3年以上后端开发经验",
                    "精通Java或Go语言",
                    "熟悉分布式系统设计",
                    "有高并发系统开发经验"
                ],
                "responsibilities": [
                    "负责推荐系统后端开发",
                    "参与系统架构设计和优化",
                    "保证系统稳定性和可用性"
                ],
                "keywords": [
                    "Java", "Go", "分布式系统", "高并发",
                    "Redis", "Kafka", "MySQL"
                ],
                "source_url": "https://job.bytedance.com/...",
                "crawled_at": "2025-11-17T10:00:00Z"
            }
        }


class InterviewExperience(BaseModel):
    """面经（面试经历分享）"""

    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位名称")
    interview_type: str = Field(
        ...,
        description="面试类型：技术面/HR面/总监面等"
    )

    questions: List[str] = Field(
        default_factory=list,
        description="面试问题列表"
    )

    difficulty: Optional[str] = Field(
        None,
        description="难度：简单/中等/困难"
    )

    topics: List[str] = Field(
        default_factory=list,
        description="涉及的技术主题"
    )

    tips: Optional[str] = Field(
        None,
        description="面试建议和提示"
    )

    source_url: Optional[str] = Field(None, description="来源URL")
    shared_at: Optional[datetime] = Field(None, description="分享时间")

    class Config:
        json_schema_extra = {
            "example": {
                "company": "字节跳动",
                "position": "后端开发工程师",
                "interview_type": "技术面",
                "questions": [
                    "讲一下你做过的最复杂的系统设计",
                    "如何设计一个分布式锁？",
                    "Redis和MySQL的数据一致性如何保证？",
                    "讲一下你在项目中遇到的最大挑战"
                ],
                "difficulty": "中等",
                "topics": [
                    "系统设计", "分布式系统", "数据库",
                    "缓存", "项目经验"
                ],
                "tips": "重点考察项目深度和系统设计能力",
                "source_url": "https://www.nowcoder.com/...",
                "shared_at": "2025-11-15T14:30:00Z"
            }
        }


class KeywordTrend(BaseModel):
    """结构化的关键字趋势信息"""

    keyword: str = Field(..., description="技能或主题关键词")
    frequency: int = Field(..., description="在数据集中出现的次数")
    weight: float = Field(1.0, description="结合领域权重后的得分")
    sources: List[str] = Field(
        default_factory=list,
        description="该关键词出现的公司或数据源"
    )


class TopicTrend(BaseModel):
    """面经主题趋势"""

    topic: str = Field(..., description="面试主题")
    frequency: int = Field(..., description="出现次数")


class ExternalInfoSummary(BaseModel):
    """外部信息汇总"""

    job_descriptions: List[JobDescription] = Field(
        default_factory=list,
        description="相关JD列表"
    )

    interview_experiences: List[InterviewExperience] = Field(
        default_factory=list,
        description="相关面经列表"
    )

    aggregated_keywords: List[str] = Field(
        default_factory=list,
        description="聚合的关键词（去重、排序）"
    )

    aggregated_topics: List[str] = Field(
        default_factory=list,
        description="聚合的主题（去重、排序）"
    )

    high_frequency_questions: List[str] = Field(
        default_factory=list,
        description="高频问题列表"
    )

    keyword_trends: List[KeywordTrend] = Field(
        default_factory=list,
        description="结构化的高频技能趋势"
    )

    topic_trends: List[TopicTrend] = Field(
        default_factory=list,
        description="结构化的高频面试主题"
    )

    retrieved_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="检索时间"
    )

    def get_summary_text(self) -> str:
        """获取格式化的汇总文本"""
        lines = []

        if self.job_descriptions:
            lines.append(f"**找到 {len(self.job_descriptions)} 个相关JD**")
            for jd in self.job_descriptions[:3]:  # 最多显示3个
                lines.append(f"- {jd.company} - {jd.position}")

        if self.interview_experiences:
            lines.append(f"\n**找到 {len(self.interview_experiences)} 条相关面经**")
            for exp in self.interview_experiences[:3]:  # 最多显示3个
                lines.append(f"- {exp.company} - {exp.position} ({exp.interview_type})")

        if self.aggregated_keywords:
            keywords_str = "、".join(self.aggregated_keywords[:15])
            lines.append(f"\n**核心技能要求**: {keywords_str}")

        if self.high_frequency_questions:
            lines.append(f"\n**高频面试题**:")
            for q in self.high_frequency_questions[:5]:
                lines.append(f"- {q}")

        if self.keyword_trends:
            trend_str = "、".join(
                [
                    f"{trend.keyword}(x{trend.frequency})"
                    for trend in self.keyword_trends[:8]
                ]
            )
            lines.append(f"\n**高频技能趋势**: {trend_str}")

        if self.topic_trends:
            topic_trend_str = "、".join(
                [f"{trend.topic}(x{trend.frequency})" for trend in self.topic_trends[:6]]
            )
            lines.append(f"\n**热点面试主题**: {topic_trend_str}")

        return "\n".join(lines) if lines else "未找到相关外部信息"
