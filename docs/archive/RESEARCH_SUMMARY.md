# BettaFish Multi-Agent Architecture Research Summary

## Research Scope

This research analyzed the GrillRadar project's planned evolution to a **BettaFish-style multi-agent architecture** (Milestone 5), examining:
- Current single-LLM implementation (M1-M4)
- Target multi-agent design patterns
- Agent communication and coordination
- Code structure and implementation
- State management approaches
- Error handling in distributed systems
- Agent specialization and roles
- Multi-agent testing strategies

---

## Files Analyzed

### Core Architecture
1. **app/core/report_generator.py** (120 lines)
   - Current orchestration logic
   - Single LLM call pattern
   - Report validation and error handling

2. **app/core/prompt_builder.py** (341 lines)
   - Multi-role prompt construction
   - Domain knowledge injection (Milestone 3)
   - External info integration (Milestone 4)

3. **app/core/llm_client.py** (160 lines)
   - Unified LLM interface (Claude + OpenAI)
   - JSON response handling
   - Error recovery

### Data Models
4. **app/models/report.py** (90 lines)
   - Report structure with metadata
   - Pydantic validation

5. **app/models/user_config.py** (67 lines)
   - User input configuration
   - Domain and mode settings

6. **app/models/question_item.py** (67 lines)
   - Individual question structure
   - Baseline answers and support materials
   - Practice prompt templates

7. **app/models/external_info.py** (175 lines)
   - JobDescription model
   - InterviewExperience model
   - ExternalInfoSummary aggregation

### Information Retrieval
8. **app/retrieval/info_aggregator.py** (159 lines)
   - Multi-source information aggregation
   - Keyword and topic extraction
   - Deduplication patterns

9. **app/sources/external_info_service.py** (99 lines)
   - External data source coordination
   - Mock data provider integration

10. **app/sources/mock_provider.py** (197 lines)
    - Sample JD and interview experience data
    - Data filtering and aggregation patterns

### API & Configuration
11. **app/api/report.py** (217 lines)
    - Report generation endpoints
    - External info search API
    - Domain management endpoints

12. **app/config/settings.py** (43 lines)
    - Application configuration management
    - Path and API key handling

13. **app/config/modes.yaml** (60 lines)
    - Mode configurations (job/grad/mixed)
    - Role weights and question distribution

14. **app/config/domains.yaml** (150+ lines)
    - Domain-specific knowledge
    - Keywords, stacks, papers, references

### Project Documentation
15. **Claude.md** (1812 lines)
    - Comprehensive project specification
    - Milestone 5 detailed design
    - BettaFish architecture patterns
    - ForumEngine concept

16. **README.md** (375 lines)
    - Project overview
    - Features and roadmap
    - BettaFish reference

---

## Key Findings

### 1. Current Architecture (M1-M4): Single-Prompt Simulation

**Pattern:**
```
UserConfig + Resume → PromptBuilder → Single LLM Call → JSON Parsing → Report
```

**Characteristics:**
- All 6 roles simulated in one prompt
- Deterministic, no iteration
- Cost-efficient (~$0.015 per call)
- Quality ceiling due to prompt complexity

**Strengths:**
- Simple, maintainable code
- Low cost and fast
- Proven pattern (works well)

**Weaknesses:**
- Limited cross-role refinement
- No agent specialization
- Scaling limitations for complexity

---

### 2. Target Architecture (M5): True Multi-Agent System

**Pattern:**
```
UserConfig + Resume
    ↓
[6 Agents] → Parallel LLM Calls
    ↓
DraftQuestion Aggregation
    ↓
ForumEngine Discussion & Filtering
    ↓
Question Enhancement
    ↓
ReportAgent Final Generation
    ↓
Report JSON
```

**Key Innovation: ForumEngine**
- Agents "discuss" via orchestrated consolidation
- Semantic deduplication
- Quality-based filtering
- Coverage validation
- Fair evaluation (advocate agent)

---

### 3. Agent Specialization

**Six-Role Committee:**

| Role | M1-M4 Weight | Job Mode | Grad Mode | Key Responsibility |
|------|-------------|----------|-----------|-------------------|
| Technical Interviewer | Simulated | 40% | 15% | CS fundamentals, system design |
| Hiring Manager | Simulated | 30% | 5% | Role fit, business impact |
| HR | Simulated | 20% | 10% | Soft skills, culture |
| Advisor | Simulated | 5% | 40% | Research ability, potential |
| Reviewer | Simulated | 5% | 30% | Academic rigor, methodology |
| Advocate | NEW | Implicit | Implicit | Quality control, fairness |

