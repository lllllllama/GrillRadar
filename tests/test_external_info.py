import pytest

from app.models.user_config import UserConfig
from app.retrieval.info_aggregator import InfoAggregator
from app.sources.external_info_service import ExternalInfoService
from app.sources.local_dataset_provider import LocalDatasetProvider
from app.sources.mock_provider import MockDataProvider


@pytest.fixture
def user_config() -> UserConfig:
    return UserConfig(
        mode="job",
        target_desc="字节跳动 后端工程师",
        domain="backend",
        resume_text="示例简历内容，包含Python、分布式系统等关键词。",
        enable_external_info=True,
        target_company="字节跳动",
    )


class TestLocalDatasetProvider:
    def test_retrieve_external_info_with_trends(self, user_config):
        provider = LocalDatasetProvider()

        summary = provider.retrieve_external_info(user_config=user_config)

        assert summary is not None
        assert len(summary.job_descriptions) > 0
        assert summary.keyword_trends, "should expose structured keyword trends"
        assert provider.get_trend_payload()["keyword_trends"]

    def test_format_prompt_contains_trends(self, user_config):
        provider = LocalDatasetProvider()
        summary = provider.retrieve_external_info(user_config=user_config)
        prompt = provider.format_prompt(summary)

        assert "高频技能" in prompt
        assert "提示" in prompt


class TestExternalInfoServiceLocalDataset:
    def test_service_returns_prompt_with_trend_keywords(self, user_config):
        service = ExternalInfoService(provider_type="local_dataset")

        summary = service.retrieve_external_info(user_config=user_config)

        assert summary is not None
        prompt = service.get_prompt_summary(summary)
        assert "高频技能" in prompt
        trends = service.get_latest_trends()
        assert trends["keyword_trends"]

    def test_trend_endpoint_cache_resets_when_no_data(self):
        provider = LocalDatasetProvider()
        provider._latest_keyword_trends = []
        payload = provider.get_trend_payload()
        assert payload["keyword_trends"] == []


class TestInfoAggregator:
    def test_aggregate_with_mock_provider(self):
        provider = MockDataProvider()
        summary = InfoAggregator.aggregate(
            provider.get_mock_jds(company="字节跳动"),
            provider.get_mock_experiences(company="字节跳动"),
        )

        assert summary.aggregated_keywords
        assert summary.get_summary_text()

    def test_aggregate_empty_lists(self):
        summary = InfoAggregator.aggregate([], [])
        assert summary.job_descriptions == []
        assert "未找到" in summary.get_summary_text()
