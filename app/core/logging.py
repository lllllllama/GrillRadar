"""
Unified Logging Configuration for GrillRadar

This module provides a centralized logging setup with:
- Request ID tracking across the entire pipeline
- Structured logging with context (mode, domain, model, etc.)
- Execution time tracking for major stages
- Token usage tracking (when available)
- Debug mode support via environment variable

Usage:
    from app.core.logging import get_logger, log_stage_timing

    logger = get_logger(__name__)
    with log_stage_timing(logger, "parsing", request_id="abc-123"):
        # ... do work
        pass
"""
import logging
import os
import sys
import time
import uuid
from contextlib import contextmanager
from typing import Optional, Dict, Any
from pathlib import Path


# Global log level - can be overridden by GRILLRADAR_DEBUG env var
DEFAULT_LOG_LEVEL = logging.INFO
DEBUG_ENV_VAR = "GRILLRADAR_DEBUG"


class RequestContextFilter(logging.Filter):
    """
    Logging filter that adds request_id and other context to log records.

    This allows us to trace a single request across multiple components.
    """

    def __init__(self):
        super().__init__()
        self.context = {}

    def filter(self, record):
        # Add context fields to log record
        for key, value in self.context.items():
            setattr(record, key, value)

        # Ensure request_id exists (fallback to empty string)
        if not hasattr(record, 'request_id'):
            record.request_id = ''

        return True

    def set_context(self, **kwargs):
        """Update logging context with key-value pairs"""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all context"""
        self.context.clear()


# Global context filter instance
_context_filter = RequestContextFilter()


def configure_logging(
    log_level: Optional[int] = None,
    log_file: Optional[str] = None,
    enable_debug: Optional[bool] = None
):
    """
    Configure the global logging setup for GrillRadar.

    Args:
        log_level: Logging level (default: INFO, or DEBUG if GRILLRADAR_DEBUG=1)
        log_file: Optional log file path (default: logs to console only)
        enable_debug: Force debug mode (default: read from GRILLRADAR_DEBUG env)

    Environment Variables:
        GRILLRADAR_DEBUG: Set to "1" or "true" to enable debug logging
    """
    # Determine log level
    if enable_debug is None:
        enable_debug = os.getenv(DEBUG_ENV_VAR, "").lower() in ("1", "true", "yes")

    if log_level is None:
        log_level = logging.DEBUG if enable_debug else DEFAULT_LOG_LEVEL

    # Create formatter
    if enable_debug:
        # More verbose format for debug mode
        log_format = (
            '%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(message)s'
        )
    else:
        # Concise format for production
        log_format = '%(asctime)s - [%(request_id)s] - %(levelname)s - %(message)s'

    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(_context_filter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_context_filter)
        root_logger.addHandler(file_handler)

    # Suppress verbose third-party loggers
    logging.getLogger('anthropic').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting process", extra={'request_id': 'abc-123'})
    """
    return logging.getLogger(name)


def generate_request_id() -> str:
    """
    Generate a unique request ID for tracing.

    Returns:
        UUID-based request ID (e.g., "req_a1b2c3d4")
    """
    return f"req_{uuid.uuid4().hex[:12]}"


def set_request_context(
    request_id: str,
    mode: Optional[str] = None,
    domain: Optional[str] = None,
    target_desc: Optional[str] = None,
    llm_model: Optional[str] = None,
    **kwargs
):
    """
    Set request context for logging.

    This context will be automatically added to all log messages.

    Args:
        request_id: Unique request identifier
        mode: User config mode (job/grad/mixed)
        domain: User config domain
        target_desc: Target description (will be truncated in logs)
        llm_model: LLM model being used
        **kwargs: Additional context fields
    """
    context = {
        'request_id': request_id,
    }

    if mode:
        context['mode'] = mode
    if domain:
        context['domain'] = domain
    if target_desc:
        # Truncate target_desc for log readability
        context['target_desc'] = target_desc[:30] + '...' if len(target_desc) > 30 else target_desc
    if llm_model:
        context['llm_model'] = llm_model

    context.update(kwargs)
    _context_filter.set_context(**context)


def clear_request_context():
    """Clear request context (call at end of request)"""
    _context_filter.clear_context()


@contextmanager
def log_stage_timing(
    logger: logging.Logger,
    stage_name: str,
    request_id: Optional[str] = None,
    **metadata
):
    """
    Context manager for timing and logging pipeline stages.

    Args:
        logger: Logger instance
        stage_name: Name of the stage being timed
        request_id: Request ID (optional, will use context if not provided)
        **metadata: Additional metadata to log

    Example:
        >>> with log_stage_timing(logger, "resume_parsing", request_id="abc-123"):
        ...     text = parse_resume("resume.pdf")

    Yields:
        Dict with timing information (can be used to add metrics)
    """
    start_time = time.time()
    timing_info = {'stage': stage_name, 'start_time': start_time}

    extra = {}
    if request_id:
        extra['request_id'] = request_id

    logger.info(f"Starting stage: {stage_name}", extra=extra)

    try:
        yield timing_info
        elapsed = time.time() - start_time
        timing_info['elapsed'] = elapsed
        logger.info(
            f"Completed stage: {stage_name} (took {elapsed:.2f}s)",
            extra={**extra, **metadata}
        )
    except Exception as e:
        elapsed = time.time() - start_time
        timing_info['elapsed'] = elapsed
        timing_info['error'] = str(e)
        logger.error(
            f"Failed stage: {stage_name} after {elapsed:.2f}s - {str(e)}",
            extra=extra,
            exc_info=True
        )
        raise


def log_llm_call(
    logger: logging.Logger,
    request_id: str,
    provider: str,
    model: str,
    prompt_length: int,
    response_length: Optional[int] = None,
    tokens_used: Optional[Dict[str, int]] = None,
    elapsed_time: Optional[float] = None
):
    """
    Log an LLM API call with metrics.

    Args:
        logger: Logger instance
        request_id: Request ID
        provider: LLM provider (anthropic/openai)
        model: Model name
        prompt_length: Length of prompt in characters
        response_length: Length of response in characters
        tokens_used: Dict with 'prompt_tokens' and 'completion_tokens'
        elapsed_time: Time taken for the call in seconds
    """
    metrics = {
        'provider': provider,
        'model': model,
        'prompt_chars': prompt_length,
    }

    if response_length:
        metrics['response_chars'] = response_length
    if tokens_used:
        metrics['prompt_tokens'] = tokens_used.get('prompt_tokens', 0)
        metrics['completion_tokens'] = tokens_used.get('completion_tokens', 0)
        metrics['total_tokens'] = metrics['prompt_tokens'] + metrics['completion_tokens']
    if elapsed_time:
        metrics['elapsed_time'] = f"{elapsed_time:.2f}s"

    logger.info(
        f"LLM call: {provider}/{model}",
        extra={'request_id': request_id, **metrics}
    )


# Initialize logging on module import (with defaults)
# This ensures logging works even if configure_logging() isn't called explicitly
configure_logging()
