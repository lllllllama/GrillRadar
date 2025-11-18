# Multi-Agent System Architecture

## Overview

GrillRadar has been upgraded from a "virtual committee" (single LLM prompt) to a **real, structured multi-agent discussion + selection pipeline**. This enhancement provides:

- **Better question quality**: Multiple specialized agents propose questions from different perspectives
- **Fair and balanced coverage**: Forum engine ensures comprehensive dimension coverage and difficulty balance
- **Harsh but fair questions**: Advocate agent acts as quality gatekeeper
- **Debuggable and iterative**: Debug mode saves all intermediate artifacts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentOrchestrator                        │
│  Coordinates the entire multi-agent workflow                │
└─────────────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │  Phase 1  │      │  Phase 2  │     │  Phase 3  │
    │ Proposals │──────▶│  Forum    │─────▶│ Assembly  │
    └───────────┘      │Discussion │     └───────────┘
                       └───────────┘

Phase 1: Parallel Agent Proposals
  - TechnicalInterviewerAgent
  - HiringManagerAgent
  - HRAgent
  - AdvisorAgent
  - ReviewerAgent
  - AdvocateAgent

Phase 2: Forum Discussion (ForumEngine)
  1. Deduplication
  2. Quality filtering
  3. Labeling & Scoring (dimension, difficulty, relevance)
  4. Coverage-aware selection
  5. Advocate gatekeeper review
  6. Enhancement to QuestionItems

Phase 3: Report Assembly
  - Generate summary, highlights, risks
  - Assemble final Report object
