# GrillRadar: Design Patterns & Code Examples

## Pattern 1: Configuration-Driven Architecture

### The Problem
Hard-coded values make systems inflexible:
```python
# BAD: Hard-coded
ROLES_WEIGHTS = {
    "technical_interviewer": 0.40,
    "hiring_manager": 0.30,
    # ... hard to change
}
```

### The Solution: External Configuration
```yaml
# File: app/config/modes.yaml
job:
  roles:
    technical_interviewer: 0.40  # Easy to change!
    hiring_manager: 0.30
    hr: 0.20
```

```python
# File: app/core/prompt_builder.py
class PromptBuilder:
    def __init__(self):
        with open(settings.MODES_CONFIG, 'r') as f:
            self.modes = yaml.safe_load(f)
    
    def build(self, user_config: UserConfig) -> str:
        mode_config = self.modes.get(user_config.mode, {})
        role_weights = mode_config.get('roles', {})
        
        # Inject into prompt
        prompt = f"""
## Role Weights
{self._format_role_weights(role_weights)}
"""
        return prompt
```

### Benefit
Change behavior without touching Python code:
```bash
# Before: Modify code, re-deploy
# After: Edit YAML, reload (or use config hot-reload)
```

---

## Pattern 2: Multi-Layer Validation

### Layer 1: Input Validation (Pydantic)

**File**: `app/models/user_config.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class UserConfig(BaseModel):
    """Self-validating configuration model"""
    
    # Constraint: Must be one of three values
    mode: str = Field(
        ...,
        description="Mode",
        pattern="^(job|grad|mixed)$"
    )
    
    # Constraint: At least 1 character
    target_desc: str = Field(
        ...,
        min_length=1
    )
    
    # Constraint: At least 10 characters (meaningful content)
    resume_text: str = Field(
        ...,
        min_length=10
    )
    
    # Constraint: Must be one of these values
    level: Optional[str] = Field(
        None,
        pattern="^(intern|junior|senior|master|phd)$"
    )
```

**Usage**:
```python
# Valid - no error
config = UserConfig(
    mode="job",
    target_desc="Backend Engineer",
    resume_text="Long resume content..." * 5
)

# Invalid - raises ValidationError immediately
try:
    config = UserConfig(
        mode="invalid_mode",  # ← Pattern mismatch
        target_desc="Engineer",
        resume_text="Short"  # ← Too short
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Layer 2: Business Logic Validation

**File**: `app/core/report_generator.py`

```python
class ReportGenerator:
    def generate_report(self, user_config: UserConfig) -> Report:
        # ... build report ...
        report = Report(**report_data)
        
        # Now validate business rules
        self._validate_report(report, user_config)
        return report
    
    def _validate_report(self, report: Report, user_config: UserConfig):
        """Additional validation after LLM generation"""
        
        # Rule 1: Question count must be 10-20
        num_q = len(report.questions)
        if num_q < 10:
            raise ValueError(f"Too few questions: {num_q}")
        if num_q > 20:
            raise ValueError(f"Too many questions: {num_q}")
        
        # Rule 2: Mode must match
        if report.mode != user_config.mode:
            raise ValueError(f"Mode mismatch")
        
        # Rule 3: Mixed mode needs dual assessment
        if user_config.mode == "mixed":
            has_eng = "【工程候选人评估】" in report.summary
            has_sci = "【科研候选人评估】" in report.summary
            if not (has_eng and has_sci):
                logger.warning("Missing dual assessment in mixed mode")
```

### Layer 3: Output Validation (LLM Response)

**File**: `app/core/llm_client.py`

```python
class LLMClient:
    def call_json(self, system_prompt: str) -> dict:
        """Call LLM and validate JSON response"""
        
        response_text = self.call(system_prompt)
        response_text = response_text.strip()
        
        # Handle markdown code blocks (LLMs often add these)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # Try to parse JSON
        try:
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            raise ValueError(f"Invalid JSON from LLM: {str(e)}")
```

### Result: Comprehensive Validation

```
Input → Pydantic Validation → Business Logic → Output Validation → Clean Report
         (Type safe)          (Business rules)  (JSON correct)