**Design Pattern:**
- Each agent: narrow, well-defined responsibility
- Independent proposal generation
- Confidence scoring for quality signals
- Standard DraftQuestion interface

---

### 4. Communication Patterns

**Phase 1: Agent Proposals**
```
Agent: "I propose these 3-5 questions with confidence scores"
Data: DraftQuestion(question, rationale, confidence, tags, ...)
Transport: Async/await with timeout handling
```

**Phase 2: Forum Discussion**
```
ForumEngine: "Consolidate these 30-40 proposals"
Operations:
  - Semantic deduplication (keep high-confidence)
  - Quality filtering (remove <0.6 confidence)
  - Coverage validation (ensure breadth)
  - Fairness checking (advocate review)
Output: 10-20 final candidates
```

**Phase 3: Enhancement**
```
ReportAgent: "Enrich selected questions with baseline answers"
Inputs: DraftQuestion
Outputs: QuestionItem (with baseline_answer, support_notes, prompt_template)
```

---

### 5. State Management Approach

**Three-Tier State Tracking:**

1. **Execution State** (AgentState)
   - Workflow ID (unique per generation)
   - Phase 1: Individual agent proposals + errors
   - Phase 2: Merged/filtered questions
   - Phase 3: Final questions
   - Monitoring: LLM calls, cost estimates

2. **Context Passing** (WorkflowContext)
   - User config
   - Resume text
   - Config caches
   - Shared across agents

3. **Optional Persistence**
   - Save intermediate states for debugging
   - Audit trails for decision tracing
   - Cost analysis and optimization

---

### 6. Error Handling in Distributed Context

**Failure Modes & Mitigations:**

| Failure | Impact | Mitigation |
|---------|--------|-----------|
| Agent Timeout | Incomplete proposals | Async timeout + skip agent |
| LLM API Error | Cannot generate | Retry with exponential backoff |
| JSON Parse Error | Output invalid | Schema validation + fallback |
| Quality Issues | Poor questions | Advocate filter + threshold |
| Coverage Gaps | Missing categories | ForumEngine detection + request |
| Cost Overrun | Expensive | Token counting + parallelization |

**Resilience Patterns:**
- Circuit Breaker (prevent cascading)
- Retry with Backoff (transient errors)
- Fallback (cached or single-LLM)
- Timeout Protection (prevent hanging)
- Graceful Degradation (continue without failed agents)

---

### 7. Implementation Blueprint

**Directory Structure:**
```
app/agents/              # NEW
├── base_agent.py        # Abstract base + DraftQuestion model
├── technical_interviewer.py, hiring_manager.py, ...  # 6 agents
├── report_agent.py      # Final report generation
└── tools/               # Shared utilities

app/core/
├── agent_orchestrator.py  # NEW: Main coordinator
├── forum_engine.py        # NEW: Discussion logic
├── report_generator.py    # REFACTORED: Delegates to orchestrator
└── [existing files]

tests/
├── test_agents/          # NEW
│   ├── test_base_agent.py
│   ├── test_technical_agent.py, ...
│   ├── test_forum_engine.py
│   └── test_agent_orchestrator.py
└── test_e2e/
    └── test_full_pipeline.py
```

**Key Classes:**
1. **BaseAgent** - Abstract class with propose_questions() interface
2. **DraftQuestion** - Intermediate format (question, rationale, confidence, tags)
3. **ForumEngine** - Consolidation logic (dedup, filter, enhance)
4. **AgentOrchestrator** - Main coordinator (parallel execution, phase management)
5. **AgentState** - Execution state tracking

---

### 8. Cost & Performance Analysis

**Current (M1-M4):**
- LLM Calls: 1
- Input Tokens: ~3,000
- Output Tokens: ~1,000
- Cost: ~$0.015
- Time: 5-10 seconds

**Target (M5):**
- LLM Calls: 8 (6 agents + forum + report)
- Input Tokens: ~25,000
- Output Tokens: ~10,000
- Cost: ~$0.225 (15x)
- Time: 15-30 seconds (parallel speedup)
- Quality: 3-5x improvement

**Optimization Opportunities:**
1. **Caching** (50-70% cost reduction) - Cache agent outputs for similar resumes
2. **Adaptive Mode** (20-30% reduction) - Skip agents not relevant to domain
3. **Model Selection** (30-40% reduction) - Use cheaper models for initial proposals
4. **Batching** (10-20% reduction) - Combine multiple generation requests