```

## Core Components

### 1. Base Abstractions (`app/agents/base_agent.py`)

- **`AgentConfig`**: Configuration for each agent (name, role, temperature, question quota, etc.)
- **`BaseAgent`**: Abstract base class all agents inherit from
  - `propose_questions()`: Core method each agent implements
  - `_call_llm_structured()`: LLM call with retry logic
  - `validate_draft_question()`: Quality validation

### 2. Agent Models (`app/agents/models.py`)

- **`DraftQuestion`**: Intermediate question format from agents
  - `question`, `rationale`, `role_name`, `role_display`
  - `tags`, `confidence`, `metadata`
- **`AgentOutput`**: Output from a single agent
- **`AgentState`**: Tracks execution state (proposals, errors, latencies, costs)
- **`WorkflowContext`**: Mutable context passed between agents

### 3. Concrete Agents

Each agent has a specific perspective and question focus:

#### **TechnicalInterviewerAgent** (`app/agents/technical_interviewer.py`)
- **Role**: Technical depth, CS fundamentals, system design
- **Focus**: Algorithms, data structures, architecture, engineering best practices
- **Modes**: Dominant in `job` and `mixed` modes

#### **HiringManagerAgent** (`app/agents/hiring_manager.py`)
- **Role**: Overall fit, project impact, career trajectory
- **Focus**: Project authenticity, leadership, business value
- **Modes**: Important in `job` mode

#### **HRAgent** (`app/agents/hr_agent.py`)
- **Role**: Soft skills, culture fit, teamwork
- **Focus**: Communication, collaboration, career planning
- **Modes**: Supporting role in all modes

#### **AdvisorAgent** (`app/agents/advisor_agent.py`)
- **Role**: Academic advisor/mentor perspective
- **Focus**: Research potential, academic curiosity, mentorship fit
- **Modes**: Dominant in `grad` and `mixed` modes

#### **ReviewerAgent** (`app/agents/reviewer_agent.py`)
- **Role**: Academic reviewer/evaluator
- **Focus**: Research methodology, paper reading, critical thinking
- **Modes**: Important in `grad` mode

#### **AdvocateAgent** (`app/agents/advocate_agent.py`)
- **Role**: Quality control and fairness checker
- **Focus**: Ensuring questions are fair, relevant, and appropriate
- **Special**: Acts as both question proposer AND gatekeeper in selection phase

### 4. Agent Orchestrator (`app/core/agent_orchestrator.py`)

**Responsibilities**:
- Initialize all 6 agents
- Collect proposals in parallel (using `asyncio.gather`)
- Track metrics (LLM calls, tokens, costs, latencies)
- Coordinate with ForumEngine
- Assemble final Report

**Key Methods**:
- `generate_report(user_config, enable_multi_agent)`: Main entry point
- `_collect_proposals(context)`: Parallel agent execution
- `_assemble_report(questions, user_config, context)`: Final report generation

### 5. Forum Engine (`app/core/forum_engine.py`)

**Phases**:

1. **Deduplication**: Merge similar questions (60% similarity threshold)
2. **Quality Filtering**: Remove low-confidence or weak questions
3. **Labeling & Scoring**:
   - Assign `dimension`: foundation, engineering, project_depth, research_method, reflection, soft_skill
   - Assign `difficulty`: basic, intermediate, killer
   - Calculate `relevance_score` (1-5)
4. **Coverage-Aware Selection**:
   - Respect target question count from `modes.yaml`
   - Ensure minimum dimension coverage per mode
   - Balance difficulty distribution (30% basic, 50% intermediate, 20% killer)
5. **Advocate Gatekeeper**: Filter offensive, trick, or low-value questions
6. **Enhancement**: Convert to final `QuestionItem` with full metadata

**Key Methods**:
- `discuss()`: Main coordination method
- `_label_and_score()`: Dimension/difficulty/score assignment
- `_select_with_coverage()`: Coverage-aware selection
- `_advocate_review()`: Quality gatekeeper

### 6. Enhanced QuestionItem Model (`app/models/question_item.py`)

New optional fields for multi-agent system:
- **`dimension`**: Question dimension for coverage analysis
- **`difficulty`**: Question difficulty level
- **`relevance_score`**: Relevance score (0-5)

These fields enable:
- Frontend visualization of question distribution
- Training mode progression (basic → intermediate → killer)
- Analytics and quality metrics

## Configuration

### `app/config/modes.yaml`

Defines agent roles and question distribution for each mode:

```yaml
job:
  roles:
    technical_interviewer: 0.40
    hiring_manager: 0.30
    hr: 0.20
    advisor: 0.05
    reviewer: 0.05
  question_distribution:
    cs_fundamentals: 0.30
    project_depth: 0.30
    system_design: 0.25
    soft_skills: 0.15
  question_count:
    min: 12
    max: 18
    target: 15

grad:
  roles:
    advisor: 0.40
    reviewer: 0.30
    technical_interviewer: 0.15
    hr: 0.10
    hiring_manager: 0.05
  question_distribution:
    research_interest: 0.25
    research_methodology: 0.25
    paper_reading: 0.20
    cs_fundamentals: 0.20
    attitude: 0.10
  question_count:
    min: 10
    max: 16
    target: 13

mixed:
  roles:
    technical_interviewer: 0.30
    advisor: 0.30
    reviewer: 0.20
    hiring_manager: 0.15
    hr: 0.05
  question_distribution:
    engineering: 0.50
    research: 0.50
  question_count:
    min: 14
    max: 20
    target: 17
```

### `app/config/settings.py`

Multi-agent settings:

```python
# Multi-Agent配置
MULTI_AGENT_ENABLED: bool = True  # 启用多智能体模式
GRILLRADAR_DEBUG_AGENTS: bool = False  # 调试模式：保存中间产物

# 路径配置
DEBUG_DIR: Path = BASE_DIR / "debug"
```

Environment variables:
- `MULTI_AGENT_ENABLED=true/false`: Enable/disable multi-agent mode
- `GRILLRADAR_DEBUG_AGENTS=1`: Enable debug mode

## Debug Mode

When enabled (`GRILLRADAR_DEBUG_AGENTS=1`), the system saves intermediate artifacts to `debug/session_<timestamp>/`:

```
debug/
└── session_20250118_143022/
    ├── technical_interviewer_output.json
    ├── hiring_manager_output.json
    ├── hr_specialist_output.json
    ├── academic_advisor_output.json
    ├── academic_reviewer_output.json
    ├── candidate_advocate_output.json
    ├── pre_selection_candidates.json
    ├── final_selected.json
    ├── advocate_feedback.json
    └── workflow_summary.json
