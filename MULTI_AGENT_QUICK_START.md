# BettaFish Multi-Agent Architecture: Quick Start Guide

## Overview

GrillRadar Milestone 5 evolves from a **single-LLM approach** (M1-M4) to a **BettaFish-style multi-agent system** where 6 specialized agents collaborate through an orchestrated workflow.

---

## Key Components

### 1. Six Specialized Agents

```
┌─────────────────────────────────────────────────────────┐
│                   Six-Agent Committee                    │
├──────────┬──────────┬─────────┬────────┬──────────┬─────┤
│Technical │ Hiring   │ HR      │Advisor │Reviewer  │Advoc│
│Interview │Manager   │         │        │          │ate  │
│          │          │         │        │          │     │
│ 40%      │ 30%      │ 20%     │ 5%     │ 5%       │     │ (job mode)
│(CS+Design)(Role Fit)(Soft)  (Research)(Academic) (QA)  │
└──────────┴──────────┴─────────┴────────┴──────────┴─────┘
```

**Each agent:**
- Makes independent 3-5 question proposals
- Targets specific evaluation dimensions
- Produces confidence scores for quality assessment
- Communicates via standard interface (DraftQuestion)

### 2. ForumEngine: Multi-Round Discussion

```
Agent Proposals → Deduplication → Quality Filter → Coverage Check → Enhancement → Final Report
                 (Merge similar)  (Remove low)     (Ensure breadth)  (Enrich)     (JSON output)
```

### 3. AgentOrchestrator: Main Coordinator

```python
# Pseudo-code flow
async def generate_report(config):
    # Phase 1: Parallel proposals (6 LLM calls)
    proposals = await asyncio.gather(
        technical.propose_questions(...),
        hiring_manager.propose_questions(...),
        ...
    )
    
    # Phase 2: Forum discussion (1 consolidated step)
    final = forum_engine.discuss(proposals)
    
    # Phase 3: Report generation (1 final LLM call)
    return report_agent.generate(final)
```

---

## Architecture Layers

### Data Model Layer
```
UserConfig → Resume → Domain Config
  ↓
DraftQuestion (intermediate)
  ↓
QuestionItem (final, with baseline answer + support notes)
  ↓
Report (JSON output)
```

### Agent Layer
- **TechnicalInterviewerAgent**: CS fundamentals, system design
- **HiringManagerAgent**: Role fit, business impact
- **HRAgent**: Soft skills, cultural fit
- **AdvisorAgent**: Research ability, academic trajectory
- **ReviewerAgent**: Paper reading, methodology
- **AdvocateAgent**: Quality control, fairness checking

### Orchestration Layer
- **ForumEngine**: Consolidates agent outputs
- **AgentOrchestrator**: Manages workflow
- **StateManager**: Tracks execution state

### Support Layer
- **LLMClient**: Unified LLM API (Claude or OpenAI)
- **PromptBuilder**: Generates agent-specific prompts
- **Tools**: Resume parsing, domain matching, validation

---

## Communication Patterns

### 1. Agent→Orchestrator: DraftQuestion Format
```python
class DraftQuestion(BaseModel):
    question: str              # The actual question
    rationale: str             # Why ask this
    role_name: str             # Which agent proposed
    role_display: str          # Display name in Chinese
    tags: List[str]            # Topic labels
    confidence: float          # 0.0-1.0 quality signal
    metadata: Dict             # Extra context
```

### 2. Orchestrator→Forum: Aggregated Proposals
```python
{
    "technical_interviewer": [DraftQuestion, ...],
    "hiring_manager": [DraftQuestion, ...],
    ...
}
```

### 3. Forum→Report: Final QuestionItem Format
```python
class QuestionItem(BaseModel):
    id: int                    # Question number
    view_role: str            # Which role asks
    tag: str                  # Topic label
    question: str             # The question
    rationale: str            # Why ask
    baseline_answer: str      # Expected answer framework
    support_notes: str        # Reference materials
    prompt_template: str      # Practice prompt for users
```

---

## State Management

### Workflow State Tracking
```python
class AgentState(BaseModel):
    workflow_id: str
    # Phase 1 state
    proposals: Dict[str, List[DraftQuestion]]
    proposal_errors: Dict[str, str]
    # Phase 2 state
    merged_questions: List[DraftQuestion]
    filtered_questions: List[DraftQuestion]
    # Phase 3 state
    final_questions: List[QuestionItem]
    # Debug info
    total_llm_calls: int
    total_cost_estimate: float
```

### State Persistence (Optional)
- Save intermediate states for debugging
- Track agent behavior patterns
- Audit decision-making trail
- Analyze cost vs. quality tradeoffs

---

## Error Handling

### Resilience Patterns
1. **Circuit Breaker**: Prevent cascading failures
2. **Retry with Backoff**: Exponential backoff for transient errors
3. **Fallback**: Use cached or single-LLM approach if multi-agent fails
4. **Timeout**: Prevent hanging on slow agents
5. **Graceful Degradation**: Skip failed agents, continue with others

### Failure Recovery
```
Multi-Agent Fails
    ↓
Try Cached Report
    ↓
Fall back to Single-LLM
    ↓
Return Error to User
```

---

## Testing Strategy

### Unit Tests
```bash
tests/test_agents/
├── test_technical_agent.py      # Individual agent behavior
├── test_hiring_manager_agent.py  # Role-specific logic
├── test_forum_engine.py          # Deduplication, filtering
└── test_agent_orchestrator.py    # End-to-end workflows
```

### Integration Tests
```bash
# Test complete workflow for each mode
- test_job_mode_full_pipeline()
- test_grad_mode_full_pipeline()
- test_mixed_mode_full_pipeline()
```

