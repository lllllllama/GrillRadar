# GrillRadar: Architecture & Design Best Practices Reference

## Quick Reference: Key Design Patterns Implemented

### 1. Configuration-Driven Architecture (TrendRadar-Inspired)

**Why**: Separate configuration from logic, enable changes without code modifications

**Implementation**:
```
File: app/config/domains.yaml (13 domains)
├─ Engineering domains (7): backend, frontend, llm_application, algorithm, data_engineering, mobile, cloud_native
├─ Research domains (6): cv_segmentation, nlp, multimodal, cv_detection, general_ml, reinforcement_learning
└─ Each domain has: keywords, stacks, roles, questions, recommended_reading

File: app/config/modes.yaml (3 modes)
├─ job: 40% Technical Interviewer, 30% Hiring Manager, etc.
├─ grad: 40% Advisor, 30% Reviewer, etc.
└─ mixed: 30% Technical, 30% Advisor (dual assessment)
```

**Benefit**: Add new domain or adjust role weights without touching Python code

---

### 2. Multi-Layer Data Validation

**File References**:
- `app/models/user_config.py` - Input validation (Pydantic)
- `app/core/report_generator.py` - Business logic validation
- `app/core/llm_client.py` - Output validation

**Layers**:
```python
# Layer 1: Pydantic Input Validation
class UserConfig(BaseModel):
    mode: str = Field(..., pattern="^(job|grad|mixed)$")
    resume_text: str = Field(..., min_length=10)
    # Auto-validates on instantiation

# Layer 2: Business Logic Validation
def _validate_report(self, report: Report, user_config: UserConfig):
    if len(report.questions) < 10:
        raise ValueError("Too few questions")
    # Custom business rules

# Layer 3: LLM Output Validation
def call_json(self, system_prompt: str) -> dict:
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
```

**Benefit**: Catch errors at appropriate layers, fail fast with clear messages

---

### 3. Service Layer Abstraction

**File References**:
- `app/core/report_generator.py` - Orchestrator
- `app/core/prompt_builder.py` - Prompt assembly
- `app/core/llm_client.py` - LLM integration
- `app/sources/external_info_service.py` - Data retrieval

**Pattern**: Each service has one responsibility
```python
# ReportGenerator: Orchestration only
class ReportGenerator:
    def __init__(self):
        self.prompt_builder = PromptBuilder()  # Delegate to service
        self.llm_client = LLMClient()          # Delegate to service
    
    def generate_report(self, config):
        prompt = self.prompt_builder.build(config)  # Compose services
        report_data = self.llm_client.call_json(prompt)
        return Report(**report_data)

# Each service is independently testable
class PromptBuilder:
    def _get_domain_knowledge(self, domain): ...
    def _get_external_info(self, config): ...
    def build(self, config): ...
```

**Benefit**: Easy to test, modify, and reuse individual services

---

### 4. Graceful Degradation Pattern

**File Reference**: `app/sources/external_info_service.py`

**Pattern**: Optional features fail gracefully
```python
def retrieve_external_info(self, company, position) -> Optional[ExternalInfoSummary]:
    try:
        jds = self.mock_provider.get_mock_jds(company, position)
        experiences = self.mock_provider.get_mock_experiences(company, position)
        
        # If nothing found, return None (not an error!)
        if not jds and not experiences:
            return None  # System continues with degraded functionality
        
        return InfoAggregator.aggregate(jds, experiences)
    except Exception as e:
        logger.error(f"Failed to retrieve: {e}")
        return None  # Graceful fallback
```

**Benefit**: System works even if optional features fail

---

### 5. Information Aggregation Pattern

**File Reference**: `app/retrieval/info_aggregator.py`

**Pattern**: Extract, aggregate, rank
```python
class InfoAggregator:
    @staticmethod
    def aggregate(jds: List[JobDescription], 
                  experiences: List[InterviewExperience]) -> ExternalInfoSummary:
        
        # Extract keywords from all JDs
        all_keywords = []
        for jd in jds:
            all_keywords.extend(jd.keywords)
        
        # Rank by frequency
        keyword_counter = Counter(all_keywords)
        aggregated_keywords = [kw for kw, _ in keyword_counter.most_common(20)]
        
        # Return structured summary
        return ExternalInfoSummary(
            aggregated_keywords=aggregated_keywords,
            aggregated_topics=aggregated_topics,
            high_frequency_questions=high_frequency_questions
        )
```

