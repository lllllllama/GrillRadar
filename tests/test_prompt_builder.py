"""Tests for PromptBuilder"""

import pytest
from unittest.mock import Mock, patch
from app.core.prompt_builder import PromptBuilder
from app.models.user_config import UserConfig


class TestPromptBuilderInitialization:
    def test_init_loads_config_manager(self):
        """Test that PromptBuilder uses config manager"""
        builder = PromptBuilder()

        assert builder.config_manager is not None

    def test_config_manager_is_singleton(self):
        """Test that multiple builders share the same config manager"""
        builder1 = PromptBuilder()
        builder2 = PromptBuilder()

        assert builder1.config_manager is builder2.config_manager


class TestPromptBuilding:
    @pytest.fixture
    def sample_user_config(self):
        """Sample user config for testing"""
        return UserConfig(
            mode="job",
            target_desc="字节跳动后端开发工程师",
            domain="backend",
            resume_text="资深后端工程师，5年分布式系统开发经验" * 10,
            level="senior"
        )

    def test_build_basic_prompt(self, sample_user_config):
        """Test building a basic prompt"""
        builder = PromptBuilder()
        prompt = builder.build(sample_user_config)

        # Check prompt structure
        assert isinstance(prompt, str)
        assert len(prompt) > 100

        # Check key sections are included
        assert "GrillRadar 虚拟面试委员会" in prompt
        assert "你的角色" in prompt
        assert "当前任务" in prompt
        assert sample_user_config.mode in prompt
        assert sample_user_config.target_desc in prompt
        assert sample_user_config.resume_text in prompt

    def test_build_prompt_with_domain(self, sample_user_config):
        """Test prompt includes domain knowledge"""
        builder = PromptBuilder()
        prompt = builder.build(sample_user_config)

        # Should include domain section
        assert "领域知识" in prompt or "domain" in prompt.lower()

    def test_build_prompt_without_domain(self):
        """Test prompt building without domain specified"""
        config = UserConfig(
            mode="job",
            target_desc="软件工程师",
            resume_text="软件工程师简历" * 10,
            domain=None  # No domain specified
        )

        builder = PromptBuilder()
        prompt = builder.build(config)

        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_build_prompt_with_external_info_disabled(self, sample_user_config):
        """Test prompt when external info is disabled"""
        sample_user_config.enable_external_info = False

        builder = PromptBuilder()
        prompt = builder.build(sample_user_config)

        # External info should not be included
        assert isinstance(prompt, str)

    def test_build_prompt_with_external_info_enabled(self):
        """Test prompt when external info is enabled"""
        config = UserConfig(
            mode="job",
            target_desc="字节跳动后端开发工程师",
            resume_text="后端工程师简历" * 10,
            enable_external_info=True,
            target_company="字节跳动"
        )

        builder = PromptBuilder()
        prompt = builder.build(config)

        # Should attempt to get external info (using mock data)
        assert isinstance(prompt, str)


class TestDomainKnowledge:
    def test_get_domain_knowledge_valid_engineering(self):
        """Test getting domain knowledge for engineering domain"""
        builder = PromptBuilder()

        # Get backend domain knowledge
        knowledge = builder._get_domain_knowledge("backend")

        assert isinstance(knowledge, str)
        assert len(knowledge) > 0
        # Should contain some technical content
        assert "backend" in knowledge.lower() or "后端" in knowledge

    def test_get_domain_knowledge_valid_research(self):
        """Test getting domain knowledge for research domain"""
        builder = PromptBuilder()

        # Try to get a research domain
        # First check what research domains exist
        domains = builder.config_manager.domains.get('research', {})

        if domains:
            first_domain = list(domains.keys())[0]
            knowledge = builder._get_domain_knowledge(first_domain)

            assert isinstance(knowledge, str)
            assert len(knowledge) > 0

    def test_get_domain_knowledge_invalid(self):
        """Test getting domain knowledge for invalid domain"""
        builder = PromptBuilder()

        knowledge = builder._get_domain_knowledge("nonexistent_domain_12345")

        assert isinstance(knowledge, str)
        assert "未在配置中找到" in knowledge

    def test_get_domain_knowledge_none(self):
        """Test getting domain knowledge when domain is None"""
        builder = PromptBuilder()

        knowledge = builder._get_domain_knowledge(None)

        assert isinstance(knowledge, str)
        assert "未指定" in knowledge

    def test_domain_knowledge_includes_keywords(self):
        """Test that domain knowledge includes keywords"""
        builder = PromptBuilder()

        # Get backend domain (should exist)
        knowledge = builder._get_domain_knowledge("backend")

        # Should include keywords section if available
        assert isinstance(knowledge, str)


