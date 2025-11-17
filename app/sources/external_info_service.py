"""外部信息服务（Milestone 4）

统一管理外部信息源的获取和聚合
"""
import logging
from typing import Optional
from app.models.external_info import ExternalInfoSummary
from app.sources.mock_provider import MockDataProvider
from app.retrieval.info_aggregator import InfoAggregator

logger = logging.getLogger(__name__)


class ExternalInfoService:
    """外部信息服务"""

    def __init__(self, use_mock: bool = True):
        """
        初始化外部信息服务

        Args:
            use_mock: 是否使用模拟数据（默认True）
        """
        self.use_mock = use_mock
        self.mock_provider = MockDataProvider()

    def retrieve_external_info(
        self,
        company: Optional[str] = None,
        position: Optional[str] = None,
        enable_jd: bool = True,
        enable_interview_exp: bool = True
    ) -> Optional[ExternalInfoSummary]:
        """
        检索外部信息

        Args:
            company: 目标公司（可选）
            position: 目标岗位（可选）
            enable_jd: 是否启用JD检索
            enable_interview_exp: 是否启用面经检索

        Returns:
            聚合后的外部信息，如果未找到则返回None
        """
        try:
            jds = []
            experiences = []

            if enable_jd:
                if self.use_mock:
                    jds = self.mock_provider.get_mock_jds(company, position)
                else:
                    # TODO: 实现真实的JD爬虫或API调用
                    logger.warning("Real JD crawler not implemented yet")
                    jds = []

            if enable_interview_exp:
                if self.use_mock:
                    experiences = self.mock_provider.get_mock_experiences(company, position)
                else:
                    # TODO: 实现真实的面经爬虫或API调用
                    logger.warning("Real interview experience crawler not implemented yet")
                    experiences = []

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

        return InfoAggregator.get_summary_for_prompt(summary)


# 全局单例
external_info_service = ExternalInfoService(use_mock=True)
