"""
API Compatibility Layer and Health Checks
Ensures GrillRadar works seamlessly with multiple LLM providers
"""
import asyncio
import logging
from typing import Dict, Optional, Tuple
from enum import Enum

from app.config.settings import settings

logger = logging.getLogger(__name__)


class APIProvider(str, Enum):
    """Supported API providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    BIGMODEL = "bigmodel"  # Anthropic-compatible third-party
    CUSTOM = "custom"      # Custom Anthropic-compatible endpoint


class APIStatus(str, Enum):
    """API health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"


class APICompatibility:
    """API compatibility checker and health monitor"""

    @staticmethod
    def detect_provider() -> APIProvider:
        """
        Detect which API provider is configured

        Returns:
            APIProvider enum value
        """
        provider = settings.DEFAULT_LLM_PROVIDER.lower()

        # Check for Anthropic variants
        if provider == "anthropic":
            if settings.ANTHROPIC_BASE_URL:
                # Third-party or custom endpoint
                if "bigmodel" in settings.ANTHROPIC_BASE_URL.lower():
                    return APIProvider.BIGMODEL
                else:
                    return APIProvider.CUSTOM
            else:
                return APIProvider.ANTHROPIC

        # OpenAI
        elif provider == "openai":
            return APIProvider.OPENAI

        # Default to configured value
        return APIProvider.CUSTOM

    @staticmethod
    def validate_api_configuration() -> Tuple[bool, str]:
        """
        Validate API configuration for the current provider

        Returns:
            Tuple of (is_valid, error_message)
        """
        provider = settings.DEFAULT_LLM_PROVIDER.lower()

        # Validate Anthropic configuration
        if provider == "anthropic":
            # Check for API key or token
            has_key = bool(settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_AUTH_TOKEN)
            if not has_key:
                return False, "Anthropic API key or auth token not configured"

            # If using custom base URL, validate format
            if settings.ANTHROPIC_BASE_URL:
                if not settings.ANTHROPIC_BASE_URL.startswith("http"):
                    return False, f"Invalid ANTHROPIC_BASE_URL format: {settings.ANTHROPIC_BASE_URL}"

            # Validate model name
            valid_anthropic_models = [
                "claude-sonnet-4",
                "claude-opus-4",
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229"
            ]
            if settings.DEFAULT_MODEL not in valid_anthropic_models:
                logger.warning(f"Model '{settings.DEFAULT_MODEL}' may not be a valid Anthropic model")

            return True, "Anthropic configuration valid"

        # Validate OpenAI configuration
        elif provider == "openai":
            if not settings.OPENAI_API_KEY:
                return False, "OpenAI API key not configured"

            # Validate model name
            valid_openai_models = [
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ]
            if not any(settings.DEFAULT_MODEL.startswith(m) for m in valid_openai_models):
                logger.warning(f"Model '{settings.DEFAULT_MODEL}' may not be a valid OpenAI model")

            return True, "OpenAI configuration valid"

        else:
            return False, f"Unsupported LLM provider: {provider}"

    @staticmethod
    async def check_api_health(provider: Optional[str] = None) -> Dict:
        """
        Check API health status

        Args:
            provider: Provider to check (defaults to configured provider)

        Returns:
            Dict with health status information
        """
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        detected_provider = APICompatibility.detect_provider()

        result = {
            "provider": provider,
            "detected_provider": detected_provider.value,
            "status": APIStatus.NOT_CONFIGURED,
            "model": settings.DEFAULT_MODEL,
            "message": "",
            "configuration": {
                "temperature": settings.LLM_TEMPERATURE,
                "max_tokens": settings.LLM_MAX_TOKENS,
                "timeout": settings.LLM_TIMEOUT
            }
        }

        # Validate configuration
        is_valid, message = APICompatibility.validate_api_configuration()
        result["message"] = message

        if not is_valid:
            result["status"] = APIStatus.NOT_CONFIGURED
            return result

        # Try to check API accessibility (basic check)
        try:
            if provider.lower() == "anthropic":
                # Check if we can import and initialize
                from anthropic import Anthropic

                api_key = settings.ANTHROPIC_AUTH_TOKEN or settings.ANTHROPIC_API_KEY
                client_kwargs = {"api_key": api_key}
                if settings.ANTHROPIC_BASE_URL:
                    client_kwargs["base_url"] = settings.ANTHROPIC_BASE_URL

                # Just try to create client (doesn't make API call)
                Anthropic(**client_kwargs)
                result["status"] = APIStatus.HEALTHY
                result["message"] = "Anthropic API configured and client initialized"

                if settings.ANTHROPIC_BASE_URL:
                    result["base_url"] = settings.ANTHROPIC_BASE_URL
                    result["message"] += f" (using custom endpoint: {settings.ANTHROPIC_BASE_URL})"

            elif provider.lower() == "openai":
                # Check if we can import and initialize
                from openai import OpenAI

                OpenAI(api_key=settings.OPENAI_API_KEY)
                result["status"] = APIStatus.HEALTHY
                result["message"] = "OpenAI API configured and client initialized"

        except ImportError as e:
            result["status"] = APIStatus.UNAVAILABLE
            result["message"] = f"Required library not installed: {str(e)}"
            logger.error(f"API library import failed: {e}")

        except Exception as e:
            result["status"] = APIStatus.DEGRADED
            result["message"] = f"Configuration issue: {str(e)}"
            logger.error(f"API health check failed: {e}")

        return result

    @staticmethod
    def get_provider_info(provider: Optional[str] = None) -> Dict:
        """
        Get detailed information about a provider

        Args:
            provider: Provider name (defaults to configured provider)

        Returns:
            Dict with provider information
        """
        provider = provider or settings.DEFAULT_LLM_PROVIDER
        detected = APICompatibility.detect_provider()

        info = {
            "provider": provider,
            "detected_type": detected.value,
            "supports": []
        }

        if provider.lower() == "anthropic":
            info.update({
                "name": "Anthropic Claude",
                "description": "Advanced AI assistant with strong reasoning capabilities",
                "max_context": "200K tokens",
                "supports": [
                    "long_context",
                    "function_calling",
                    "system_prompts",
                    "streaming"
                ],
                "models": [
                    "claude-sonnet-4 (recommended)",
                    "claude-opus-4 (most capable)",
                    "claude-3-5-sonnet-20241022 (legacy)"
                ]
            })

            if detected == APIProvider.BIGMODEL:
                info["using_third_party"] = True
                info["third_party_name"] = "BigModel (智谱AI)"
                info["endpoint"] = settings.ANTHROPIC_BASE_URL

            elif detected == APIProvider.CUSTOM:
                info["using_third_party"] = True
                info["third_party_name"] = "Custom Endpoint"
                info["endpoint"] = settings.ANTHROPIC_BASE_URL

        elif provider.lower() == "openai":
            info.update({
                "name": "OpenAI GPT",
                "description": "Powerful language models from OpenAI",
                "max_context": "128K tokens",
                "supports": [
                    "function_calling",
                    "json_mode",
                    "vision (gpt-4o)",
                    "streaming"
                ],
                "models": [
                    "gpt-4o (recommended)",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo (economical)"
                ]
            })

        return info

    @staticmethod
    def compare_providers() -> Dict:
        """
        Compare different API providers

        Returns:
            Dict with provider comparison
        """
        return {
            "anthropic": {
                "strengths": [
                    "Longer context window (200K vs 128K)",
                    "Better reasoning capabilities",
                    "Strong safety features",
                    "Better Chinese language support"
                ],
                "use_cases": [
                    "Complex analysis tasks",
                    "Long document processing",
                    "Chinese language applications",
                    "Interview question generation (our use case)"
                ],
                "cost": "$$"
            },
            "openai": {
                "strengths": [
                    "Mature ecosystem",
                    "Wide tool support",
                    "Vision capabilities (GPT-4o)",
                    "Fast response times"
                ],
                "use_cases": [
                    "Standard text generation",
                    "Multi-modal applications",
                    "Integration with OpenAI tools",
                    "Cost-sensitive applications (GPT-3.5)"
                ],
                "cost": "$-$$$"
            },
            "recommendation": {
                "for_grillradar": "anthropic",
                "reason": "Better at complex reasoning and analysis required for generating insightful interview questions"
            }
        }


