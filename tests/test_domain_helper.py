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
        assert len(domains['engineering']) == 12  # 12 engineering domains (added 5 new: embedded, game_dev, blockchain, security, test_qa)
        assert len(domains['research']) == 11     # 11 research domains (added 5 new: robotics, graph_learning, time_series, federated_learning, ai_safety)

        # Check first engineering domain structure
        first_eng = domains['engineering'][0]
        assert 'value' in first_eng
        assert 'label' in first_eng
        assert 'description' in first_eng

    def test_get_domain_summary(self, helper):
        """Test domain summary statistics"""
        summary = helper.get_domain_summary()

        assert summary['total'] == 23  # Total 23 domains (12 engineering + 11 research)
        assert summary['engineering'] == 12
        assert summary['research'] == 11

    def test_get_all_domains(self, helper):
        """Test getting all domains with complete information"""
        all_domains = helper.get_all_domains()

        assert isinstance(all_domains, dict)
        assert 'engineering' in all_domains
        assert 'research' in all_domains

        # Check that domains have complete structure
        eng_domains = all_domains['engineering']
        assert len(eng_domains) == 12  # 12 engineering domains

        # Verify a specific domain has all fields
        assert 'backend' in eng_domains
        backend = eng_domains['backend']
        assert 'display_name' in backend
        assert 'description' in backend
        assert 'keywords' in backend

    def test_validate_domain_valid_engineering(self, helper):
        """Test validation of valid engineering domain"""
        assert helper.validate_domain('backend') is True
        assert helper.validate_domain('frontend') is True

    def test_validate_domain_valid_research(self, helper):
        """Test validation of valid research domain"""
        # Get first research domain
        all_domains = helper.get_all_domains()
        if all_domains['research']:
            first_research = list(all_domains['research'].keys())[0]
            assert helper.validate_domain(first_research) is True

    def test_validate_domain_invalid(self, helper):
        """Test validation of invalid domain"""
        assert helper.validate_domain('nonexistent_domain_12345') is False
        assert helper.validate_domain('invalid') is False

    def test_validate_domain_none(self, helper):
        """Test validation when domain is None (allowed)"""
        assert helper.validate_domain(None) is True

    def test_validate_domain_empty_string(self, helper):
        """Test validation when domain is empty string (allowed)"""
        assert helper.validate_domain('') is True
