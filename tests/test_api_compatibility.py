"""Tests for API compatibility layer"""

import pytest
from unittest.mock import Mock, patch
from app.utils.api_compatibility import (
    APICompatibility,
    APIProvider,
    APIStatus,
    APIAdapter,
    api_compatibility
)
from app.config.settings import settings


class TestAPIProviderDetection:
    def test_detect_anthropic_official(self):
        """Test detection of official Anthropic API"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', None):
                provider = APICompatibility.detect_provider()
                assert provider == APIProvider.ANTHROPIC

    def test_detect_bigmodel(self):
        """Test detection of BigModel third-party service"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', 'https://open.bigmodel.cn/api/anthropic'):
                provider = APICompatibility.detect_provider()
                assert provider == APIProvider.BIGMODEL

    def test_detect_custom_anthropic(self):
        """Test detection of custom Anthropic-compatible endpoint"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', 'https://custom.api.com/anthropic'):
                provider = APICompatibility.detect_provider()
                assert provider == APIProvider.CUSTOM

    def test_detect_openai(self):
        """Test detection of OpenAI provider"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'openai'):
            provider = APICompatibility.detect_provider()
            assert provider == APIProvider.OPENAI


class TestAPIConfigurationValidation:
    def test_validate_anthropic_with_api_key(self):
        """Test validation with Anthropic API key"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', 'sk-ant-test-key'):
                with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', None):
                    with patch.object(settings, 'DEFAULT_MODEL', 'claude-sonnet-4'):
                        is_valid, message = APICompatibility.validate_api_configuration()
                        assert is_valid is True
                        assert "valid" in message.lower()

    def test_validate_anthropic_with_auth_token(self):
        """Test validation with Anthropic auth token (third-party)"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', None):
                with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', 'test-token'):
                    with patch.object(settings, 'DEFAULT_MODEL', 'claude-sonnet-4'):
                        is_valid, message = APICompatibility.validate_api_configuration()
                        assert is_valid is True

    def test_validate_anthropic_missing_credentials(self):
        """Test validation failure when credentials missing"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', None):
                with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', None):
                    is_valid, message = APICompatibility.validate_api_configuration()
                    assert is_valid is False
                    assert "not configured" in message.lower()

    def test_validate_anthropic_invalid_base_url(self):
        """Test validation failure with invalid base URL"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', 'test-key'):
                with patch.object(settings, 'ANTHROPIC_BASE_URL', 'invalid-url'):
                    with patch.object(settings, 'DEFAULT_MODEL', 'claude-sonnet-4'):
                        is_valid, message = APICompatibility.validate_api_configuration()
                        assert is_valid is False
                        assert "invalid" in message.lower()

    def test_validate_openai_with_api_key(self):
        """Test validation with OpenAI API key"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'openai'):
            with patch.object(settings, 'OPENAI_API_KEY', 'sk-test-key'):
                with patch.object(settings, 'DEFAULT_MODEL', 'gpt-4o'):
                    is_valid, message = APICompatibility.validate_api_configuration()
                    assert is_valid is True
                    assert "valid" in message.lower()

    def test_validate_openai_missing_key(self):
        """Test validation failure when OpenAI key missing"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'openai'):
            with patch.object(settings, 'OPENAI_API_KEY', None):
                is_valid, message = APICompatibility.validate_api_configuration()
                assert is_valid is False
                assert "not configured" in message.lower()

    def test_validate_unsupported_provider(self):
        """Test validation failure for unsupported provider"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'unsupported'):
            is_valid, message = APICompatibility.validate_api_configuration()
            assert is_valid is False
            assert "unsupported" in message.lower()


class TestAPIHealthCheck:
    @pytest.mark.asyncio
    async def test_health_check_anthropic_configured(self):
        """Test health check for configured Anthropic"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', 'test-key'):
                with patch.object(settings, 'DEFAULT_MODEL', 'claude-sonnet-4'):
                    with patch('anthropic.Anthropic'):
                        result = await APICompatibility.check_api_health()

                        assert result["provider"] == "anthropic"
                        assert result["model"] == "claude-sonnet-4"
                        assert result["status"] == APIStatus.HEALTHY
                        assert "configuration" in result

    @pytest.mark.asyncio
    async def test_health_check_not_configured(self):
        """Test health check when not configured"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', None):
                with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', None):
                    result = await APICompatibility.check_api_health()

                    assert result["status"] == APIStatus.NOT_CONFIGURED
                    assert "not configured" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_health_check_import_error(self):
        """Test health check when library not installed"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_API_KEY', 'test-key'):
                with patch('anthropic.Anthropic', side_effect=ImportError("Module not found")):
                    result = await APICompatibility.check_api_health()

                    assert result["status"] == APIStatus.UNAVAILABLE
                    assert "not installed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_health_check_with_custom_endpoint(self):
        """Test health check with custom endpoint"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', 'test-token'):
                with patch.object(settings, 'ANTHROPIC_BASE_URL', 'https://custom.api.com'):
                    with patch.object(settings, 'DEFAULT_MODEL', 'claude-sonnet-4'):
                        with patch('anthropic.Anthropic'):
                            result = await APICompatibility.check_api_health()

                            assert result["status"] == APIStatus.HEALTHY
                            assert "base_url" in result
                            assert "custom endpoint" in result["message"].lower()


class TestProviderInfo:
    def test_get_anthropic_info(self):
        """Test getting Anthropic provider info"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', None):
                info = APICompatibility.get_provider_info()

                assert info["provider"] == "anthropic"
                assert info["name"] == "Anthropic Claude"
                assert "200K tokens" in info["max_context"]
                assert "models" in info
                assert isinstance(info["models"], list)
                assert len(info["models"]) > 0

    def test_get_bigmodel_info(self):
        """Test getting BigModel (third-party) info"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', 'https://open.bigmodel.cn/api/anthropic'):
                info = APICompatibility.get_provider_info()

                assert info["provider"] == "anthropic"
                assert info["detected_type"] == "bigmodel"
                assert info["using_third_party"] is True
                assert info["third_party_name"] == "BigModel (智谱AI)"
                assert "endpoint" in info

    def test_get_openai_info(self):
        """Test getting OpenAI provider info"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'openai'):
            info = APICompatibility.get_provider_info()

            assert info["provider"] == "openai"
            assert info["name"] == "OpenAI GPT"
            assert "128K tokens" in info["max_context"]
            assert "models" in info
            assert "function_calling" in info["supports"]

    def test_get_openai_models_list(self):
        """Test that OpenAI info includes expected models"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'openai'):
            info = APICompatibility.get_provider_info()

            models_str = " ".join(info["models"])
            assert "gpt-4o" in models_str
            assert "gpt-4-turbo" in models_str
            assert "gpt-3.5-turbo" in models_str


class TestProviderComparison:
    def test_compare_providers_structure(self):
        """Test provider comparison structure"""
        comparison = APICompatibility.compare_providers()

        assert "anthropic" in comparison
        assert "openai" in comparison
        assert "recommendation" in comparison

        # Check anthropic details
        assert "strengths" in comparison["anthropic"]
        assert "use_cases" in comparison["anthropic"]
        assert "cost" in comparison["anthropic"]

        # Check openai details
        assert "strengths" in comparison["openai"]
        assert "use_cases" in comparison["openai"]

    def test_compare_providers_recommendation(self):
        """Test that comparison includes recommendation"""
        comparison = APICompatibility.compare_providers()

        assert comparison["recommendation"]["for_grillradar"] == "anthropic"
        assert "reason" in comparison["recommendation"]

    def test_compare_providers_strengths(self):
        """Test that strengths are listed"""
        comparison = APICompatibility.compare_providers()

        # Anthropic should mention context window
        anthropic_strengths = " ".join(comparison["anthropic"]["strengths"]).lower()
        assert "context" in anthropic_strengths or "200k" in anthropic_strengths

        # OpenAI should mention ecosystem
        openai_strengths = " ".join(comparison["openai"]["strengths"]).lower()
        assert "ecosystem" in openai_strengths or "tool" in openai_strengths


class TestAPIAdapter:
    def test_adapter_initialization(self):
        """Test adapter initialization"""
        with patch.object(settings, 'DEFAULT_LLM_PROVIDER', 'anthropic'):
            adapter = APIAdapter()
            assert adapter.provider == "anthropic"

    def test_adapter_custom_provider(self):
        """Test adapter with custom provider"""
        adapter = APIAdapter(provider="openai")
        assert adapter.provider == "openai"

    def test_get_anthropic_client_kwargs(self):
        """Test getting Anthropic client kwargs"""
        with patch.object(settings, 'ANTHROPIC_API_KEY', 'test-key'):
            with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', None):
                with patch.object(settings, 'ANTHROPIC_BASE_URL', None):
                    adapter = APIAdapter(provider="anthropic")
                    kwargs = adapter.get_client_kwargs()

                    assert "api_key" in kwargs
                    assert kwargs["api_key"] == "test-key"
                    assert "base_url" not in kwargs

    def test_get_anthropic_client_kwargs_with_base_url(self):
        """Test getting Anthropic kwargs with custom base URL"""
        with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', 'test-token'):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', 'https://custom.api.com'):
                adapter = APIAdapter(provider="anthropic")
                kwargs = adapter.get_client_kwargs()

                assert "api_key" in kwargs
                assert "base_url" in kwargs
                assert kwargs["base_url"] == "https://custom.api.com"

    def test_get_openai_client_kwargs(self):
        """Test getting OpenAI client kwargs"""
        with patch.object(settings, 'OPENAI_API_KEY', 'test-key'):
            adapter = APIAdapter(provider="openai")
            kwargs = adapter.get_client_kwargs()

            assert "api_key" in kwargs
            assert kwargs["api_key"] == "test-key"

    def test_get_client_kwargs_unsupported_provider(self):
        """Test that unsupported provider raises error"""
        adapter = APIAdapter(provider="unsupported")

        with pytest.raises(ValueError, match="Unsupported provider"):
            adapter.get_client_kwargs()

    def test_validate_model_name_anthropic(self):
        """Test validating Anthropic model names"""
        adapter = APIAdapter(provider="anthropic")

        assert adapter.validate_model_name("claude-sonnet-4") is True
        assert adapter.validate_model_name("claude-opus-4") is True
        assert adapter.validate_model_name("gpt-4o") is False

    def test_validate_model_name_openai(self):
        """Test validating OpenAI model names"""
        adapter = APIAdapter(provider="openai")

        assert adapter.validate_model_name("gpt-4o") is True
        assert adapter.validate_model_name("gpt-3.5-turbo") is True
        assert adapter.validate_model_name("claude-sonnet-4") is False

    def test_get_default_parameters(self):
        """Test getting default parameters"""
        with patch.object(settings, 'LLM_TEMPERATURE', 0.7):
            with patch.object(settings, 'LLM_MAX_TOKENS', 16000):
                with patch.object(settings, 'DEFAULT_MODEL', 'claude-sonnet-4'):
                    adapter = APIAdapter(provider="anthropic")
                    params = adapter.get_default_parameters()

                    assert params["temperature"] == 0.7
                    assert params["max_tokens"] == 16000
                    assert params["model"] == "claude-sonnet-4"


class TestSingletonInstance:
    def test_singleton_instance_exists(self):
        """Test that singleton instance exists"""
        assert api_compatibility is not None
        assert isinstance(api_compatibility, APICompatibility)

    def test_singleton_methods_accessible(self):
        """Test that singleton methods are accessible"""
        # These should not raise errors
        provider = api_compatibility.detect_provider()
        assert isinstance(provider, APIProvider)

        comparison = api_compatibility.compare_providers()
        assert isinstance(comparison, dict)