```

---

## Pattern 3: Service Composition

### Single Responsibility
```python
# File: app/core/report_generator.py
class ReportGenerator:
    """ONLY: Coordinate workflow"""
    def __init__(self):
        self.prompt_builder = PromptBuilder()  # Delegate
        self.llm_client = LLMClient()          # Delegate
    
    def generate_report(self, config: UserConfig) -> Report:
        prompt = self.prompt_builder.build(config)
        report_data = self.llm_client.call_json(prompt)
        return Report(**report_data)

# File: app/core/prompt_builder.py
class PromptBuilder:
    """ONLY: Build prompts"""
    def build(self, config: UserConfig) -> str:
        # Build prompt
        return prompt

# File: app/core/llm_client.py
class LLMClient:
    """ONLY: Call LLM"""
    def call_json(self, prompt: str) -> dict:
        # Call LLM, parse JSON
        return data
```

### Why This Pattern Works

```
Easy to Test
├─ Test PromptBuilder independently: build() → prompt
├─ Test LLMClient independently: call_json() → dict
└─ Test ReportGenerator: integration test

Easy to Modify
├─ Change prompt format → modify PromptBuilder
├─ Add LLM provider → modify LLMClient
└─ Change workflow → modify ReportGenerator

Easy to Reuse
├─ Use PromptBuilder elsewhere
├─ Use LLMClient for other tasks
└─ Compose services in different ways
```

---

## Pattern 4: Graceful Degradation

### Problem: What if external data isn't available?

**Bad Approach**: Crash the whole system
```python
# BAD: If external info fails, everything fails
def generate_report(self, config):
    external_info = self.external_info_service.retrieve(...)  # Crashes!
    # Report generation blocked
```

### Good Approach: Continue with degraded functionality

**File**: `app/sources/external_info_service.py`

```python
class ExternalInfoService:
    def retrieve_external_info(self, company, position) -> Optional[ExternalInfoSummary]:
        """Gracefully degrade if external info unavailable"""
        
        try:
            jds = []
            experiences = []
            
            # Try to get JDs
            if self.use_mock:
                jds = self.mock_provider.get_mock_jds(company, position)
            else:
                logger.warning("Real JD crawler not implemented")
                jds = []
            
            # Try to get interview experiences
            if self.use_mock:
                experiences = self.mock_provider.get_mock_experiences(company, position)
            else:
                logger.warning("Real interview crawler not implemented")
                experiences = []
            
            # If NOTHING found, that's OK - return None, not error!
            if not jds and not experiences:
                logger.info("No external info found - that's OK")
                return None  # System continues!
            
            # Aggregate what we have
            return InfoAggregator.aggregate(jds, experiences)
        
        except Exception as e:
            # Even if something breaks, return None (not crash!)
            logger.error(f"Error retrieving external info: {e}", exc_info=True)
            return None  # Graceful fallback
```

**Usage**: Report generation doesn't stop if external info fails

```python
# File: app/core/prompt_builder.py
def _get_external_info(self, user_config: UserConfig) -> str:
    if not user_config.enable_external_info:
        return "未启用外部信息"
    
    # This returns None if external info unavailable
    summary = external_info_service.retrieve_external_info(...)
    
    if summary is None:
        # No external info - just skip it
        return "未检索到外部信息"
    
    # We have external info - use it
    return InfoAggregator.get_summary_for_prompt(summary)
```

### Result
```
System Behavior:
├─ With external info: ← Optimal
│  └─ Report with real JD/interview data
├─ Without external info: ← Degraded, but works
│  └─ Report without external info
└─ External info error: ← Graceful degradation
   └─ System continues, reports as "no external info"
```

---

## Pattern 5: Information Aggregation

### Problem: Too much raw data

**File**: `app/retrieval/info_aggregator.py`

```python
from collections import Counter
from typing import List

