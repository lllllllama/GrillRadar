"""Tests for External Info Service and Aggregator"""

import pytest
from app.sources.external_info_service import ExternalInfoService
from app.sources.mock_provider import MockDataProvider
from app.retrieval.info_aggregator import InfoAggregator


class TestMockDataProvider:
    def test_get_mock_jds_no_filter(self):
        """Test getting all JDs without filter"""
        provider = MockDataProvider()
        jds = provider.get_mock_jds()

        assert len(jds) > 0
        assert all(hasattr(jd, 'company') for jd in jds)
        assert all(hasattr(jd, 'position') for jd in jds)
        assert all(hasattr(jd, 'keywords') for jd in jds)

    def test_get_mock_jds_with_company_filter(self):
        """Test filtering JDs by company"""
        provider = MockDataProvider()
        jds = provider.get_mock_jds(company='字节跳动')

        assert len(jds) > 0
        assert all(jd.company == '字节跳动' for jd in jds)

    def test_get_mock_jds_with_position_filter(self):
        """Test filtering JDs by position"""
        provider = MockDataProvider()
        jds = provider.get_mock_jds(position='后端')

        assert len(jds) > 0
        assert all('后端' in jd.position for jd in jds)

    def test_get_mock_experiences_no_filter(self):
        """Test getting all experiences without filter"""
        provider = MockDataProvider()
        experiences = provider.get_mock_experiences()

        assert len(experiences) > 0
        assert all(hasattr(exp, 'company') for exp in experiences)
        assert all(hasattr(exp, 'questions') for exp in experiences)
        assert all(hasattr(exp, 'topics') for exp in experiences)

    def test_get_mock_experiences_with_company_filter(self):
        """Test filtering experiences by company"""
        provider = MockDataProvider()
        experiences = provider.get_mock_experiences(company='字节跳动')

        assert len(experiences) > 0
        assert all(exp.company == '字节跳动' for exp in experiences)


class TestExternalInfoService:
    def test_retrieve_external_info_success(self):
        """Test successful external info retrieval"""
        service = ExternalInfoService(use_mock=True)

        summary = service.retrieve_external_info(
            company='字节跳动',
            position='后端',
            enable_jd=True,
            enable_interview_exp=True
        )

        assert summary is not None
        assert len(summary.job_descriptions) > 0
        assert len(summary.interview_experiences) > 0
        assert len(summary.aggregated_keywords) > 0

    def test_retrieve_external_info_jd_only(self):
        """Test retrieval with JD only"""
        service = ExternalInfoService(use_mock=True)

        summary = service.retrieve_external_info(
            company='字节跳动',
            enable_jd=True,
            enable_interview_exp=False
        )

        assert summary is not None
        assert len(summary.job_descriptions) > 0
        assert len(summary.interview_experiences) == 0

    def test_retrieve_external_info_experience_only(self):
        """Test retrieval with experiences only"""
        service = ExternalInfoService(use_mock=True)

        summary = service.retrieve_external_info(
            company='字节跳动',
            enable_jd=False,
            enable_interview_exp=True
        )

        assert summary is not None
        assert len(summary.job_descriptions) == 0
        assert len(summary.interview_experiences) > 0

    def test_get_prompt_summary_with_data(self):
        """Test getting prompt summary with data"""
        service = ExternalInfoService(use_mock=True)

        summary = service.retrieve_external_info(
            company='字节跳动',
            position='后端'
        )

        prompt_text = service.get_prompt_summary(summary)

        assert prompt_text is not None
        assert len(prompt_text) > 0
        assert '外部信息' in prompt_text or 'JD' in prompt_text

    def test_get_prompt_summary_none(self):
        """Test getting prompt summary with None"""
        service = ExternalInfoService(use_mock=True)

        prompt_text = service.get_prompt_summary(None)

        assert '未启用' in prompt_text or '未检索' in prompt_text


