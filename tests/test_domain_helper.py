"""Tests for DomainHelper"""

import pytest
from app.utils.domain_helper import DomainHelper


class TestDomainHelper:
    @pytest.fixture
    def helper(self):
        return DomainHelper()

    def test_get_domain_detail_backend(self, helper):
        """Test backend domain retrieval"""
        detail = helper.get_domain_detail('backend')

        assert detail is not None
        assert detail['display_name'] == '后端开发'
        assert 'keywords' in detail
        assert isinstance(detail['keywords'], list)
        assert len(detail['keywords']) > 0

    def test_get_domain_detail_invalid(self, helper):
        """Test invalid domain returns None"""
        detail = helper.get_domain_detail('nonexistent_domain')
        assert detail is None

    def test_get_domains_list_structure(self, helper):
        """Test domains list has correct structure"""
        domains = helper.get_domains_list()

        assert 'engineering' in domains
        assert 'research' in domains
        assert isinstance(domains['engineering'], list)
        assert len(domains['engineering']) == 7  # 7 engineering domains
        assert len(domains['research']) == 6     # 6 research domains

        # Check first engineering domain structure
        first_eng = domains['engineering'][0]
        assert 'value' in first_eng
        assert 'label' in first_eng
        assert 'description' in first_eng

    def test_get_domain_summary(self, helper):
        """Test domain summary statistics"""
        summary = helper.get_domain_summary()

        assert summary['total'] == 13
        assert summary['engineering'] == 7
        assert summary['research'] == 6