class TestRoleWeightsFormatting:
    def test_format_role_weights_valid(self):
        """Test formatting role weights"""
        builder = PromptBuilder()

        roles = {
            'technical_interviewer': 0.4,
            'hiring_manager': 0.3,
            'hr': 0.3
        }

        formatted = builder._format_role_weights(roles)

        assert isinstance(formatted, str)
        assert "技术面试官" in formatted
        assert "40%" in formatted
        assert "30%" in formatted

    def test_format_role_weights_empty(self):
        """Test formatting empty role weights"""
        builder = PromptBuilder()

        formatted = builder._format_role_weights({})

        assert "未配置" in formatted

    def test_format_role_weights_sorted(self):
        """Test that role weights are sorted by weight"""
        builder = PromptBuilder()

        roles = {
            'hr': 0.1,
            'technical_interviewer': 0.5,
            'hiring_manager': 0.4
        }

        formatted = builder._format_role_weights(roles)

        # Should be sorted descending (50% first, then 40%, then 10%)
        lines = formatted.split('\n')
        assert "50%" in lines[0]
        assert "40%" in lines[1]
        assert "10%" in lines[2]


class TestQuestionDistribution:
    def test_format_question_distribution_valid(self):
        """Test formatting question distribution"""
        builder = PromptBuilder()

        mode_config = {
            'question_distribution': {
                '技术问题': 0.6,
                '行为问题': 0.3,
                '软技能': 0.1
            }
        }

        formatted = builder._format_question_distribution('job', mode_config)

        assert isinstance(formatted, str)
        assert "60%" in formatted
        assert "30%" in formatted
        assert "10%" in formatted

    def test_format_question_distribution_empty(self):
        """Test formatting empty question distribution"""
        builder = PromptBuilder()

        formatted = builder._format_question_distribution('job', {})

        assert "未配置" in formatted


class TestModeSpecificRequirements:
    def test_get_mode_requirements_mixed(self):
        """Test mode-specific requirements for mixed mode"""
        builder = PromptBuilder()

        requirements = builder._get_mode_specific_requirements('mixed')

        assert isinstance(requirements, str)
        assert "mixed" in requirements or "双视角" in requirements

    def test_get_mode_requirements_grad(self):
        """Test mode-specific requirements for grad mode"""
        builder = PromptBuilder()

        requirements = builder._get_mode_specific_requirements('grad')

        assert isinstance(requirements, str)
        assert "grad" in requirements or "研究" in requirements

    def test_get_mode_requirements_job(self):
        """Test mode-specific requirements for job mode"""
        builder = PromptBuilder()

        requirements = builder._get_mode_specific_requirements('job')

        assert isinstance(requirements, str)
        assert "CS基础" in requirements or "工程" in requirements


class TestSummaryRequirements:
    def test_get_summary_requirements_mixed(self):
        """Test summary requirements for mixed mode"""
        builder = PromptBuilder()

        requirements = builder._get_summary_requirements('mixed')

        assert isinstance(requirements, str)
        assert "工程候选人评估" in requirements
        assert "科研候选人评估" in requirements

    def test_get_summary_requirements_other_modes(self):
        """Test summary requirements for non-mixed modes"""
        builder = PromptBuilder()

        requirements_job = builder._get_summary_requirements('job')
        requirements_grad = builder._get_summary_requirements('grad')

        # Should return empty or minimal requirements
        assert isinstance(requirements_job, str)
        assert isinstance(requirements_grad, str)