**Benefit**: Summarize large datasets into actionable insights

---

### 6. Configuration Injection into Prompts

**File Reference**: `app/core/prompt_builder.py`

**Pattern**: Build comprehensive prompts from multiple sources
```python
def build(self, user_config: UserConfig) -> str:
    # Get configurations
    mode_config = self.modes.get(user_config.mode, {})
    domain_knowledge = self._get_domain_knowledge(user_config.domain)
    external_info_text = self._get_external_info(user_config)
    
    # Inject into prompt template
    prompt = f"""
# Virtual Committee Prompt

## Domain Knowledge (Key Reference)
{domain_knowledge}

## External Information (Real JD/Interview Data)
{external_info_text}

## Role Weights (Mode: {user_config.mode})
{self._format_role_weights(mode_config.get('roles', {}))}

## Input
- Target: {user_config.target_desc}
- Resume: {user_config.resume_text}

## Output Requirements
Generate JSON with: summary, highlights, risks, questions[]
"""
    return prompt
```

**Benefit**: Comprehensive, parameterized prompts that can be modified via config

---

## Key File Locations for Reference

| Purpose | File | Key Class | Pattern |
|---------|------|-----------|---------|
| Input validation | `app/models/user_config.py` | `UserConfig` | Pydantic validation |
| Output schema | `app/models/report.py` | `Report` | Self-validating model |
| Question schema | `app/models/question_item.py` | `QuestionItem` | Rich metadata |
| Domain config | `app/config/domains.yaml` | N/A | YAML-based knowledge |
| Mode config | `app/config/modes.yaml` | N/A | Role weight distribution |
| Settings | `app/config/settings.py` | `Settings` | Pydantic BaseSettings |
| Orchestration | `app/core/report_generator.py` | `ReportGenerator` | Workflow coordination |
| Prompt building | `app/core/prompt_builder.py` | `PromptBuilder` | Configuration injection |
| LLM integration | `app/core/llm_client.py` | `LLMClient` | Provider abstraction |
| Data retrieval | `app/sources/external_info_service.py` | `ExternalInfoService` | Service layer |
| Data aggregation | `app/retrieval/info_aggregator.py` | `InfoAggregator` | Data processing |
| Domain helper | `app/utils/domain_helper.py` | `DomainHelper` | Metadata access |
| API routes | `app/api/report.py` | Various | REST endpoints |
| CLI entry | `cli.py` | N/A | CLI interface |
| FastAPI app | `app/main.py` | N/A | Web service setup |

---

## Code Quality Indicators

### ✅ What's Well-Implemented

1. **Type Safety**
   - All core functions have type hints
   - Pydantic models enforce types
   - Optional types explicitly marked

2. **Error Handling**
   - Multi-layer validation
   - Graceful degradation for optional features
   - Detailed error messages

3. **Logging**
   - Structured logging with context
   - Appropriate log levels (DEBUG, INFO, WARNING, ERROR)
   - Debug info logged for error cases

4. **Code Organization**
   - Clear separation of concerns
   - Single responsibility per module
   - Composition over inheritance

5. **Configurability**
   - Environment variables via BaseSettings
   - YAML-based configuration
   - Command-line arguments in CLI

### 🔄 Areas to Enhance

1. **Testing**
   - No unit tests currently
   - Recommend: pytest with fixtures
   - Target: 80%+ code coverage

2. **Custom Exceptions**
   - Currently uses generic Exception
   - Recommend: Custom exception hierarchy
   - Example:
     ```python
     class GrillRadarError(Exception): pass
     class ConfigurationError(GrillRadarError): pass
     class LLMError(GrillRadarError): pass
     ```

3. **Configuration Validation**
   - Could validate domains.yaml structure at startup
   - Could validate modes.yaml completeness
   - Could add schema files (JSON Schema)

4. **Async/Await**
   - FastAPI supports async
   - Could make LLM calls async
   - Could improve concurrency

