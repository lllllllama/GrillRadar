# GrillRadar Developer Guide

This guide covers internal architecture, debugging, logging, and development best practices for GrillRadar.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Debug & Logs](#debug--logs)
- [JSON Repair System](#json-repair-system)
- [Error Handling & Graceful Degradation](#error-handling--graceful-degradation)
- [Testing](#testing)
- [Contributing](#contributing)

---

## Architecture Overview

GrillRadar follows a clean, layered architecture:

```
┌─────────────────────────────────────────┐
│   CLI (cli.py) / API (app/api/)        │
│   - User interface layer                │
│   - Generates request_id for tracing   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   GrillRadarPipeline (app/core/)       │
│   - Central orchestration               │
│   - Resume parsing                      │
│   - Mode selection (single/multi-agent) │
│   - Request ID propagation              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   ReportGenerator / AgentOrchestrator   │
│   - Prompt building                     │
│   - LLM calls                           │
│   - Report assembly                     │
│   - Graceful degradation                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   LLMClient (app/core/llm_client.py)   │
│   - API calls (Anthropic/OpenAI)        │
│   - JSON parsing with auto-repair       │
│   - Token usage logging                 │
└─────────────────────────────────────────┘
```

### Key Components

1. **Pipeline** (`app/core/pipeline.py`): Orchestrates the entire flow
2. **LLMClient** (`app/core/llm_client.py`): Handles all LLM API calls with robust error handling
3. **ReportGenerator** (`app/core/report_generator.py`): Single-agent report generation
4. **AgentOrchestrator** (`app/core/agent_orchestrator.py`): Multi-agent debate system
5. **Logging** (`app/core/logging.py`): Centralized logging with request tracing
6. **JSONSanitizer** (`app/utils/json_sanitizer.py`): Repairs malformed JSON from LLMs

---

## Debug & Logs

### Enabling Debug Mode

GrillRadar supports debug logging via environment variable:

```bash
# Enable debug logging
export GRILLRADAR_DEBUG=1

# Run CLI with debug logs
python cli.py --config config.json --resume resume.pdf
```

**What debug mode does:**
- Enables `DEBUG` level logging (shows all internal operations)
- Includes file names and line numbers in logs
- Shows detailed LLM call metrics (tokens, timing)
- Logs JSON parsing attempts and repairs

### Log Format

**Production (INFO level):**
```
2025-01-15 10:30:45 - [req_a1b2c3d4] - INFO - Pipeline started - mode=job
```

**Debug (DEBUG level):**
```
2025-01-15 10:30:45 - [req_a1b2c3d4] - app.core.pipeline - DEBUG - pipeline.py:95 - Parsing resume with OCR
```

### Request ID Tracing

Every request (CLI or API) gets a unique `request_id` like `req_a1b2c3d4`. This ID appears in **all** log messages for that request.

**How to trace a specific request:**

1. Find the request ID from the initial log message:
   ```
   2025-01-15 10:30:45 - INFO - 生成请求ID: req_a1b2c3d4
   ```

2. Filter logs by request ID:
   ```bash
   # If logging to console
   python cli.py ... 2>&1 | grep "req_a1b2c3d4"

   # If logging to file
   grep "req_a1b2c3d4" grillradar.log
   ```

3. You'll see the entire flow for that request:
   ```
   [req_a1b2c3d4] - Starting stage: resume_parsing
   [req_a1b2c3d4] - Completed stage: resume_parsing (took 1.23s)
   [req_a1b2c3d4] - LLM call: anthropic/claude-3-5-sonnet-20241022
   [req_a1b2c3d4] - Starting stage: report_generation
   [req_a1b2c3d4] - Completed stage: report_generation (took 12.45s)
   ```

### Log Files

By default, GrillRadar logs to **console only**. To log to a file:

```python
from app.core.logging import configure_logging

# Configure with file output
configure_logging(log_file="grillradar.log")
```

Or set environment variable:
```bash
export GRILLRADAR_LOG_FILE=grillradar.log
```

### Understanding Log Messages

**Stage Timing:**
```
INFO - Starting stage: resume_parsing
INFO - Completed stage: resume_parsing (took 1.23s)
```
- Tracks execution time for major pipeline stages
- Stages: `resume_parsing`, `report_generation`, `external_info_fetch`, `agent_debate`, `forum_selection`

**LLM Call Metrics:**
```
INFO - LLM call: anthropic/claude-3-5-sonnet-20241022
  {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-20241022',
   'prompt_tokens': 1234, 'completion_tokens': 567, 'total_tokens': 1801,
   'elapsed_time': '3.45s'}
```
- Shows token usage and API call duration
- Useful for cost estimation and performance analysis

**JSON Repair:**
```
WARNING - Attempting LLM-based JSON repair
INFO - LLM successfully repaired JSON
```
- Indicates JSON parsing initially failed
- Shows whether repair succeeded

**Graceful Degradation:**
```
WARNING - Creating simplified report from partial data
```
- LLM output was malformed but we salvaged some data
- Report may be incomplete but won't crash

---

## JSON Repair System

GrillRadar includes a sophisticated JSON repair system to handle malformed LLM outputs.

### How It Works

1. **Direct Parse Attempt:** Try `json.loads()` directly
2. **Basic Cleanup:** Remove markdown code blocks, fix trailing commas
3. **LLM Repair (optional):** Ask LLM to fix the JSON structure
4. **Graceful Degradation:** Return simplified report if all else fails

### Basic Cleanup

The `clean_json_text()` function handles:
- Markdown code blocks (`\`\`\`json`, `\`\`\``)
- Trailing commas (`{"key": "value",}` → `{"key": "value"}`)
- Single quotes (`{'key': 'value'}` → `{"key": "value"}`)
- Comments (`// comment`, `/* comment */`)

### LLM-Based Repair

If basic cleanup fails, we can ask the same LLM to fix the JSON:

```python
from app.core.llm_client import LLMClient

# Enable JSON repair (default: True)
client = LLMClient(enable_json_repair=True)

# This will auto-repair if needed
data = client.call_json(prompt)
```

**When to disable repair:**
- You want strict JSON validation (fail fast)
- Cost optimization (LLM repair adds an extra API call)
- Testing/debugging (want to see raw failures)

```python
# Disable JSON repair
client = LLMClient(enable_json_repair=False)
```

### Manual JSON Repair

You can also use the JSON sanitizer directly:

```python
from app.utils.json_sanitizer import repair_json, safe_json_parse

# Basic repair (no LLM)
try:
    cleaned = repair_json(raw_text, enable_llm_repair=False)
    data = json.loads(cleaned)
except JSONRepairError:
    # Handle failure
    pass

# With LLM repair
from app.core.llm_client import LLMClient
client = LLMClient()

data = safe_json_parse(
    raw_text,
    enable_llm_repair=True,
    llm_client=client,
    request_id="req_abc123",
    fallback_value={}  # Return this if all fails
)
```

---

## Error Handling & Graceful Degradation

GrillRadar is designed to **never crash silently**. All failures are logged, but we try to provide partial results when possible.

### Degradation Levels

1. **Full Success:** Report generated normally
2. **Simplified Report:** LLM output was malformed, but we extracted valid questions
3. **Fallback Report:** LLM call failed completely, return error message as "question"

### Example: Simplified Report

If LLM returns malformed JSON but we can extract some questions:

```python
# Input: Partial/malformed LLM output
{
  "questions": [
    {"question": "Valid question 1", "role": "Interviewer"},
    {"malformed": true},  # This will be skipped
    {"question": "Valid question 2", "role": "HR"}
  ]
  # Missing summary, meta, etc.
}

# Output: Simplified Report
- summary: "⚠️ 简化报告\n\n由于数据验证失败，此报告仅包含部分信息。"
- questions: [Question 1, Question 2]  # Only valid questions
- meta: Partial metadata extracted from available data
```

### Example: Fallback Report

If LLM call fails completely (network error, API error):

```python
# Output: Fallback Report
{
  "questions": [{
    "id": 1,
    "question": "⚠️ 报告生成失败",
    "rationale": "LLM调用失败: Connection timeout",
    "role": "系统",
    "baseline_answer": "请检查API配置和网络连接，然后重试。"
  }]
}
```

### Checking for Degraded Reports

```python
from app.core.pipeline import GrillRadarPipeline

pipeline = GrillRadarPipeline(request_id="req_abc123")
report = pipeline.run(resume_path="resume.pdf", user_config=config)

# Check if degraded
if "⚠️" in report.summary:
    print("Warning: This is a degraded report")
    # Check logs for details
    # grep "req_abc123" logs
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_pipeline.py

# Run with debug logging
GRILLRADAR_DEBUG=1 pytest tests/test_llm_client.py -v
```

### Testing with Request IDs

```python
from app.core.logging import generate_request_id
from app.core.pipeline import GrillRadarPipeline

def test_pipeline_with_tracing():
    request_id = generate_request_id()
    pipeline = GrillRadarPipeline(request_id=request_id)

    # All logs will include this request_id
    report = pipeline.run(...)

    # Can trace this specific test run in logs
    assert report is not None
```

### Mock LLM Calls

```python
from unittest.mock import Mock, patch

@patch('app.core.llm_client.LLMClient.call_json')
def test_report_generation(mock_call_json):
    mock_call_json.return_value = {
        "mode": "job",
        "questions": [...]
    }

    # Test code
    ...
```

---

## Contributing

### Code Style

- Follow PEP 8
- Use type hints for function signatures
- Add docstrings for public functions
- Keep functions focused (Single Responsibility Principle)

### Logging Best Practices

**DO:**
```python
from app.core.logging import get_logger

logger = get_logger(__name__)

def process_data(data, request_id):
    logger.info(f"Processing {len(data)} items", extra={'request_id': request_id})
    # ... work
    logger.info(f"Completed processing", extra={'request_id': request_id})
```

**DON'T:**
```python
# Don't use print()
print("Processing data...")  # ❌

# Don't use basic logging without request_id
logging.info("Processing data")  # ❌

# Don't log sensitive data
logger.info(f"API key: {api_key}")  # ❌
```

### Adding New Features

1. **Start with logging:** Add appropriate log messages for traceability
2. **Handle errors gracefully:** Use try-except with fallbacks
3. **Propagate request_id:** Pass it through all function calls
4. **Test with debug mode:** Run with `GRILLRADAR_DEBUG=1` to verify logs
5. **Document behavior:** Update this guide if behavior changes

### Debugging Checklist

When investigating a bug:

1. ✅ Get the `request_id` from the user
2. ✅ Search logs for that `request_id`
3. ✅ Check stage timings (identify slow stages)
4. ✅ Check LLM call metrics (token usage, errors)
5. ✅ Check for JSON repair warnings
6. ✅ Check for graceful degradation warnings
7. ✅ Enable `GRILLRADAR_DEBUG=1` and reproduce
8. ✅ Check exception stack traces

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GRILLRADAR_DEBUG` | `0` | Enable debug logging (`1` or `true`) |
| `GRILLRADAR_LOG_FILE` | None | Path to log file (optional) |
| `ANTHROPIC_API_KEY` | Required | Anthropic API key |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `DEFAULT_LLM_PROVIDER` | `anthropic` | LLM provider to use |
| `DEFAULT_MODEL` | `claude-3-5-sonnet-20241022` | Default LLM model |

---

## Troubleshooting

### Issue: Logs are too verbose

**Solution:** Don't enable `GRILLRADAR_DEBUG` in production. Use INFO level.

### Issue: Can't trace a specific request

**Solution:** Ensure you're passing `request_id` through the pipeline:
```python
pipeline = GrillRadarPipeline(request_id=your_request_id)
```

### Issue: JSON parsing keeps failing

**Solution:**
1. Check if LLM is returning valid JSON
2. Enable JSON repair: `LLMClient(enable_json_repair=True)`
3. Check logs for repair attempts
4. Try a different LLM model if problem persists

### Issue: Reports are degraded

**Solution:**
1. Check logs for the `request_id`
2. Look for warnings about JSON parsing or validation
3. Verify LLM API credentials and quotas
4. Try reducing prompt complexity

---

## Performance Optimization

### Reduce Token Usage

```python
# Use smaller model for simple tasks
client = LLMClient(model="claude-3-haiku-20240307")
```

### Disable JSON Repair (if not needed)

```python
client = LLMClient(enable_json_repair=False)
```

### Cache Prompts

```python
from app.core.prompt_builder import PromptBuilder

builder = PromptBuilder()
# Reuse builder across requests to leverage any internal caching
```

---

## Support

- GitHub Issues: https://github.com/yourusername/GrillRadar/issues
- Documentation: README.md
- Architecture: This guide

For urgent issues, include:
1. Request ID from logs
2. Full error message
3. GrillRadar version
4. Environment (OS, Python version)
5. Relevant log excerpt