### Performance Tests
```bash
# Ensure parallelization provides speedup
- test_parallel_execution_performance()
- test_cost_tracking_accuracy()
```

---

## Cost Analysis

### Current Approach (M1-M4)
- **LLM Calls**: 1
- **Tokens**: ~3k input + 1k output
- **Cost**: ~$0.015
- **Time**: ~5-10 seconds

### Multi-Agent Approach (M5)
- **LLM Calls**: 8 (6 agents + forum + report)
- **Tokens**: ~25k input + 10k output
- **Cost**: ~$0.225
- **Time**: ~15-30 seconds (parallel)
- **Quality Improvement**: 3-5x better question diversity and accuracy

### Optimization Opportunities
1. **Caching**: Cache agent outputs for similar resumes (50-70% reduction)
2. **Adaptive Mode**: Skip agents not relevant to domain
3. **Batching**: Combine multiple generation requests
4. **Model Selection**: Use cheaper models for initial proposals

---

## Integration with Existing Code

### Backward Compatibility
- Keep existing `ReportGenerator` as fallback
- Expose new `AgentOrchestrator` via API flag
- Gradual rollout with A/B testing

### API Changes
```python
# New endpoint for multi-agent approach
POST /api/generate-report-multi-agent
{
    "mode": "job",
    "target_desc": "...",
    "resume_text": "...",
    "use_multi_agent": true  # NEW flag
}
```

### Configuration
```yaml
# config/agents.yaml (new file)
agents:
  technical_interviewer:
    enabled: true
    temperature: 0.7
    timeout: 30
  hiring_manager:
    enabled: true
    temperature: 0.7
    timeout: 30
  # ... rest of agents

forum:
  deduplication_threshold: 0.8
  confidence_threshold: 0.6
  enable_caching: true
```

---

## Development Roadmap

### Week 1-2: Core Implementation
- [ ] BaseAgent abstract class
- [ ] 6 concrete agent implementations
- [ ] DraftQuestion data model
- [ ] ForumEngine deduplication logic

### Week 2-3: Orchestration
- [ ] AgentOrchestrator main coordinator
- [ ] State management (AgentState, WorkflowContext)
- [ ] Error handling & resilience patterns
- [ ] Basic integration with LLMClient

### Week 3-4: Testing & Polish
- [ ] Unit tests for each agent
- [ ] Integration tests for full workflow
- [ ] Performance benchmarking
- [ ] Cost tracking and optimization

### Week 4+: Refinement & Deployment
- [ ] API integration
- [ ] Monitoring & observability
- [ ] Gradual rollout
- [ ] User feedback collection

---

## Example: Full Workflow

### 1. Input
```python
config = UserConfig(
    mode="job",
    target_desc="字节跳动后端工程师",
    domain="backend",
    resume_text="..."
)
```

### 2. Parallel Agent Proposals
```python
# Technical Agent proposes:
[
    DraftQuestion("讲一下你的分布式系统设计", "考察系统设计", confidence=0.85),
    DraftQuestion("如何解决缓存一致性问题", "考察缓存知识", confidence=0.80),
    ...
]

# Hiring Manager proposes:
[
    DraftQuestion("为什么对字节跳动感兴趣", "考察匹配度", confidence=0.75),
    ...
]

# HR proposes:
[
    DraftQuestion("讲一个团队冲突的例子", "考察软技能", confidence=0.70),
    ...
]

# ... (other agents)
```

### 3. Forum Discussion
```python
# Consolidate similar questions
# Remove low-confidence ones (< 0.6)
# Check coverage (30% CS + 30% project + 25% design + 15% soft)
# Enhance each to final form with baseline answers
```

### 4. Final Output
```python
Report(
    mode="job",
    summary="作为后端候选人，你的分布式系统经验...",
    highlights="1. 有分布式爬虫项目经验...",
    risks="1. 项目中缺少性能优化指标...",
    questions=[
        QuestionItem(
            id=1,
            view_role="技术面试官",
            tag="分布式系统",
            question="讲一下你的分布式系统设计...",
            rationale="考察系统设计思维...",
            baseline_answer="一个好的回答应该包含：...",
            support_notes="关键概念：...",
            prompt_template="我在简历中写了... {your_experience} ...请帮我组织..."
        ),
        ...  # 14 more questions
    ]
)
```

---

## Key Insights

1. **Specialization > Generalization**: Independent specialized agents beat a single generalist prompt
2. **Async I/O**: Parallel execution is critical for acceptable performance
3. **Quality Signals**: Confidence scores enable intelligent filtering
4. **Graceful Degradation**: Fallback mechanisms make the system robust
5. **Testability**: Modular design makes testing easier

---

## FAQ

### Q: Why 6 agents instead of 3?
A: More agents = more diverse perspectives. Research shows 5-7 is the sweet spot for committee size.

### Q: Why not use embeddings for deduplication?
A: Cost-benefit tradeoff. Simple heuristics work well for 30-40 questions.

### Q: How much does it cost compared to M1-M4?
A: ~15x per call, but generates better quality. For bulk users, caching brings it back to ~5x.

### Q: What if an agent times out?
A: ForumEngine uses remaining agents' proposals. Quality degrades gracefully.

### Q: Can I customize agent roles?
A: Yes, via configuration. You can enable/disable agents per mode.

---

## References

- **Full Analysis**: See `BETTAFISH_ANALYSIS.md`
- **BettaFish Project**: https://github.com/666ghj/BettaFish
- **Related Work**: Chain-of-Thought prompting, Multi-Agent Debate