```

**Enable debug mode**:

CLI:
```bash
python cli.py --config config.json --resume resume.txt --debug-agents
```

Environment:
```bash
export GRILLRADAR_DEBUG_AGENTS=1
```

## Usage

### API

The API automatically uses multi-agent mode if enabled in settings:

```python
# app/api/report.py
if settings.MULTI_AGENT_ENABLED:
    llm_client = LLMClient()
    orchestrator = AgentOrchestrator(llm_client)
    report = await orchestrator.generate_report(user_config, enable_multi_agent=True)
else:
    generator = ReportGenerator()
    report = generator.generate_report(user_config)
```

### CLI

The CLI supports explicit flags to override settings:

```bash
# Force enable multi-agent mode
python cli.py --config config.json --resume resume.txt --multi-agent

# Force disable (use fallback)
python cli.py --config config.json --resume resume.txt --no-multi-agent

# Enable with debug
python cli.py --config config.json --resume resume.txt --multi-agent --debug-agents
```

### Programmatic

```python
from app.core.agent_orchestrator import AgentOrchestrator
from app.core.llm_client import LLMClient
from app.models.user_config import UserConfig

# Create user config
user_config = UserConfig(
    mode="job",
    target_desc="ByteDance - Backend Engineer",
    domain="backend",
    resume_text=resume_text
)

# Use multi-agent orchestrator
llm_client = LLMClient()
orchestrator = AgentOrchestrator(llm_client)
report = await orchestrator.generate_report(user_config, enable_multi_agent=True)
```

## Backward Compatibility

The multi-agent system is **fully backward compatible**:

1. **Fallback mode**: When `MULTI_AGENT_ENABLED=false`, the system uses the original `ReportGenerator`
2. **Same input/output contract**: `UserConfig` → `Report` interface unchanged
3. **Graceful degradation**: If multi-agent mode fails, automatically falls back to single-agent mode

## Performance Considerations

**Parallelization**:
- All 6 agents run in parallel using `asyncio.gather`
- Typical total time: ~10-30s (depending on LLM latency)

**Cost**:
- Multi-agent mode makes 6-8 LLM calls (vs 1 in single-agent mode)
- Estimated cost increase: 6-8x
- Debug mode tracks costs via `WorkflowContext`

**Optimization opportunities**:
- Cache agent outputs for same resume
- Reduce number of active agents per mode
- Use smaller/faster models for specific agents (e.g., Haiku for advocate)

## Testing

Run tests for multi-agent system:

```bash
# Test agents
pytest tests/test_agents.py

# Test orchestrator
pytest tests/test_agent_orchestrator.py

# Integration test
pytest tests/test_multi_agent_integration.py
```

Compare single vs multi-agent:

```bash
python examples/compare_single_vs_multi_agent.py
```

## Future Enhancements

1. **Dynamic agent selection**: Enable/disable agents per request
2. **LLM-based advocate review**: Replace heuristics with LLM call
3. **Embedding-based deduplication**: More sophisticated similarity detection
4. **Agent performance tracking**: Monitor which agents contribute best questions
5. **Adaptive coverage**: Learn optimal dimension distribution from feedback
6. **Question revision**: Agents can revise questions based on forum discussion
7. **Multi-round discussion**: Iterate between proposal and selection phases

## Key Design Principles

1. **Structure over cleverness**: Clean, testable skeleton
2. **Debuggable artifacts**: All intermediate states observable
3. **Simple heuristics first**: Only optimize when proven necessary
4. **Fail gracefully**: Fallback to single-agent mode on errors
5. **Observable performance**: Track costs, latencies, coverage

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