class InfoAggregator:
    @staticmethod
    def aggregate(
        jds: List[JobDescription],
        experiences: List[InterviewExperience]
    ) -> ExternalInfoSummary:
        """Extract, rank, and summarize information"""
        
        # Step 1: EXTRACT all keywords from all JDs
        all_keywords = []
        for jd in jds:
            all_keywords.extend(jd.keywords)
        
        # Step 2: RANK by frequency
        keyword_counter = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counter.most_common(20)]
        
        # Step 3: EXTRACT topics from experiences
        all_topics = []
        for exp in experiences:
            all_topics.extend(exp.topics)
        
        # Step 4: RANK topics
        topic_counter = Counter(all_topics)
        top_topics = [topic for topic, _ in topic_counter.most_common(15)]
        
        # Step 5: EXTRACT high-frequency questions
        high_freq_questions = InfoAggregator._extract_high_frequency_questions(
            experiences
        )
        
        # Step 6: RETURN structured summary
        return ExternalInfoSummary(
            job_descriptions=jds,
            interview_experiences=experiences,
            aggregated_keywords=top_keywords,
            aggregated_topics=top_topics,
            high_frequency_questions=high_freq_questions
        )
    
    @staticmethod
    def _extract_high_frequency_questions(
        experiences: List[InterviewExperience]
    ) -> List[str]:
        """Extract questions that appear in multiple experiences"""
        all_questions = []
        for exp in experiences:
            all_questions.extend(exp.questions)
        
        # Simple: return top questions (in reality, use NLP clustering)
        return all_questions[:10]
```

### Result: Actionable Insights

```
Raw Data:              Aggregated Data:
├─ 10 JDs              ├─ Top 20 keywords (ranked)
│  ├─ keywords        │  ├─ 分布式系统
│  ├─ keywords        │  ├─ Redis
│  └─ keywords        │  └─ ...
├─ 50 interview exp.   ├─ Top 15 topics
│  ├─ topics          │  ├─ System Design
│  ├─ topics          │  └─ ...
│  └─ questions       └─ Top 10 questions
└─ ...                   ├─ Design distributed cache?
                         └─ ...
```

---

## Pattern 6: Configuration Injection into Prompts

### Build Comprehensive Prompts from Multiple Sources

**File**: `app/core/prompt_builder.py`

```python
def build(self, user_config: UserConfig) -> str:
    """Compose prompt from multiple configuration sources"""
    
    # 1. Get mode configuration
    mode_config = self.modes.get(user_config.mode, {})
    
    # 2. Get domain knowledge
    domain_knowledge = self._get_domain_knowledge(user_config.domain)
    
    # 3. Get external information (optional)
    external_info_text = self._get_external_info(user_config)
    
    # 4. Get role weights formatted
    role_weights_text = self._format_role_weights(mode_config.get('roles', {}))
    
    # 5. Compose into comprehensive prompt
    prompt = f"""# Virtual Interview Committee System Prompt

## Your Role
You are a 6-person committee: Technical Interviewer, Hiring Manager, etc.

## Current Task
Generate a report for:
- Target: {user_config.target_desc}
- Mode: {user_config.mode}
- Resume: {user_config.resume_text}

### Domain Knowledge (Key Reference)
{domain_knowledge}

### External Information (Real JD/Interview Data)
{external_info_text}

### Role Weights (Mode: {user_config.mode})
{role_weights_text}

### Question Distribution
{self._format_question_distribution(user_config.mode, mode_config)}

## Output Requirements
Generate JSON with:
- summary (100+ chars)
- highlights (50+ chars)
- risks (50+ chars)
- questions (10-20 items)
  - Each question: id, view_role, tag, question, rationale, baseline_answer, support_notes, prompt_template

**Output ONLY valid JSON, no markdown.**
"""
    return prompt
```

### What Makes This Powerful

```
Configuration Files:     Code:                    Prompt:
domains.yaml             PromptBuilder            Comprehensive
├─ backend              ├─ Load YAML             LLM-optimized
├─ frontend             ├─ Load YAML             Prompt with:
└─ ...                  └─ Inject into prompt    ├─ Domain knowledge
                                                 ├─ Mode config
