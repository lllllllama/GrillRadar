"""
JSON Sanitizer - Repair Malformed JSON from LLM Outputs

This module provides utilities to detect and repair malformed JSON that LLMs
sometimes generate. When direct JSON parsing fails, we can use an LLM to fix
the JSON structure before parsing.

Design Philosophy:
- First, try basic cleanup (remove markdown, fix common issues)
- If that fails, optionally use LLM to repair
- Always log failures for debugging
- Provide graceful degradation options

Usage:
    from app.utils.json_sanitizer import repair_json, safe_json_parse

    # Basic usage
    data = safe_json_parse(raw_llm_output, request_id="abc-123")

    # With LLM repair enabled
    data = safe_json_parse(
        raw_llm_output,
        request_id="abc-123",
        enable_llm_repair=True,
        llm_client=my_llm_client
    )
"""
import json
import logging
import re
from typing import Optional, Dict, Any, Callable

from app.core.logging import get_logger

logger = get_logger(__name__)


class JSONRepairError(Exception):
    """Raised when JSON repair fails"""
    pass


def clean_json_text(raw_text: str) -> str:
    """
    Apply basic cleanup to raw text before JSON parsing.

    This handles common issues:
    - Markdown code blocks (```json, ```)
    - Extra whitespace
    - Trailing commas in objects/arrays
    - Single quotes instead of double quotes
    - Comments (// and /* */)

    Args:
        raw_text: Raw text from LLM

    Returns:
        Cleaned text ready for JSON parsing
    """
    text = raw_text.strip()

    # Remove markdown code blocks
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Remove comments (simple regex, not perfect but handles common cases)
    # Remove single-line comments
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    # Remove multi-line comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

    # Fix trailing commas (simple approach - works for most cases)
    # Trailing comma before closing brace
    text = re.sub(r',(\s*})', r'\1', text)
    # Trailing comma before closing bracket
    text = re.sub(r',(\s*\])', r'\1', text)

    # Replace single quotes with double quotes (risky but often needed)
    # Only do this if the text doesn't contain valid double quotes already
    if '"' not in text and "'" in text:
        text = text.replace("'", '"')

    return text.strip()


def basic_repair_json(raw_text: str) -> str:
    """
    Attempt basic JSON repair without using LLM.

    Args:
        raw_text: Raw text that failed JSON parsing

    Returns:
        Repaired JSON text

    Raises:
        JSONRepairError: If basic repair fails
    """
    # Apply basic cleanup
    cleaned = clean_json_text(raw_text)

    # Try to parse
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError as e:
        # Basic repair failed
        raise JSONRepairError(f"Basic repair failed: {str(e)}")


def llm_repair_json(
    raw_text: str,
    llm_client: Any,
    request_id: Optional[str] = None
) -> str:
    """
    Use an LLM to repair malformed JSON.

    This is a last resort when basic cleanup fails. We ask the LLM to fix
    the JSON structure.

    Args:
        raw_text: Malformed JSON text
        llm_client: LLM client instance (must have .call() method)
        request_id: Request ID for logging

    Returns:
        Repaired JSON text

    Raises:
        JSONRepairError: If LLM repair fails
    """
    extra = {'request_id': request_id} if request_id else {}
    logger.warning("Attempting LLM-based JSON repair", extra=extra)

    # Construct repair prompt
    repair_prompt = f"""You are a JSON repair assistant. Your task is to fix malformed JSON and output ONLY valid JSON.

Input (malformed JSON):
{raw_text[:2000]}

Instructions:
1. Fix any syntax errors (missing brackets, trailing commas, etc.)
2. Ensure all strings use double quotes
3. Remove any comments
4. Output ONLY the corrected JSON, no explanations

Output:"""

    try:
        # Call LLM to repair
        repaired_text = llm_client.call(
            system_prompt="You are a JSON repair assistant. Output only valid JSON, no explanations.",
            user_message=repair_prompt
        )

        # Clean the LLM response
        repaired_text = clean_json_text(repaired_text)

        # Validate it's valid JSON
        json.loads(repaired_text)

        logger.info("LLM successfully repaired JSON", extra=extra)
        return repaired_text

    except json.JSONDecodeError as e:
        logger.error(f"LLM repair produced invalid JSON: {str(e)}", extra=extra)
        raise JSONRepairError(f"LLM repair failed: {str(e)}")
    except Exception as e:
        logger.error(f"LLM repair error: {str(e)}", extra=extra)
        raise JSONRepairError(f"LLM repair error: {str(e)}")


