"""Tests for ConfigValidator"""

import pytest
import tempfile
import yaml
from pathlib import Path
from app.config.validator import ConfigValidator
from app.exceptions import ConfigurationError


class TestConfigValidator:
    def test_validate_domains_config_success(self):
        """Test validation of valid domains config"""
        # Use real config file
        from app.config.settings import settings

        result = ConfigValidator.validate_domains_config(settings.DOMAINS_CONFIG)
        assert result is True

    def test_validate_modes_config_success(self):
        """Test validation of valid modes config"""
        from app.config.settings import settings

        result = ConfigValidator.validate_modes_config(settings.MODES_CONFIG)
        assert result is True

    def test_validate_all_success(self):
        """Test validation of all configs"""
        result = ConfigValidator.validate_all()
        assert result is True

    def test_invalid_domains_missing_category(self):
        """Test validation fails when category is missing"""
        # Create temporary invalid config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            invalid_config = {
                'engineering': {
                    'backend': {
                        'display_name': '后端开发',
                        'description': '服务端开发',
                        'keywords': ['Java', 'Go', 'Python']
                    }
                }
                # Missing 'research' category
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                ConfigValidator.validate_domains_config(temp_path)

            assert 'research' in str(exc_info.value)
            assert 'Missing required category' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_invalid_domain_missing_field(self):
        """Test validation fails when required field is missing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            invalid_config = {
                'engineering': {
                    'backend': {
                        'display_name': '后端开发',
                        # Missing 'description' and 'keywords'
                    }
                },
                'research': {}
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                ConfigValidator.validate_domains_config(temp_path)

            assert 'backend' in str(exc_info.value)
            assert 'missing required field' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_invalid_domain_wrong_type(self):
        """Test validation fails when field has wrong type"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            invalid_config = {
                'engineering': {
                    'backend': {
                        'display_name': 123,  # Should be string
                        'description': '服务端开发',
                        'keywords': ['Java', 'Go']
                    }
                },
                'research': {}
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                ConfigValidator.validate_domains_config(temp_path)

            assert 'display_name must be a string' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_invalid_domain_too_few_keywords(self):
        """Test validation fails when keywords list is too short"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            invalid_config = {
                'engineering': {
                    'backend': {
                        'display_name': '后端开发',
                        'description': '服务端开发',
                        'keywords': ['Java']  # Need at least 3
                    }
                },
                'research': {}
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                ConfigValidator.validate_domains_config(temp_path)

            assert 'must have at least 3 keywords' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_invalid_modes_missing_mode(self):
        """Test validation fails when required mode is missing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            invalid_config = {
                'job': {
                    'description': 'Job mode',
                    'roles': {'technical_interviewer': 0.5, 'hiring_manager': 0.5}
                }
                # Missing 'grad' and 'mixed'
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                ConfigValidator.validate_modes_config(temp_path)

            assert 'Missing required mode' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_invalid_modes_weights_sum(self):
        """Test validation fails when role weights don't sum to ~1.0"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            invalid_config = {
                'job': {
                    'description': 'Job mode',
                    'roles': {
                        'technical_interviewer': 0.3,
                        'hiring_manager': 0.3  # Sum = 0.6, should be ~1.0
                    }
                },
                'grad': {
                    'description': 'Grad mode',
                    'roles': {'advisor': 1.0}
                },
                'mixed': {
                    'description': 'Mixed mode',
                    'roles': {'technical_interviewer': 1.0}
                }
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                ConfigValidator.validate_modes_config(temp_path)

            assert 'role weights sum to' in str(exc_info.value)
            assert 'should be ~1.0' in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