class TestInfoAggregator:
    def test_aggregate_empty_lists(self):
        """Test aggregation with empty lists"""
        summary = InfoAggregator.aggregate([], [])

        assert summary is not None
        assert len(summary.job_descriptions) == 0
        assert len(summary.interview_experiences) == 0
        assert len(summary.aggregated_keywords) == 0

    def test_aggregate_keywords(self):
        """Test keyword aggregation"""
        provider = MockDataProvider()
        jds = provider.get_mock_jds(company='字节跳动', position='后端')
        experiences = provider.get_mock_experiences(company='字节跳动')

        summary = InfoAggregator.aggregate(jds, experiences)

        # Should have aggregated keywords
        assert len(summary.aggregated_keywords) > 0

        # Common keywords should appear
        keywords_str = ' '.join(summary.aggregated_keywords)
        # At least some tech keywords should be present
        assert any(kw in keywords_str for kw in ['Java', 'Go', 'Python', 'MySQL', 'Redis'])

    def test_aggregate_topics(self):
        """Test topic aggregation"""
        provider = MockDataProvider()
        experiences = provider.get_mock_experiences(company='字节跳动')

        summary = InfoAggregator.aggregate([], experiences)

        # Should have aggregated topics
        assert len(summary.aggregated_topics) > 0

    def test_aggregate_high_frequency_questions(self):
        """Test high-frequency question extraction"""
        provider = MockDataProvider()
        experiences = provider.get_mock_experiences(company='字节跳动')

        summary = InfoAggregator.aggregate([], experiences)

        # Should extract some high-frequency questions
        assert isinstance(summary.high_frequency_questions, list)
        # Questions should come from experiences
        if len(experiences) > 0:
            assert len(summary.high_frequency_questions) > 0

    def test_get_summary_for_prompt(self):
        """Test formatted summary for prompt"""
        provider = MockDataProvider()
        jds = provider.get_mock_jds(company='字节跳动', position='后端')
        experiences = provider.get_mock_experiences(company='字节跳动')

        summary = InfoAggregator.aggregate(jds, experiences)
        prompt_text = InfoAggregator.get_summary_for_prompt(summary)

        assert len(prompt_text) > 0
        assert '外部信息' in prompt_text
        # Should contain some structured content
        assert '核心技能要求' in prompt_text or '高频' in prompt_text

    def test_get_summary_for_prompt_empty(self):
        """Test formatted summary for prompt with empty data"""
        summary = InfoAggregator.aggregate([], [])
        prompt_text = InfoAggregator.get_summary_for_prompt(summary)

        # Should return a message indicating no external info
        assert "未检索" in prompt_text

    def test_extract_requirements_keywords_work_experience(self):
        """Test extracting work experience keywords"""
        from app.models.external_info import JobDescription

        jd = JobDescription(
            company="测试公司",
            position="测试岗位",
            requirements=["3年以上工作经验", "熟悉后端开发"],
            keywords=[]
        )

        keywords = InfoAggregator.extract_requirements_keywords(jd)

        assert "工作经验" in keywords

    def test_extract_requirements_keywords_programming_languages(self):
        """Test extracting programming language keywords"""
        from app.models.external_info import JobDescription

        jd = JobDescription(
            company="测试公司",
            position="测试岗位",
            requirements=["熟练掌握Java/Go/Python", "C++开发经验"],
            keywords=[]
        )

        keywords = InfoAggregator.extract_requirements_keywords(jd)

        assert "编程语言" in keywords

    def test_extract_requirements_keywords_distributed_systems(self):
        """Test extracting distributed systems keywords"""
        from app.models.external_info import JobDescription

        jd = JobDescription(
            company="测试公司",
            position="测试岗位",
            requirements=["熟悉分布式系统架构", "有高并发系统经验"],
            keywords=[]
        )

        keywords = InfoAggregator.extract_requirements_keywords(jd)

        assert "分布式系统" in keywords
        assert "高并发" in keywords

    def test_extract_requirements_keywords_database(self):
        """Test extracting database keywords"""
        from app.models.external_info import JobDescription

        jd = JobDescription(
            company="测试公司",
            position="测试岗位",
            requirements=["熟悉MySQL数据库", "Redis使用经验"],
            keywords=[]
        )

        keywords = InfoAggregator.extract_requirements_keywords(jd)

        assert "数据库" in keywords

    def test_extract_requirements_keywords_with_existing_keywords(self):
        """Test that existing JD keywords are included"""
        from app.models.external_info import JobDescription

        jd = JobDescription(
            company="测试公司",
            position="测试岗位",
            requirements=["3年工作经验"],
            keywords=["微服务", "云计算"]
        )

        keywords = InfoAggregator.extract_requirements_keywords(jd)

        # Should include both extracted and existing keywords
        assert "工作经验" in keywords
        assert "微服务" in keywords
        assert "云计算" in keywords

    def test_extract_requirements_keywords_multiple_conditions(self):
        """Test extracting keywords with multiple matching conditions"""
        from app.models.external_info import JobDescription

        jd = JobDescription(
            company="测试公司",
            position="测试岗位",
            requirements=[
                "5年以上Java开发经验",
                "熟悉分布式系统和高并发架构",
                "精通MySQL和Redis数据库"
            ],
            keywords=["Kafka", "Docker"]
        )

        keywords = InfoAggregator.extract_requirements_keywords(jd)

        # Should extract all matching keywords
        assert "工作经验" in keywords
        assert "编程语言" in keywords
        assert "分布式系统" in keywords
        assert "高并发" in keywords
        assert "数据库" in keywords
        assert "Kafka" in keywords
        assert "Docker" in keywords
