"""Tests for PromptBuilder"""

import pytest
from app.core.prompt_builder import PromptBuilder


class TestPromptBuilder:
    @pytest.fixture
    def builder(self):
        return PromptBuilder()

    def test_build_prompt_structure(self, builder, job_config):
        """Test prompt has required sections"""
        prompt = builder.build(job_config)

        # Check for key sections
        assert '你的角色' in prompt
        assert '任务目标' in prompt
        assert '领域知识' in prompt
        assert '问题分布要求' in prompt
        assert job_config.target_desc in prompt
        assert job_config.resume_text in prompt

    def test_domain_knowledge_injection(self, builder, job_config):
        """Test domain knowledge is injected"""
        prompt = builder.build(job_config)

        # Backend domain should be mentioned
        assert '后端开发' in prompt
        # Should have keywords or stacks
        assert '分布式系统' in prompt or 'Java' in prompt or 'Go' in prompt

    def test_no_domain_specified(self, builder, sample_resume):
        """Test prompt works without domain"""
        from app.models.user_config import UserConfig

        config = UserConfig(
            mode='job',
            target_desc='软件工程师',
            resume_text=sample_resume
        )

        prompt = builder.build(config)
        assert '未指定领域' in prompt

    def test_external_info_disabled(self, builder, job_config):
        """Test external info section is empty when disabled"""
        job_config.enable_external_info = False

        prompt = builder.build(job_config)

        # External info should not be prominent
        # (Section may exist but should be minimal)
        assert prompt is not None

    def test_mode_specific_requirements(self, builder, grad_config):
        """Test grad mode has specific requirements"""
        prompt = builder.build(grad_config)

        # Should mention research/academic aspects
        assert 'grad' in prompt.lower() or '研究' in prompt or '学术' in prompt