def repair_json(
    raw_text: str,
    enable_llm_repair: bool = False,
    llm_client: Optional[Any] = None,
    request_id: Optional[str] = None
) -> str:
    """
    Repair malformed JSON text.

    This function tries:
    1. Basic cleanup (markdown removal, trailing commas, etc.)
    2. LLM-based repair (if enabled and basic cleanup fails)

    Args:
        raw_text: Raw text from LLM
        enable_llm_repair: Whether to use LLM for repair if basic cleanup fails
        llm_client: LLM client instance (required if enable_llm_repair=True)
        request_id: Request ID for logging

    Returns:
        Repaired JSON text

    Raises:
        JSONRepairError: If all repair attempts fail
    """
    extra = {'request_id': request_id} if request_id else {}

    # Try basic repair first
    try:
        return basic_repair_json(raw_text)
    except JSONRepairError as e:
        logger.debug(f"Basic JSON repair failed: {str(e)}", extra=extra)

        # Try LLM repair if enabled
        if enable_llm_repair:
            if not llm_client:
                raise JSONRepairError("LLM repair enabled but no llm_client provided")
            return llm_repair_json(raw_text, llm_client, request_id)
        else:
            raise


def safe_json_parse(
    raw_text: str,
    request_id: Optional[str] = None,
    enable_llm_repair: bool = False,
    llm_client: Optional[Any] = None,
    fallback_value: Optional[Any] = None,
    on_error: Optional[Callable[[str, Exception], None]] = None
) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON with automatic repair and graceful degradation.

    This is the main entry point for robust JSON parsing in GrillRadar.

    Args:
        raw_text: Raw text from LLM
        request_id: Request ID for logging
        enable_llm_repair: Whether to use LLM for repair if basic cleanup fails
        llm_client: LLM client instance (required if enable_llm_repair=True)
        fallback_value: Value to return if parsing fails (default: None)
        on_error: Optional callback called on error: on_error(raw_text, exception)

    Returns:
        Parsed JSON dict, or fallback_value if parsing fails

    Example:
        >>> data = safe_json_parse(
        ...     raw_llm_output,
        ...     request_id="abc-123",
        ...     enable_llm_repair=True,
        ...     llm_client=client,
        ...     fallback_value={}
        ... )
    """
    extra = {'request_id': request_id} if request_id else {}

    # First attempt: direct parsing
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        logger.debug("Direct JSON parsing failed, attempting repair", extra=extra)

    # Second attempt: repair and parse
    try:
        repaired_text = repair_json(
            raw_text,
            enable_llm_repair=enable_llm_repair,
            llm_client=llm_client,
            request_id=request_id
        )
        return json.loads(repaired_text)
    except (JSONRepairError, json.JSONDecodeError) as e:
        logger.error(
            f"JSON parsing failed after repair attempts: {str(e)}",
            extra=extra
        )

        # Log first 500 chars of malformed JSON for debugging
        logger.debug(f"Malformed JSON: {raw_text[:500]}", extra=extra)

        # Call error callback if provided
        if on_error:
            try:
                on_error(raw_text, e)
            except Exception as callback_error:
                logger.error(f"Error callback failed: {callback_error}", extra=extra)

        # Return fallback value
        return fallback_value


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that may contain surrounding explanations.

    Useful when LLM includes JSON in a larger response.

    Args:
        text: Text that contains JSON somewhere

    Returns:
        Extracted JSON text, or None if not found

    Example:
        >>> text = "Here's the JSON:\\n{\"key\": \"value\"}\\nHope this helps!"
        >>> json_text = extract_json_from_text(text)
        >>> data = json.loads(json_text)
    """
    text = text.strip()

    # Look for JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)

    # Look for JSON array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return match.group(0)

    return None


def is_valid_json(text: str) -> bool:
    """
    Check if text is valid JSON.

    Args:
        text: Text to validate

    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, TypeError):
        return False
