"""Tests for custom exceptions"""

import pytest
from app.exceptions import (
    GrillRadarError,
    ConfigurationError,
    LLMError,
    ValidationError,
    ExternalDataError
)


class TestExceptions:
    def test_grillradar_error_base(self):
        """Test base GrillRadarError"""
        error = GrillRadarError("Test error")

        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_configuration_error_basic(self):
        """Test ConfigurationError with basic message"""
        error = ConfigurationError("Invalid configuration")

        assert "Configuration error" in str(error)
        assert "Invalid configuration" in str(error)
        assert isinstance(error, GrillRadarError)

    def test_configuration_error_with_file(self):
        """Test ConfigurationError with config file"""
        error = ConfigurationError(
            "Missing field",
            config_file="domains.yaml"
        )

        error_msg = str(error)
        assert "Configuration error" in error_msg
        assert "domains.yaml" in error_msg
        assert "Missing field" in error_msg

    def test_configuration_error_with_field(self):
        """Test ConfigurationError with field"""
        error = ConfigurationError(
            "Invalid type",
            config_file="modes.yaml",
            field="job.roles"
        )

        error_msg = str(error)
        assert "modes.yaml" in error_msg
        assert "job.roles" in error_msg
        assert "Invalid type" in error_msg

    def test_configuration_error_attributes(self):
        """Test ConfigurationError attributes are set"""
        error = ConfigurationError(
            "Test",
            config_file="test.yaml",
            field="test.field"
        )

        assert error.config_file == "test.yaml"
        assert error.field == "test.field"

    def test_llm_error_basic(self):
        """Test LLMError with provider"""
        error = LLMError("anthropic", "API call failed")

        error_msg = str(error)
        assert "LLM error" in error_msg
        assert "anthropic" in error_msg
        assert "API call failed" in error_msg

    def test_llm_error_with_original(self):
        """Test LLMError with original exception"""
        original = ValueError("Network timeout")
        error = LLMError("openai", "Request failed", original_error=original)

        assert error.provider == "openai"
        assert error.original_error is original
        assert isinstance(error, GrillRadarError)

    def test_validation_error_basic(self):
        """Test ValidationError"""
        error = ValidationError("resume_text", "Text too short")

        error_msg = str(error)
        assert "Validation error" in error_msg
        assert "resume_text" in error_msg
        assert "Text too short" in error_msg

    def test_validation_error_attributes(self):
        """Test ValidationError attributes"""
        error = ValidationError("mode", "Invalid mode value")

        assert error.field == "mode"
        assert isinstance(error, GrillRadarError)

    def test_external_data_error(self):
        """Test ExternalDataError"""
        error = ExternalDataError("Failed to fetch JD data")

        assert "Failed to fetch JD data" in str(error)
        assert isinstance(error, GrillRadarError)

    def test_exception_hierarchy(self):
        """Test that all custom exceptions inherit from GrillRadarError"""
        errors = [
            ConfigurationError("test"),
            LLMError("test", "test"),
            ValidationError("test", "test"),
            ExternalDataError("test")
        ]

        for error in errors:
            assert isinstance(error, GrillRadarError)
            assert isinstance(error, Exception)

    def test_exception_catching(self):
        """Test that exceptions can be caught at different levels"""

        # Can catch specific exception
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("test")

        # Can catch as GrillRadarError
        with pytest.raises(GrillRadarError):
            raise ConfigurationError("test")

        # Can catch as Exception
        with pytest.raises(Exception):
            raise ConfigurationError("test")
