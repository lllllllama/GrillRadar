"""Custom exceptions for GrillRadar"""


class GrillRadarError(Exception):
    """Base exception for all GrillRadar errors"""
    pass


class ConfigurationError(GrillRadarError):
    """Raised when configuration files are invalid"""

    def __init__(self, message: str, config_file: str = None, field: str = None):
        self.config_file = config_file
        self.field = field

        error_msg = "Configuration error"
        if config_file:
            error_msg += f" in {config_file}"
        if field:
            error_msg += f" (field: {field})"
        error_msg += f": {message}"

        super().__init__(error_msg)


class LLMError(GrillRadarError):
    """Raised when LLM API calls fail"""

    def __init__(self, provider: str, message: str, original_error: Exception = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"LLM error ({provider}): {message}")


class ValidationError(GrillRadarError):
    """Raised when input validation fails"""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class ExternalDataError(GrillRadarError):
    """Raised when external data retrieval fails"""
    pass
