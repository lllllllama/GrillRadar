"""
多源爬虫提供者 / Multi-Source Crawler Provider

TrendRadar风格的多源信息采集提供者，整合GitHub、CSDN等数据源
"""
from typing import List, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.external_info import ExternalInfoSummary
from app.models.user_config import UserConfig
from app.sources.crawlers.base_crawler import BaseCrawler
from app.sources.crawlers.models import RawItem, CrawlerConfig, CrawlerResult
from app.sources.crawlers.github_crawler import GitHubCrawler
from app.sources.crawlers.csdn_crawler import CSDNCrawler
from app.sources.crawlers.trend_aggregator import TrendAggregator

logger = logging.getLogger(__name__)


class MultiSourceCrawlerProvider:
    """
    多源爬虫提供者

    整合多个爬虫，并行抓取，聚合结果
    """

    def __init__(
        self,
        config: Optional[CrawlerConfig] = None,
        enable_github: bool = True,
        enable_csdn: bool = True
    ):
        """
        初始化多源提供者

        Args:
            config: 爬虫配置
            enable_github: 是否启用GitHub爬虫
            enable_csdn: 是否启用CSDN爬虫
        """
        self.config = config or CrawlerConfig()
        self.crawlers: List[BaseCrawler] = []

        # 注册爬虫
        if enable_github:
            self.crawlers.append(GitHubCrawler(self.config))
            logger.info("GitHub crawler enabled")

        if enable_csdn:
            self.crawlers.append(CSDNCrawler(self.config))
            logger.info("CSDN crawler enabled")

        logger.info(f"MultiSourceCrawlerProvider initialized with {len(self.crawlers)} crawlers")

    def retrieve_external_info(
        self,
        user_config: UserConfig,
        resume_keywords: Optional[List[str]] = None
    ) -> Optional[ExternalInfoSummary]:
        """
        检索外部信息

        Args:
            user_config: 用户配置
            resume_keywords: 从简历中提取的关键词

        Returns:
            ExternalInfoSummary 或 None
        """
        try:
            domain = user_config.domain or 'backend'
            keywords = resume_keywords or []

            # 添加目标描述中的关键词
            if user_config.target_desc:
                keywords.extend(self._extract_keywords_from_desc(user_config.target_desc))

            # 去重
            keywords = list(set(keywords))[:5]  # 最多5个关键词

            logger.info(f"Retrieving external info for domain '{domain}' with keywords: {keywords}")

            # 并行爬取所有数据源
            all_results = self._crawl_all_sources(domain, keywords)

            # 合并所有RawItem
            all_items = []
            for result in all_results:
                if result.success:
                    all_items.extend(result.items)
                    logger.info(f"Source '{result.source}': {result.crawled_count} items in {result.duration_ms}ms")
                else:
                    logger.warning(f"Source '{result.source}' failed: {result.error_message}")

            if not all_items:
                logger.info("No external information found")
                return None

            # 聚合为ExternalInfoSummary
            summary = TrendAggregator.aggregate(
                raw_items=all_items,
                domain=domain,
                max_jd=5,
                max_exp=5,
                max_keywords=20
            )

            logger.info(
                f"External info retrieved: {len(summary.job_descriptions)} JDs, "
                f"{len(summary.interview_experiences)} experiences"
            )

            return summary

        except Exception as e:
            logger.error(f"Failed to retrieve external info: {e}", exc_info=True)
            return None

    def _crawl_all_sources(
        self,
        domain: str,
        keywords: List[str]
    ) -> List[CrawlerResult]:
        """
        并行爬取所有数据源

        Args:
            domain: 目标领域
            keywords: 关键词列表

        Returns:
            CrawlerResult列表
        """
        results = []

        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=len(self.crawlers)) as executor:
            # 提交所有爬虫任务
            future_to_crawler = {
                executor.submit(crawler.crawl, domain, keywords): crawler
                for crawler in self.crawlers
            }

            # 收集结果
            for future in as_completed(future_to_crawler):
                crawler = future_to_crawler[future]
                try:
                    result = future.result(timeout=30)  # 30秒超时
                    results.append(result)
                except Exception as e:
                    logger.error(f"Crawler {crawler.source_name} failed: {e}")
                    results.append(CrawlerResult(
                        source=crawler.source_name,
                        success=False,
                        error_message=str(e)
                    ))

        return results

    def _extract_keywords_from_desc(self, description: str) -> List[str]:
        """
        从目标描述中提取关键词

        Args:
            description: 目标描述文本

        Returns:
            关键词列表
        """
        keywords = []

        # 简单的关键词提取（可以用NLP改进）
        tech_terms = [
            'Python', 'Java', 'Go', 'JavaScript', 'TypeScript', 'C++',
            'React', 'Vue', 'Angular', 'Django', 'Flask', 'Spring',
            'MySQL', 'Redis', 'MongoDB', 'Kafka', 'Docker', 'Kubernetes',
            'LLM', 'RAG', 'GPT', 'Transformer', 'PyTorch', 'TensorFlow',
            '分布式', '微服务', '高并发', '后端', '前端', '全栈',
            '算法', '机器学习', '深度学习', '计算机视觉'
        ]

        desc_lower = description.lower()
        for term in tech_terms:
            if term.lower() in desc_lower or term in description:
                keywords.append(term)

        return keywords[:5]

    def get_prompt_summary(self, summary: Optional[ExternalInfoSummary]) -> str:
        """
        获取用于Prompt的摘要文本

        Args:
            summary: 外部信息摘要

        Returns:
            格式化的摘要文本
        """
        if summary is None:
            return "未检索到外部信息。"

        lines = []
        lines.append("### 外部技术趋势参考（来自GitHub、CSDN等真实数据源）")

        # JD信息
        if summary.job_descriptions:
            lines.append(f"\n**技术趋势数据**: {len(summary.job_descriptions)}个相关项目/文章")
            lines.append("**核心技术栈**:")
            if summary.aggregated_keywords:
                keywords_str = "、".join(summary.aggregated_keywords[:15])
                lines.append(f"- {keywords_str}")

        # 面经信息
        if summary.interview_experiences:
            lines.append(f"\n**面试经验参考**: {len(summary.interview_experiences)}条")
            if summary.aggregated_topics:
                topics_str = "、".join(summary.aggregated_topics[:10])
                lines.append(f"**高频主题**: {topics_str}")

            if summary.high_frequency_questions:
                lines.append("\n**高频技术问题示例**:")
                for q in summary.high_frequency_questions[:5]:
                    lines.append(f"- {q}")

        lines.append("\n**提示**: 根据以上真实技术趋势和面经，生成的问题应更贴近当前行业实际。")

        return "\n".join(lines)


# 用于替换现有MockProvider的工厂函数
def create_external_info_provider(
    provider_type: str = "mock",
    crawler_config: Optional[CrawlerConfig] = None
) -> object:
    """
    创建外部信息提供者

    Args:
        provider_type: 提供者类型 ("mock" | "multi_source_crawler")
        crawler_config: 爬虫配置（仅用于multi_source_crawler）

    Returns:
        提供者实例
    """
    if provider_type == "multi_source_crawler":
        return MultiSourceCrawlerProvider(config=crawler_config)
    else:
        # 返回原有的MockProvider
        from app.sources.mock_provider import MockDataProvider
        return MockDataProvider()
