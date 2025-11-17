"""Tests for UserConfig validation"""

import pytest
from pydantic import ValidationError
from app.models.user_config import UserConfig


class TestUserConfig:
    def test_valid_job_config(self, sample_resume):
        """Test valid job configuration"""
        config = UserConfig(
            mode='job',
            target_desc='后端开发工程师',
            domain='backend',
            resume_text=sample_resume
        )

        assert config.mode == 'job'
        assert config.domain == 'backend'

    def test_invalid_mode(self, sample_resume):
        """Test invalid mode raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            UserConfig(
                mode='invalid_mode',  # ❌ Invalid
                target_desc='工程师',
                resume_text=sample_resume
            )

        # Check error message
        assert 'mode' in str(exc_info.value)

    def test_resume_too_short(self):
        """Test resume length validation"""
        with pytest.raises(ValidationError) as exc_info:
            UserConfig(
                mode='job',
                target_desc='工程师',
                resume_text='短'  # ❌ Too short (< 10 chars)
            )

        assert 'resume_text' in str(exc_info.value)

    def test_external_info_fields(self, sample_resume):
        """Test external info configuration"""
        config = UserConfig(
            mode='job',
            target_desc='字节跳动后端工程师',
            resume_text=sample_resume,
            enable_external_info=True,
            target_company='字节跳动'
        )

        assert config.enable_external_info is True
        assert config.target_company == '字节跳动'