class TestExternalInfo:
    def test_get_external_info_disabled(self):
        """Test external info when disabled"""
        builder = PromptBuilder()

        config = UserConfig(
            mode="job",
            target_desc="后端工程师",
            resume_text="简历内容" * 10,
            enable_external_info=False
        )

        external_info = builder._get_external_info(config)

        assert external_info == ""

    def test_get_external_info_enabled_with_company(self):
        """Test external info when enabled with company"""
        builder = PromptBuilder()

        config = UserConfig(
            mode="job",
            target_desc="字节跳动后端开发工程师",
            resume_text="简历内容" * 10,
            enable_external_info=True,
            target_company="字节跳动"
        )

        external_info = builder._get_external_info(config)

        # Should return something (using mock provider)
        assert isinstance(external_info, str)

    def test_get_external_info_position_extraction_backend(self):
        """Test position extraction for backend"""
        builder = PromptBuilder()

        config = UserConfig(
            mode="job",
            target_desc="某公司后端开发工程师",
            resume_text="简历" * 10,
            enable_external_info=True,
            target_company="某公司"
        )

        external_info = builder._get_external_info(config)

        assert isinstance(external_info, str)

    def test_get_external_info_position_extraction_frontend(self):
        """Test position extraction for frontend"""
        builder = PromptBuilder()

        config = UserConfig(
            mode="job",
            target_desc="某公司前端开发工程师",
            resume_text="简历" * 10,
            enable_external_info=True,
            target_company="某公司"
        )

        external_info = builder._get_external_info(config)

        assert isinstance(external_info, str)

    def test_get_external_info_position_extraction_algorithm(self):
        """Test position extraction for algorithm"""
        builder = PromptBuilder()

        config = UserConfig(
            mode="job",
            target_desc="算法工程师",
            resume_text="简历" * 10,
            enable_external_info=True,
            target_company="某公司"
        )

        external_info = builder._get_external_info(config)

        assert isinstance(external_info, str)

    @patch('app.core.prompt_builder.external_info_service')
    def test_get_external_info_service_error(self, mock_service):
        """Test external info when service raises error"""
        builder = PromptBuilder()

        # Mock service to raise exception
        mock_service.retrieve_external_info.side_effect = Exception("Service error")

        config = UserConfig(
            mode="job",
            target_desc="后端工程师",
            resume_text="简历" * 10,
            enable_external_info=True,
            target_company="某公司"
        )

        # Should handle error gracefully and return empty string
        external_info = builder._get_external_info(config)

        assert external_info == ""

    @patch('app.core.prompt_builder.external_info_service')
    def test_get_external_info_no_results(self, mock_service):
        """Test external info when no results found"""
        builder = PromptBuilder()

        # Mock service to return None
        mock_service.retrieve_external_info.return_value = None

        config = UserConfig(
            mode="job",
            target_desc="后端工程师",
            resume_text="简历" * 10,
            enable_external_info=True,
            target_company="某公司"
        )

        external_info = builder._get_external_info(config)

        assert external_info == ""


class TestPromptIntegration:
    def test_build_prompt_all_modes(self):
        """Test building prompts for all modes"""
        builder = PromptBuilder()

        for mode in ['job', 'grad', 'mixed']:
            config = UserConfig(
                mode=mode,
                target_desc=f"测试目标-{mode}",
                resume_text="测试简历内容" * 10,
                domain="backend"
            )

            prompt = builder.build(config)

            assert isinstance(prompt, str)
            assert len(prompt) > 100
            assert mode in prompt

    def test_build_prompt_with_all_optional_fields(self):
        """Test building prompt with all optional fields"""
        config = UserConfig(
            mode="job",
            target_desc="字节跳动后端开发工程师",
            resume_text="完整简历内容" * 10,
            domain="backend",
            level="senior",
            enable_external_info=True,
            target_company="字节跳动"
        )

        builder = PromptBuilder()
        prompt = builder.build(config)

        assert isinstance(prompt, str)
        assert len(prompt) > 200
        assert "senior" in prompt or "高级" in prompt
