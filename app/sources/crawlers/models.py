"""
爬虫数据模型 / Crawler Data Models

定义统一的原始数据结构，供所有爬虫使用
"""
from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class RawItem(BaseModel):
    """
    统一的原始数据项 / Unified Raw Data Item

    所有爬虫返回此标准格式，便于后续聚合处理
    """
    source: Literal["github", "csdn", "leetcode", "zhihu", "nowcoder", "juejin", "v2ex", "ithome"] = Field(
        ...,
        description="数据来源"
    )

    url: str = Field(
        ...,
        description="原始URL"
    )

    title: str = Field(
        ...,
        description="标题"
    )

    snippet: str = Field(
        default="",
        description="摘要/简介/前N个字符"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="从标题/内容提取的标签/关键词"
    )

    created_at: Optional[datetime] = Field(
        None,
        description="创建时间（如果可获取）"
    )

    engagement: Dict[str, int] = Field(
        default_factory=dict,
        description="互动指标：star/view/like/comment等"
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="额外元数据（作者、语言、分类等）"
    )

    crawled_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="爬取时间"
    )

    def get_engagement_score(self) -> int:
        """
        计算综合互动分数

        用于排序和过滤
        """
        score = 0
        score += self.engagement.get('star', 0) * 10
        score += self.engagement.get('like', 0) * 2
        score += self.engagement.get('view', 0) // 100
        score += self.engagement.get('comment', 0) * 1
        return score

    def get_all_text(self) -> str:
        """获取所有文本内容（用于关键词提取）"""
        return f"{self.title} {self.snippet} {' '.join(self.tags)}"


class CrawlerConfig(BaseModel):
    """爬虫配置 / Crawler Configuration"""

    max_items: int = Field(
        default=20,
        description="每个源最多抓取的条目数"
    )

    timeout: int = Field(
        default=10,
        description="请求超时时间（秒）"
    )

    retry_times: int = Field(
        default=2,
        description="失败重试次数"
    )

    sleep_between_requests: float = Field(
        default=1.0,
        description="请求间隔（秒）- 避免被封"
    )

    use_cache: bool = Field(
        default=True,
        description="是否使用缓存"
    )

    cache_ttl: int = Field(
        default=3600,
        description="缓存有效期（秒）"
    )

    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        description="User-Agent"
    )


class CrawlerResult(BaseModel):
    """爬虫结果 / Crawler Result"""

    source: str = Field(..., description="数据源名称")
    items: List[RawItem] = Field(default_factory=list, description="抓取的数据项")
    success: bool = Field(default=True, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    crawled_count: int = Field(default=0, description="成功抓取的数量")
    duration_ms: int = Field(default=0, description="耗时（毫秒）")