class APIAdapter:
    """
    Adapter pattern for different API providers
    Ensures consistent interface across providers
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize adapter for specific provider

        Args:
            provider: Provider name (defaults to configured provider)
        """
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.detected_provider = APICompatibility.detect_provider()

    def get_client_kwargs(self) -> Dict:
        """
        Get provider-specific client initialization arguments

        Returns:
            Dict of kwargs for client initialization
        """
        if self.provider.lower() == "anthropic":
            api_key = settings.ANTHROPIC_AUTH_TOKEN or settings.ANTHROPIC_API_KEY
            kwargs = {"api_key": api_key}

            if settings.ANTHROPIC_BASE_URL:
                kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
                logger.info(f"Using custom Anthropic endpoint: {settings.ANTHROPIC_BASE_URL}")

            return kwargs

        elif self.provider.lower() == "openai":
            return {"api_key": settings.OPENAI_API_KEY}

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def validate_model_name(self, model: str) -> bool:
        """
        Validate if model name is compatible with provider

        Args:
            model: Model name to validate

        Returns:
            True if valid, False otherwise
        """
        if self.provider.lower() == "anthropic":
            return model.startswith("claude")

        elif self.provider.lower() == "openai":
            return model.startswith("gpt")

        return False

    def get_default_parameters(self) -> Dict:
        """
        Get provider-specific default parameters

        Returns:
            Dict of default parameters
        """
        base_params = {
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS
        }

        if self.provider.lower() == "anthropic":
            # Anthropic-specific parameters
            base_params["model"] = settings.DEFAULT_MODEL

        elif self.provider.lower() == "openai":
            # OpenAI-specific parameters
            base_params["model"] = settings.DEFAULT_MODEL

        return base_params


# Singleton instance for global access
api_compatibility = APICompatibility()