modes.yaml                                       ├─ External info
├─ job                                           ├─ Role weights
├─ grad                                          └─ User input
└─ mixed

Result: No code change needed to adapt prompts!
```

---

## Pattern 7: Singleton Configuration Loading

### Problem: Load YAML multiple times (inefficient)

```python
# BAD: Load every time
class PromptBuilder:
    def build(self, config):
        with open('domains.yaml') as f:  # ← Load YAML every time!
            domains = yaml.safe_load(f)
```

### Solution: Load once at initialization

```python
# GOOD: Load once, reuse
class PromptBuilder:
    def __init__(self):
        # Load once at initialization
        with open(settings.DOMAINS_CONFIG, 'r') as f:
            self.domains = yaml.safe_load(f)
        
        with open(settings.MODES_CONFIG, 'r') as f:
            self.modes = yaml.safe_load(f)
    
    def build(self, config):
        # Reuse pre-loaded configurations
        mode_config = self.modes.get(config.mode, {})
        domain_knowledge = self._get_domain_knowledge(config.domain)
        # ... rest of logic
```

### Usage Pattern

```python
# File: app/utils/domain_helper.py
class DomainHelper:
    def __init__(self):
        with open(settings.DOMAINS_CONFIG, 'r') as f:
            self.domains = yaml.safe_load(f)  # Load once
    
    def get_domain_detail(self, domain: str) -> Optional[Dict]:
        # Reuse loaded data
        for category in ['engineering', 'research']:
            if domain in self.domains[category]:
                return self.domains[category][domain]
        return None

# Global singleton instance
domain_helper = DomainHelper()
```

---

## Pattern 8: CLI vs API Unified Core Logic

### Shared Core
```python
# File: app/core/report_generator.py
class ReportGenerator:
    """Works with both CLI and API"""
    def generate_report(self, user_config: UserConfig) -> Report:
        # Implementation agnostic to CLI or API
```

### CLI Wrapper
```python
# File: cli.py
def main():
    args = parser.parse_args()
    config_data = load_config(args.config)
    resume_text = load_resume(args.resume)
    
    # Use shared core logic
    user_config = UserConfig(**config_data, resume_text=resume_text)
    generator = ReportGenerator()
    report = generator.generate_report(user_config)
    
    # CLI-specific output
    content = report_to_markdown(report)
    save_output(args.output, content)
```

### API Wrapper
```python
# File: app/api/report.py
@router.post("/generate-report")
async def generate_report(request: GenerateReportRequest):
    # Use shared core logic
    user_config = UserConfig(
        mode=request.mode,
        target_desc=request.target_desc,
        resume_text=request.resume_text,
        domain=request.domain,
        enable_external_info=request.enable_external_info,
        target_company=request.target_company
    )
    
    generator = ReportGenerator()
    report = generator.generate_report(user_config)
    
    # API-specific output
    markdown_content = report_to_markdown(report)
    
    return GenerateReportResponse(
        success=True,
        report=report,
        markdown=markdown_content
    )
```

### Benefit
```
Core Logic (ReportGenerator)
├─ CLI: cli.py → UserConfig → generate_report() → Markdown
├─ API: app/api/report.py → UserConfig → generate_report() → JSON + Markdown
└─ Future: Scheduled job → UserConfig → generate_report() → Store
```

---

## Summary: Design Patterns Quick Reference

| Pattern | Location | Use Case | Benefit |
|---------|----------|----------|---------|
| Configuration-Driven | `config/` | Parameterize behavior | Change without code |
| Multi-Layer Validation | `models/` + `core/` | Catch errors early | Type safety + business rules |
| Service Composition | `core/` | Coordinate components | Testable, reusable |
| Graceful Degradation | `sources/` | Handle failures | Robust systems |
| Information Aggregation | `retrieval/` | Summarize data | Actionable insights |
| Configuration Injection | `prompt_builder.py` | Dynamic prompts | Comprehensive LLM input |
| Singleton Loading | `__init__` | Efficient reuse | Avoid repeated loads |
| Unified Core Logic | `core/` + `cli.py` + `api/` | Multiple interfaces | DRY principle |

