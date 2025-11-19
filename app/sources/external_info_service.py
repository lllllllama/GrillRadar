"""外部信息服务（Milestone 4）

统一管理外部信息源的获取和聚合
支持Mock、真实爬虫以及本地数据集三种模式
"""
import logging
import os
from typing import Dict, Optional

from app.models.external_info import ExternalInfoSummary
from app.models.user_config import UserConfig
from app.sources.mock_provider import MockDataProvider
from app.retrieval.info_aggregator import InfoAggregator

logger = logging.getLogger(__name__)


class ExternalInfoService:
    """外部信息服务"""

    def __init__(self, provider_type: str = "mock"):
        """
        初始化外部信息服务

        Args:
            provider_type: 提供者类型
                - "mock": 使用模拟数据（默认，快速）
                - "multi_source_crawler": 使用真实爬虫（GitHub + CSDN）
        """
        self.provider_type = provider_type
        self.logger = logging.getLogger(__name__)
        self._latest_trend_payload: Dict[str, list] = {
            "keyword_trends": [],
            "topic_trends": [],
        }

        # 根据类型初始化提供者
        if provider_type == "multi_source_crawler":
            try:
                from app.sources.multi_source_provider import MultiSourceCrawlerProvider
                from app.sources.crawlers.models import CrawlerConfig

                # 从环境变量读取配置
                crawler_config = CrawlerConfig(
                    max_items=int(os.getenv('CRAWLER_MAX_ITEMS', '20')),
                    timeout=int(os.getenv('CRAWLER_TIMEOUT', '10')),
                    sleep_between_requests=float(os.getenv('CRAWLER_SLEEP', '1.0')),
                    use_cache=os.getenv('CRAWLER_USE_CACHE', 'true').lower() == 'true'
                )

                self.provider = MultiSourceCrawlerProvider(
                    config=crawler_config,
                    enable_github=True,
                    enable_juejin=True,
                    enable_zhihu=True,
                    enable_csdn=False  # 禁用CSDN (SSL握手问题)
                )
                self.logger.info("Using MultiSourceCrawlerProvider (GitHub + Juejin + Zhihu)")
            except Exception as e:
                self.logger.warning(f"Failed to initialize crawler provider: {e}. Falling back to mock.")
                self.provider = MockDataProvider()
                self.provider_type = "mock"
        elif provider_type == "local_dataset":
            try:
                from app.sources.local_dataset_provider import LocalDatasetProvider

                self.provider = LocalDatasetProvider()
                self.logger.info("Using LocalDatasetProvider (curated JSON dataset)")
            except Exception as exc:
                self.logger.warning(
                    "Failed to initialize LocalDatasetProvider: %s. Falling back to mock.",
                    exc,
                )
                self.provider = MockDataProvider()
                self.provider_type = "mock"
        else:
            self.provider = MockDataProvider()
            self.logger.info("Using MockDataProvider (fast, no real crawling)")

    def retrieve_external_info(
        self,
        user_config: Optional[UserConfig] = None,
        company: Optional[str] = None,
        position: Optional[str] = None,
        resume_keywords: Optional[list] = None,
        enable_jd: bool = True,
        enable_interview_exp: bool = True,
        domain: Optional[str] = None,
    ) -> Optional[ExternalInfoSummary]:
        """
        检索外部信息

        Args:
            user_config: 用户配置（优先使用）
            company: 目标公司（可选，用于Mock模式）
            position: 目标岗位（可选，用于Mock模式）
            resume_keywords: 简历关键词（用于爬虫模式）
            enable_jd: 是否启用JD检索
            enable_interview_exp: 是否启用面经检索

        Returns:
            聚合后的外部信息，如果未找到则返回None
        """
        try:
            # 如果使用真实爬虫
            if self.provider_type == "multi_source_crawler" and user_config:
                summary = self.provider.retrieve_external_info(
                    user_config=user_config,
                    resume_keywords=resume_keywords
                )
                return summary

            if self.provider_type == "local_dataset":
                from app.sources.local_dataset_provider import LocalDatasetProvider

                dataset_provider: LocalDatasetProvider = self.provider
                summary = dataset_provider.retrieve_external_info(
                    user_config=user_config,
                    company=company,
                    position=position,
                    domain=domain,
                    enable_jd=enable_jd,
                    enable_interview_exp=enable_interview_exp,
                )
                self._latest_trend_payload = dataset_provider.get_trend_payload()
                return summary

            # 否则使用Mock模式
            jds = []
            experiences = []

            if enable_jd:
                jds = self.provider.get_mock_jds(company, position)

            if enable_interview_exp:
                experiences = self.provider.get_mock_experiences(company, position)

            # 如果都没有找到，返回None
            if not jds and not experiences:
                logger.info("No external information found")
                return None

            # 聚合信息
            summary = InfoAggregator.aggregate(jds, experiences)
            logger.info(f"Retrieved {len(jds)} JDs and {len(experiences)} interview experiences")

            return summary

        except Exception as e:
            logger.error(f"Failed to retrieve external info: {e}", exc_info=True)
            return None

    def get_prompt_summary(self, summary: Optional[ExternalInfoSummary]) -> str:
        """
        获取用于Prompt的摘要文本

        Args:
            summary: 外部信息摘要

        Returns:
            格式化的摘要文本
        """
        if summary is None:
            return "未启用外部信息检索。"

        if self.provider_type == "multi_source_crawler":
            return self.provider.get_prompt_summary(summary)

        if self.provider_type == "local_dataset":
            return self.provider.format_prompt(summary)

        return InfoAggregator.get_summary_for_prompt(summary)

    def get_latest_trends(self) -> Dict[str, list]:
        """Return structured trend payload for API consumers."""

        return self._latest_trend_payload


# 全局单例（默认使用mock，可通过环境变量配置）
_provider_type = os.getenv('EXTERNAL_INFO_PROVIDER', 'mock')
external_info_service = ExternalInfoService(provider_type=_provider_type)