5. **Documentation**
   - API docs (Swagger via FastAPI - already done!)
   - Configuration guide
   - Development setup

---

## How to Apply These Patterns

### For Adding a New Domain

1. Edit `app/config/domains.yaml`
2. Add new section:
   ```yaml
   engineering:
     new_domain:
       display_name: "Display Name"
       description: "..."
       keywords: [...]
       common_stacks: [...]
       typical_roles: [...]
       recommended_reading: [...]
   ```
3. No Python code changes needed!
4. Test via API: `GET /api/domains/new_domain`

### For Adding a New Mode

1. Edit `app/config/modes.yaml`
2. Add new mode:
   ```yaml
   new_mode:
     description: "..."
     roles:
       technical_interviewer: 0.35
       advisor: 0.35
       # ...
     question_distribution: {...}
   ```
3. No Python code changes needed!

### For Improving Validation

1. Update Pydantic model in `app/models/`
2. Add business logic validation in `app/core/report_generator.py`
3. Test via `pytest` (when tests are added)

### For Adding External Data Source

1. Create provider class in `app/sources/`
2. Implement data retrieval interface
3. Update `ExternalInfoService` to use it
4. Respect graceful degradation pattern

---

## Performance Considerations

| Operation | Current Approach | Optimization |
|-----------|------------------|--------------|
| Load domains.yaml | Per-request | Load once at startup (singleton) |
| Load modes.yaml | Per-request | Load once at startup (singleton) |
| Mock data generation | In-memory | Already optimized |
| LLM calls | Synchronous | Could be async |
| JSON parsing | Try-catch | Already handles edge cases |

---

## Testing Template

```python
# tests/test_validation.py
import pytest
from app.models.user_config import UserConfig
from pydantic import ValidationError

class TestUserConfigValidation:
    """Test UserConfig Pydantic model"""
    
    def test_valid_config(self):
        config = UserConfig(
            mode="job",
            target_desc="Backend Engineer",
            resume_text="A" * 50
        )
        assert config.mode == "job"
    
    def test_invalid_mode(self):
        with pytest.raises(ValidationError):
            UserConfig(
                mode="invalid_mode",
                target_desc="Engineer",
                resume_text="A" * 50
            )
    
    def test_resume_too_short(self):
        with pytest.raises(ValidationError):
            UserConfig(
                mode="job",
                target_desc="Engineer",
                resume_text="short"
            )

# tests/test_prompt_builder.py
from app.core.prompt_builder import PromptBuilder
from app.models.user_config import UserConfig

class TestPromptBuilder:
    """Test prompt building and configuration injection"""
    
    def test_domain_knowledge_injection(self):
        builder = PromptBuilder()
        config = UserConfig(
            mode="job",
            target_desc="Backend Engineer",
            domain="backend",
            resume_text="A" * 50
        )
        
        prompt = builder.build(config)
        
        # Verify domain knowledge is injected
        assert "分布式系统" in prompt
        assert "后端开发" in prompt
```

---

## Environment Configuration

```bash
# .env (example)
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=16000
DEBUG=false

# Development
DEBUG=true
DEFAULT_MODEL=claude-3-sonnet

# Production
DEBUG=false
DEFAULT_MODEL=claude-sonnet-4
```

---

## Summary: Design Principles Applied

| Principle | Implementation | Benefit |
|-----------|-----------------|---------|
| **Single Responsibility** | Each class has one job | Easy to test and modify |
| **Configuration Over Code** | domains.yaml, modes.yaml | Change behavior without code |
| **Data Validation** | Pydantic + business logic | Fail fast, clear errors |
| **Composition** | ReportGenerator composes services | Flexible, reusable components |
| **Layered Architecture** | API → Orchestration → Services → Data | Clear dependencies, testable |
| **Graceful Degradation** | Optional features fail safely | Robust system behavior |
| **Logging** | Comprehensive structured logs | Observable, debuggable system |
| **Type Safety** | Full type hints | IDE support, fewer bugs |

---

## References

- **Pydantic**: https://docs.pydantic.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **PyYAML**: https://pyyaml.org/
- **Python Type Hints**: https://www.python.org/dev/peps/pep-0484/