---

### 9. Testing Strategy

**Unit Tests:**
- Individual agent behavior
- DraftQuestion format validation
- Confidence scoring correctness
- Prompt generation accuracy

**Integration Tests:**
- Full workflow for each mode (job/grad/mixed)
- Agent proposal aggregation
- ForumEngine deduplication logic
- Question enhancement pipeline

**Performance Tests:**
- Parallel execution speedup
- Token counting accuracy
- Cost estimation validation

**E2E Tests:**
- Complete pipeline with real LLM calls
- Output quality validation
- Graceful fallback on failures

---

### 10. Patterns Worth Extracting

**1. Prompt Composition**
```python
# Each agent gets a role-specific prompt template
# Reduces prompt complexity, improves specialization
prompt = f"""
You are a {role_name}.
Your evaluation dimension: {responsibility}
Quality criteria: {criteria}
...
"""
```

**2. Confidence Scoring**
```python
# Every agent output includes 0.0-1.0 confidence
# Enables intelligent filtering and quality control
confidence = 0.85  # High confidence = keep
confidence = 0.45  # Low confidence = filter out
```

**3. Semantic Deduplication**
```python
# Compare questions by content similarity
# Keep only high-confidence duplicates
# Prevents redundancy while preserving diversity
```

**4. Coverage Validation**
```python
# Ensure question distribution across categories
# If gaps detected, request additional questions
# Guarantees breadth of evaluation
```

**5. Asynchronous Orchestration**
```python
# asyncio.gather() for parallel agent execution
# Massive speedup with no code complexity increase
# Enables scaling to many agents
```

---

## Recommendations for GrillRadar

### Phase 1: Foundation (Weeks 1-2)
- Implement BaseAgent abstract class
- Create DraftQuestion data model
- Implement 6 concrete agent classes
- Set up async/await infrastructure

### Phase 2: Orchestration (Weeks 2-3)
- Implement ForumEngine deduplication & filtering
- Implement AgentOrchestrator main coordinator
- Add state management (AgentState, WorkflowContext)
- Integrate with existing LLMClient

### Phase 3: Testing (Week 3-4)
- Write comprehensive unit tests
- Create integration test suite
- Performance benchmarking
- Cost tracking validation

### Phase 4: Deployment (Week 4+)
- API endpoint integration
- Gradual rollout with feature flag
- A/B testing vs. M1-M4
- Monitoring and observability

---

## Documents Generated

1. **BETTAFISH_ANALYSIS.md** (11,000+ words)
   - Comprehensive architecture analysis
   - Implementation blueprints with code
   - State management design
   - Error handling patterns
   - Testing strategy
   - Development roadmap

2. **MULTI_AGENT_QUICK_START.md** (500+ words)
   - Quick reference guide
   - Architecture layers
   - Communication patterns
   - Cost analysis
   - FAQ
   - Development checklist

3. **RESEARCH_SUMMARY.md** (This document)
   - Research scope and files analyzed
   - Key findings and patterns
   - Implementation recommendations
   - Document reference

---

## References

### Source Files (Analyzed)
- `/home/user/GrillRadar/app/core/report_generator.py`
- `/home/user/GrillRadar/app/core/prompt_builder.py`
- `/home/user/GrillRadar/app/core/llm_client.py`
- `/home/user/GrillRadar/app/models/*.py` (all models)
- `/home/user/GrillRadar/app/api/report.py`
- `/home/user/GrillRadar/Claude.md` (project spec)
- `/home/user/GrillRadar/README.md`

### Key Concepts
- **BettaFish**: Multi-agent opinion analysis system (reference implementation)
- **ForumEngine**: Multi-round agent discussion pattern
- **Chain-of-Thought**: Reasoning steps improve LLM output quality
- **Multi-Agent Debate**: Agents arguing improves consensus

---

## Next Steps

1. **Read BETTAFISH_ANALYSIS.md** for detailed design patterns
2. **Read MULTI_AGENT_QUICK_START.md** for implementation overview
3. **Review Milestone 5 section** in Claude.md for project context
4. **Begin Phase 1 implementation** with BaseAgent and agent classes
5. **Set up testing infrastructure** early (test-driven development)

---

**Research Date:** 2025-11-17
**Project:** GrillRadar (Milestone 5: Multi-Agent Architecture)
**Scope:** Analysis of BettaFish-style agent orchestration patterns
**Status:** Complete with actionable recommendations
