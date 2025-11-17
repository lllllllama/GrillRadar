# BettaFish Multi-Agent Architecture Analysis for GrillRadar

## Executive Summary

The GrillRadar project is designed to evolve from a single-prompt LLM system (Milestones 1-4) to a sophisticated **BettaFish-style multi-agent architecture** (Milestone 5). BettaFish is a reference implementation for building multi-agent systems where independent agents collaborate through orchestrated workflows.

---

## 1. MULTI-AGENT ARCHITECTURE OVERVIEW

### 1.1 Current State (Milestones 1-4): Single LLM Call
The current MVP uses a "Virtual Committee" pattern simulated via a single LLM call:
```python
# app/core/report_generator.py
class ReportGenerator:
    def generate_report(self, user_config: UserConfig) -> Report:
        # Single LLM call with multi-role prompt simulation
        system_prompt = self.prompt_builder.build(user_config)
        report_data = self.llm_client.call_json(system_prompt)
        return Report(**report_data)
```

**Limitations:**
- All 6 roles evaluated simultaneously in one prompt
- No iterative refinement or discussion between roles
- Less coherent cross-role analysis
- Cost-efficient but limited quality for complex cases

### 1.2 Target State (Milestone 5): True Multi-Agent Architecture

**Architecture Pattern:** ForumEngine-based agent orchestration

```python
# Planned: app/core/agent_orchestrator.py
class AgentOrchestrator:
    def __init__(self):
        self.technical = TechnicalInterviewerAgent()
        self.hiring_manager = HiringManagerAgent()
        self.hr = HRAgent()
        self.advisor = AdvisorAgent()
        self.reviewer = ReviewerAgent()
        self.advocate = AdvocateAgent()
        self.forum_engine = ForumEngine()
        self.report_agent = ReportAgent()

    async def generate_report(self, user_config, resume_text):
        # 1. Parallel agent proposals
        draft_questions = await asyncio.gather(
            self.technical.propose_questions(resume_text, user_config),
            self.hiring_manager.propose_questions(resume_text, user_config),
            self.hr.propose_questions(resume_text, user_config),
            self.advisor.propose_questions(resume_text, user_config),
            self.reviewer.propose_questions(resume_text, user_config),
            self.advocate.propose_questions(resume_text, user_config)
        )
        
        # 2. Forum-based discussion and filtering
        final_questions = self.forum_engine.discuss(
            draft_questions, 
            resume_text, 
            user_config
        )
        
        # 3. Final report generation
        return self.report_agent.generate(final_questions, user_config)
```

---

## 2. AGENT COMMUNICATION & COORDINATION PATTERNS

### 2.1 Six Core Agents

| Agent | Responsibility | Input | Output | Skills |
|-------|-----------------|-------|--------|--------|
| **TechnicalInterviewerAgent** | CS fundamentals, system design, technical depth | Resume, config | 3-5 tech questions | Algorithm, architecture knowledge |
| **HiringManagerAgent** | Role fit, business understanding, impact | Resume, JD | 3-5 business questions | Domain expertise, career mapping |
| **HRAgent** | Soft skills, values, teamwork | Resume, culture | 2-3 behavioral questions | Communication, culture assessment |
| **AdvisorAgent** | Research ability, academic potential | Resume, research exp | 3-5 research questions | Domain science knowledge |
| **ReviewerAgent** | Paper reading, methodology, academic rigor | Resume, publications | 3-5 academic questions | Methodology assessment |
| **AdvocateAgent** | Quality control, fairness | All questions | Flags/feedback | Meta-evaluation |

### 2.2 Communication Flow: ForumEngine Model

```
┌─────────────────────────────────────────────────────────┐
│ Input: Resume + UserConfig + Domain Config              │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │ PHASE 1: Parallel Proposals    │
        │ (Each agent LLM call)          │
        └────────────────┬────────────────┘
                         │
    ┌────────┬───────┬──────┬────────┬───────┬──────────┐
    │        │       │      │        │       │          │
  Tech    Hiring   HR    Advisor  Reviewer Advocate   (6 LLM calls)
  [3-5]   [3-5]  [2-3]  [3-5]     [3-5]   [2-3]
    │        │       │      │        │       │          │
    └────────┴───────┴──────┴────────┴───────┴──────────┘
                         │
        ┌────────────────▼────────────────┐
        │ PHASE 2: Forum Discussion      │
        │ (Orchestrator consolidates)    │
        └────────────────┬────────────────┘
                         │
    ┌─── Merge similar questions
    ├─── Remove low-quality/offensive questions
    ├─── Validate coherence
    ├─── Check coverage (breadth + depth)
    └─── Advocate flags unfair questions
                         │
        ┌────────────────▼────────────────┐
        │ PHASE 3: Select Final Set      │
        │ (10-20 questions)              │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │ PHASE 4: ReportAgent Generation│
        │ (Final LLM call for reporting) │
        └────────────────┬────────────────┘
                         │
    ┌─────────────────────────────────────────────────────┐
    │ Output: Final Report (JSON + Markdown)              │
    └─────────────────────────────────────────────────────┘
```

### 2.3 Agent Input/Output Contracts

Each agent follows a standard interface:

```python
# Planned: app/agents/base_agent.py
class BaseAgent(ABC):
    @abstractmethod
    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """
        Generate initial questions from this agent's perspective.
        
        Returns:
            List of draft questions with preliminary reasoning
        """
        pass

class DraftQuestion(BaseModel):
    """Intermediate format before consolidation"""
    question: str
    rationale: str
    expected_tags: List[str]
    role_name: str
    confidence: float  # 0.0-1.0 confidence in relevance
    quality_signal: Dict[str, Any]  # Technical depth, relevance score, etc.
```

---

## 3. CODE STRUCTURE & IMPLEMENTATION BLUEPRINT

### 3.1 Proposed Directory Structure

```
app/
├── agents/                          # NEW: Multi-agent modules
│   ├── __init__.py
│   ├── base_agent.py               # Abstract base class
│   ├── technical_interviewer.py    # TechnicalInterviewerAgent
│   ├── hiring_manager.py            # HiringManagerAgent
│   ├── hr_agent.py                  # HRAgent
│   ├── advisor_agent.py             # AdvisorAgent
│   ├── reviewer_agent.py            # ReviewerAgent
│   ├── advocate_agent.py            # AdvocateAgent
│   ├── report_agent.py              # ReportAgent
│   ├── models.py                    # DraftQuestion, AgentOutput
│   └── tools/                       # Shared tools (resumeparser, etc.)
│       ├── resume_parser.py
│       ├── domain_matcher.py
│       └── question_validator.py
│
├── core/
│   ├── llm_client.py                # (Keep as-is)
│   ├── prompt_builder.py            # (Keep agent prompt templates here)
│   ├── report_generator.py          # (Refactor to delegate to orchestrator)
│   ├── agent_orchestrator.py        # NEW: Main orchestration logic
│   └── forum_engine.py              # NEW: Discussion & filtering logic
│
├── api/
│   ├── report.py                    # (Existing routes)
│   └── agents.py                    # NEW: Agent status/debug endpoints
│
├── models/
│   ├── report.py                    # (Keep as-is)
│   ├── user_config.py               # (Keep as-is)
│   └── agent_state.py               # NEW: Track agent execution state
│
└── retrieval/
    └── info_aggregator.py           # (Keep as-is)
```

### 3.2 Key Implementation Classes

#### BaseAgent (Abstract)

```python
# app/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio

class AgentConfig(BaseModel):
    name: str
    role_description: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30

class DraftQuestion(BaseModel):
    question: str
    rationale: str
    role_name: str
    role_display: str
    tags: List[str] = []
    confidence: float  # Quality signal (0.0-1.0)
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, llm_client):
        self.config = config
        self.llm_client = llm_client
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """Generate initial questions from this agent's perspective."""
        pass

    def _build_prompt(self, resume_text: str, user_config: UserConfig) -> str:
        """Build role-specific prompt template."""
        # Override in subclasses
        pass

    async def _call_llm_structured(self, prompt: str) -> Dict:
        """Call LLM and ensure structured JSON output."""
        # Retry logic, JSON parsing, validation
        pass
```

#### TechnicalInterviewerAgent (Concrete Example)

```python
# app/agents/technical_interviewer.py
class TechnicalInterviewerAgent(BaseAgent):
    def __init__(self, llm_client):
        config = AgentConfig(
            name="technical_interviewer",
            role_description="Evaluates CS fundamentals, system design, technical depth"
        )
        super().__init__(config, llm_client)

    async def propose_questions(
        self,
        resume_text: str,
        user_config: UserConfig,
        context: Optional[Dict] = None
    ) -> List[DraftQuestion]:
        """Generate 3-5 technical questions."""
        prompt = f"""
你是技术面试官角色。根据候选人简历和目标岗位，生成3-5个最想问的技术问题。

## 简历信息
{resume_text}

## 岗位信息
- 目标: {user_config.target_desc}
- 领域: {user_config.domain or '未指定'}
- 级别: {user_config.level or '未指定'}

## 你的任务
1. 识别简历中的技术深度信号（关键词、项目规模、技术栈）
2. 为每个问题生成明确的理由和预期答案框架
3. 优先考察：CS基础、系统设计、项目真实性、技术深度
4. 避免纯概念题，优先场景题和深度追问

## 输出格式（JSON）
{{
    "questions": [
        {{
            "question": "具体问题文本",
            "rationale": "为什么问这个问题，考察什么",
            "tags": ["标签1", "标签2"],
            "confidence": 0.85
        }}
    ]
}}
"""
        try:
            response = await self._call_llm_structured(prompt)
            draft_questions = []
            for q in response.get("questions", []):
                draft_questions.append(DraftQuestion(
                    question=q["question"],
                    rationale=q["rationale"],
                    role_name="technical_interviewer",
                    role_display="技术面试官",
                    tags=q.get("tags", []),
                    confidence=q.get("confidence", 0.8),
                    metadata={"raw_response": q}
                ))
            return draft_questions
        except Exception as e:
            self.logger.error(f"Failed to propose questions: {e}")
            return []
```

#### ForumEngine (Discussion & Consolidation)

```python
# app/core/forum_engine.py
class ForumEngine:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

    async def discuss(
        self,
        draft_questions_by_agent: Dict[str, List[DraftQuestion]],
        resume_text: str,
        user_config: UserConfig
    ) -> List[QuestionItem]:
        """
        Multi-round discussion to consolidate and refine questions.
        
        Steps:
        1. Merge similar questions
        2. Remove duplicates
        3. Validate quality
        4. Check coverage
        5. Apply advocate feedback
        """
        all_drafts = []
        for agent_name, drafts in draft_questions_by_agent.items():
            all_drafts.extend([(d, agent_name) for d in drafts])

        # Phase 1: Deduplication (semantic similarity)
        deduped = self._deduplicate_questions(all_drafts)

        # Phase 2: Quality filtering
        filtered = self._filter_low_quality(deduped)

        # Phase 3: Coverage validation
        coverage_checked = self._validate_coverage(filtered, user_config)

        # Phase 4: Enhance each question to final QuestionItem
        final_questions = await self._enhance_questions(
            coverage_checked,
            resume_text,
            user_config
        )

        return final_questions

    def _deduplicate_questions(self, drafts: List[tuple]) -> List[tuple]:
        """Remove semantically similar questions."""
        # Use embedding-based similarity or heuristic matching
        # Keep questions with highest confidence scores
        pass

    def _filter_low_quality(self, drafts: List[tuple]) -> List[tuple]:
        """
        Remove:
        - Pure concept questions (no resume connection)
        - Offensive or unfair questions
        - Questions below confidence threshold (< 0.6)
        """
        filtered = [
            d for d in drafts 
            if d[0].confidence >= 0.6 and self._is_fair(d[0])
        ]
        return filtered

    def _validate_coverage(self, drafts, config) -> List[tuple]:
        """Ensure coverage across question categories."""
        # Check: CS basics, projects, engineering/research, soft skills
        # If gaps exist, request additional questions
        pass

    async def _enhance_questions(self, drafts, resume_text, config) -> List[QuestionItem]:
        """
        Convert DraftQuestion -> QuestionItem (final format).
        Add: baseline_answer, support_notes, prompt_template
        """
        final_items = []
        for draft, agent_name in drafts:
            # Call enhancer LLM
            enhanced = await self._enhance_single_question(
                draft, agent_name, resume_text, config
            )
            final_items.append(enhanced)
        return final_items

    async def _enhance_single_question(
        self,
        draft: DraftQuestion,
        agent_name: str,
        resume_text: str,
        config: UserConfig
    ) -> QuestionItem:
        """Enhance draft question to final form."""
        prompt = f"""
基于以下初步问题，生成完整的问题卡片（QuestionItem）。

## 初步问题
问题: {draft.question}
理由: {draft.rationale}

## 候选人信息
{resume_text}

## 任务
为这个问题生成：
1. baseline_answer - 基准答案框架（回答结构、关键要点）
2. support_notes - 支撑材料（相关技术、论文、推荐阅读）
3. prompt_template - 练习提示词（含{{{{your_experience}}}}占位符）

## 输出格式（JSON）
{{
    "baseline_answer": "...",
    "support_notes": "...",
    "prompt_template": "...",
    "tag": "主题标签"
}}
"""
        response = await self.llm_client.call_json(prompt)
        
        return QuestionItem(
            id=0,  # Will be assigned by orchestrator
            view_role=draft.role_display,
            tag=response.get("tag", draft.tags[0] if draft.tags else "综合"),
            question=draft.question,
            rationale=draft.rationale,
            baseline_answer=response.get("baseline_answer", ""),
            support_notes=response.get("support_notes", ""),
            prompt_template=response.get("prompt_template", "")
        )
```

#### AgentOrchestrator (Main Coordinator)

```python
# app/core/agent_orchestrator.py
class AgentOrchestrator:
    def __init__(self, llm_client):
        self.technical = TechnicalInterviewerAgent(llm_client)
        self.hiring_manager = HiringManagerAgent(llm_client)
        self.hr = HRAgent(llm_client)
        self.advisor = AdvisorAgent(llm_client)
        self.reviewer = ReviewerAgent(llm_client)
        self.advocate = AdvocateAgent(llm_client)
        self.forum_engine = ForumEngine(llm_client)
        self.report_agent = ReportAgent(llm_client)
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

    async def generate_report(
        self,
        user_config: UserConfig
    ) -> Report:
        """
        Orchestrate multi-agent workflow to generate final report.
        """
        self.logger.info("Starting multi-agent orchestration")

        # Phase 1: Parallel agent proposals
        self.logger.info("Phase 1: Collecting agent proposals")
        draft_questions = await self._collect_proposals(user_config)

        # Phase 2: Forum discussion
        self.logger.info("Phase 2: Forum discussion and filtering")
        final_questions = await self.forum_engine.discuss(
            draft_questions,
            user_config.resume_text,
            user_config
        )

        # Phase 3: Generate final report
        self.logger.info("Phase 3: Generating final report")
        report = await self.report_agent.generate(
            final_questions,
            user_config
        )

        return report

    async def _collect_proposals(self, user_config: UserConfig) -> Dict:
        """Collect proposals from all agents in parallel."""
        results = await asyncio.gather(
            self.technical.propose_questions(user_config.resume_text, user_config),
            self.hiring_manager.propose_questions(user_config.resume_text, user_config),
            self.hr.propose_questions(user_config.resume_text, user_config),
            self.advisor.propose_questions(user_config.resume_text, user_config),
            self.reviewer.propose_questions(user_config.resume_text, user_config),
            self.advocate.propose_questions(user_config.resume_text, user_config),
            return_exceptions=True
        )

        return {
            "technical_interviewer": results[0] if not isinstance(results[0], Exception) else [],
            "hiring_manager": results[1] if not isinstance(results[1], Exception) else [],
            "hr": results[2] if not isinstance(results[2], Exception) else [],
            "advisor": results[3] if not isinstance(results[3], Exception) else [],
            "reviewer": results[4] if not isinstance(results[4], Exception) else [],
            "advocate": results[5] if not isinstance(results[5], Exception) else [],
        }
```

---

## 4. STATE MANAGEMENT ACROSS AGENTS

### 4.1 State Flow Architecture

```python
# app/models/agent_state.py
class AgentState(BaseModel):
    """Tracks execution state across multi-agent workflow."""
    
    workflow_id: str  # Unique identifier for this generation run
    timestamp: datetime
    
    # Phase 1: Proposal state
    proposals: Dict[str, List[DraftQuestion]] = {}
    proposal_errors: Dict[str, str] = {}
    proposal_latencies: Dict[str, float] = {}
    
    # Phase 2: Forum discussion state
    merged_questions: List[DraftQuestion] = []
    filtered_questions: List[DraftQuestion] = []
    quality_issues: List[str] = []
    coverage_gaps: List[str] = []
    
    # Phase 3: Final report state
    final_questions: List[QuestionItem] = []
    report_meta: Dict[str, Any] = {}
    
    # Debug/monitoring
    total_llm_calls: int = 0
    total_cost_estimate: float = 0.0
    errors: List[str] = []

class WorkflowContext:
    """Passed between agents to maintain state."""
    
    def __init__(self, user_config: UserConfig, resume_text: str):
        self.state = AgentState(workflow_id=str(uuid.uuid4()))
        self.user_config = user_config
        self.resume_text = resume_text
        self.config_cache = {}  # Domain, mode configs
        
    def record_proposal(self, agent_name: str, questions: List[DraftQuestion]):
        self.state.proposals[agent_name] = questions
        
    def record_error(self, agent_name: str, error: str):
        self.state.proposal_errors[agent_name] = error
        self.state.errors.append(error)
```

### 4.2 State Persistence (Optional)

For longer workflows or debugging:

```python
# app/core/state_manager.py
class StateManager:
    """Persist agent state for debugging and auditing."""
    
    async def save_state(self, context: WorkflowContext):
        """Save intermediate state to database or file."""
        # Useful for:
        # - Debugging multi-agent interactions
        # - Auditing decision-making
        # - Analyzing agent behavior patterns
        # - Cost tracking
        pass
    
    async def load_state(self, workflow_id: str) -> WorkflowContext:
        """Retrieve saved state."""
        pass
```

---

## 5. ERROR HANDLING IN DISTRIBUTED CONTEXT

### 5.1 Failure Modes & Mitigations

| Failure Mode | Impact | Mitigation |
|-------------|--------|-----------|
| Agent timeout | Incomplete proposals | Async timeout + fallback to cached defaults |
| LLM API error | Agent cannot generate | Retry with exponential backoff; skip agent |
| Malformed JSON | Parsing fails | JSON schema validation; human review |
| Quality issues | Poor questions generated | Advocate agent review + threshold filtering |
| Coverage gaps | Missing question categories | ForumEngine detects; request additional |
| Cost overrun | Expensive operation | Token counting; agent parallelization |

### 5.2 Resilience Patterns

```python
# app/agents/resilience.py
class AgentResilience:
    """Patterns for handling agent failures."""
    
    @staticmethod
    async def call_with_retry(
        coro,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        timeout: int = 30
    ):
        """Retry with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(backoff_factor ** attempt)
    
    @staticmethod
    async def call_with_fallback(
        primary_coro,
        fallback_coro,
        timeout: int = 30
    ):
        """Use fallback if primary fails."""
        try:
            return await asyncio.wait_for(primary_coro, timeout=timeout)
        except (asyncio.TimeoutError, Exception):
            return await fallback_coro

class CircuitBreaker:
    """Prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, coro):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker open")
        
        try:
            result = await coro
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### 5.3 Error Recovery Strategy

```python
# Graceful degradation
async def generate_report(orchestrator: AgentOrchestrator, config: UserConfig):
    try:
        # Full multi-agent flow
        return await orchestrator.generate_report(config)
    except Exception as e:
        logger.error(f"Multi-agent generation failed: {e}")
        
        # Fallback 1: Use cached model from previous runs
        cached = await cache_manager.get_recent_report(config.target_desc)
        if cached:
            logger.info("Returning cached report")
            return cached
        
        # Fallback 2: Use single-LLM approach (pre-Milestone 5)
        logger.info("Falling back to single-LLM generation")
        fallback_generator = ReportGenerator()
        return fallback_generator.generate_report(config)
```

---

## 6. AGENT SPECIALIZATION: ROLES & RESPONSIBILITIES

### 6.1 Six-Role Committee Design

#### 1. **TechnicalInterviewerAgent**
- **Focus:** CS fundamentals, system design, technical depth
- **Evaluation Criteria:**
  - Algorithm and data structure knowledge
  - System design thinking
  - Project technical depth
  - Problem-solving approach
- **Question Types:**
  - Design questions: "Design X system for Y constraints"
  - Depth questions: "Explain the internals of technology X"
  - Trade-off questions: "When would you choose A over B?"
- **Domain Knowledge:** Backend, frontend, algorithms, ML systems
- **Confidence Signals:**
  - Explicitly mentioned technical keywords in resume
  - Project scale indicators
  - Language/framework proficiency

#### 2. **HiringManagerAgent**
- **Focus:** Role fit, business impact, career trajectory
- **Evaluation Criteria:**
  - Alignment with job description
  - Business impact of past projects
  - Growth mindset and career progression
  - Communication and presentation skills
- **Question Types:**
  - Motivation: "Why are you interested in this role?"
  - Impact: "What was the business impact of X?"
  - Growth: "What skill do you want to develop?"
- **Domain Knowledge:** Role requirements, industry trends, business metrics
- **Confidence Signals:**
  - Explicit role/company mentions in resume
  - Quantified impact metrics
  - Career progression patterns

#### 3. **HRAgent**
- **Focus:** Soft skills, cultural fit, teamwork
- **Evaluation Criteria:**
  - Communication and collaboration
  - Leadership and initiative
  - Conflict resolution
  - Value alignment
- **Question Types:**
  - Behavioral: "Tell me about a time when..."
  - Values: "How do you handle disagreement?"
  - Culture: "Describe your ideal team dynamic"
- **Domain Knowledge:** Soft skills assessment, STAR method, company culture
- **Confidence Signals:**
  - Team project indicators
  - Leadership roles
  - Volunteer/community involvement

#### 4. **AdvisorAgent** (for grad/research mode)
- **Focus:** Research potential, academic trajectory, depth
- **Evaluation Criteria:**
  - Research interest and clarity
  - Problem formulation ability
  - Experimental thinking
  - Collaboration in research
- **Question Types:**
  - Research design: "How would you approach studying X?"
  - Depth: "What's the frontier in your field?"
  - Methodology: "How would you validate your hypothesis?"
- **Domain Knowledge:** Research methodology, domain-specific knowledge
- **Confidence Signals:**
  - Research experience, publications
  - Projects with research components
  - Academic collaborations

#### 5. **ReviewerAgent** (for research/grad)
- **Focus:** Paper reading, methodology rigor, academic standards
- **Evaluation Criteria:**
  - Literature understanding
  - Experimental design
  - Statistical rigor
  - Academic writing quality
- **Question Types:**
  - Paper analysis: "Describe the key contributions of X paper"
  - Methodology: "What are the weaknesses in this experiment?"
  - Standards: "How do you ensure research integrity?"
- **Domain Knowledge:** Research standards, literature, methodologies
- **Confidence Signals:**
  - Publication records
  - Paper citations
  - Methodology descriptions

#### 6. **AdvocateAgent**
- **Focus:** Quality control, fairness, ethical evaluation
- **Evaluation Criteria:**
  - Question fairness
  - Relevance to resume
  - Avoiding stereotypes
  - Opportunity for demonstration
- **Question Types:**
  - Meta-evaluation: "Is this question fair?"
  - Flags: "This question might be biased because..."
  - Suggestions: "This question could be improved by..."
- **Domain Knowledge:** Bias detection, fairness metrics, ethics
- **Confidence Signals:**
  - Inconsistency with other questions
  - Lack of evidence in resume
  - Culturally specific assumptions

### 6.2 Role Weight Distribution (Configurable)

**Job Mode** (工程求职):
```yaml
technical_interviewer: 40%  # Primary focus
hiring_manager: 30%
hr: 20%
advisor: 5%
reviewer: 5%
```

**Grad Mode** (学术/读研):
```yaml
advisor: 40%               # Primary focus
reviewer: 30%
technical_interviewer: 15%
hr: 10%
hiring_manager: 5%
```

**Mixed Mode** (工程+学术):
```yaml
technical_interviewer: 30%
advisor: 30%               # Equal weight
reviewer: 20%
hiring_manager: 15%
hr: 5%
```

---

## 7. TESTING MULTI-AGENT SYSTEMS

### 7.1 Testing Strategy

```python
# tests/test_agents/
├── __init__.py
├── test_base_agent.py        # Base class contract tests
├── test_technical_agent.py   # Agent-specific behavior
├── test_hiring_manager_agent.py
├── test_hr_agent.py
├── test_advisor_agent.py
├── test_reviewer_agent.py
├── test_advocate_agent.py
├── test_forum_engine.py      # Orchestration logic
├── test_agent_orchestrator.py # End-to-end workflows
├── test_resilience.py         # Error handling
└── fixtures/
    ├── sample_resumes.json
    ├── sample_configs.json
    └── expected_outputs.json
```

### 7.2 Unit Tests (Agent-Level)

```python
# tests/test_agents/test_technical_agent.py
import pytest
from app.agents.technical_interviewer import TechnicalInterviewerAgent
from app.models.user_config import UserConfig

@pytest.fixture
def technical_agent(mock_llm_client):
    return TechnicalInterviewerAgent(mock_llm_client)

@pytest.fixture
def sample_resume():
    return """
    经验：
    - 分布式爬虫系统 (Python, Redis, Kafka)
    - 微服务后端系统 (Go, MySQL, gRPC)
    """

@pytest.fixture
def sample_config():
    return UserConfig(
        mode="job",
        target_desc="字节跳动后端开发",
        domain="backend",
        level="junior",
        resume_text="..."
    )

def test_propose_questions_returns_list(technical_agent, sample_resume, sample_config):
    """Test that agent returns list of questions."""
    questions = await technical_agent.propose_questions(sample_resume, sample_config)
    assert isinstance(questions, list)
    assert len(questions) >= 3
    assert len(questions) <= 5

def test_question_format_valid(technical_agent, sample_resume, sample_config):
    """Test that each question follows DraftQuestion schema."""
    questions = await technical_agent.propose_questions(sample_resume, sample_config)
    for q in questions:
        assert isinstance(q.question, str)
        assert len(q.question) >= 10
        assert hasattr(q, 'rationale')
        assert hasattr(q, 'confidence')
        assert 0.0 <= q.confidence <= 1.0

def test_question_relevance_to_resume(technical_agent, sample_resume, sample_config):
    """Test that questions reference resume content."""
    questions = await technical_agent.propose_questions(sample_resume, sample_config)
    resume_keywords = ["分布式", "爬虫", "缓存", "微服务"]
    
    for q in questions:
        # At least one keyword should appear in question or rationale
        is_relevant = any(
            keyword in q.question or keyword in q.rationale
            for keyword in resume_keywords
        )
        assert is_relevant, f"Question not relevant: {q.question}"

@pytest.mark.asyncio
async def test_timeout_handling(technical_agent, sample_resume, sample_config, monkeypatch):
    """Test that agent handles LLM timeout gracefully."""
    async def timeout_coro(*args, **kwargs):
        await asyncio.sleep(10)  # Exceed timeout
    
    monkeypatch.setattr(technical_agent.llm_client, "call_json", timeout_coro)
    
    with pytest.raises(asyncio.TimeoutError):
        await technical_agent.propose_questions(sample_resume, sample_config)
```

### 7.3 Integration Tests (Multi-Agent)

```python
# tests/test_agents/test_agent_orchestrator.py
@pytest.mark.asyncio
async def test_orchestrator_full_workflow():
    """Test complete multi-agent workflow."""
    config = UserConfig(
        mode="job",
        target_desc="后端开发",
        resume_text="..."
    )
    
    orchestrator = AgentOrchestrator(mock_llm_client)
    report = await orchestrator.generate_report(config)
    
    # Validate report structure
    assert isinstance(report, Report)
    assert 10 <= len(report.questions) <= 20
    assert report.mode == "job"
    
    # Check role distribution
    role_counts = Counter(q.view_role for q in report.questions)
    assert role_counts["技术面试官"] >= 3  # Job mode: 40% -> ~6 questions

@pytest.mark.asyncio
async def test_forum_engine_deduplication():
    """Test that ForumEngine removes duplicate questions."""
    draft1 = DraftQuestion(
        question="讲一下你的分布式系统设计",
        rationale="考察系统设计能力",
        role_name="technical_interviewer",
        role_display="技术面试官",
        confidence=0.9
    )
    
    # Semantically similar question
    draft2 = DraftQuestion(
        question="你是如何设计分布式系统的",
        rationale="考察系统设计思维",
        role_name="hiring_manager",
        role_display="招聘经理",
        confidence=0.7
    )
    
    forum = ForumEngine(mock_llm_client)
    deduped = forum._deduplicate_questions([(draft1, "tech"), (draft2, "hiring")])
    
    # Should keep only one (the one with higher confidence)
    assert len(deduped) == 1
    assert deduped[0][0].confidence == 0.9

@pytest.mark.asyncio
async def test_advocate_agent_flags_unfair_questions():
    """Test that advocate agent identifies problematic questions."""
    unfair_questions = [
        "你是个女性，是否觉得在技术领域会受到歧视？",  # Stereotype
        "你的口音很重，这会影响表现吗？",  # Discrimination
        "你有没有朋友在我们公司工作？",  # Not resume-related
    ]
    
    advocate = AdvocateAgent(mock_llm_client)
    
    for q_text in unfair_questions:
        draft = DraftQuestion(question=q_text, ...)
        flags = advocate.evaluate_fairness(draft, resume_text)
        assert len(flags) > 0, f"Failed to flag: {q_text}"
```

### 7.4 Performance & Cost Tests

```python
# tests/test_agents/test_performance.py
@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_parallel_proposals_performance(benchmark):
    """Benchmark that parallelization improves performance."""
    config = UserConfig(...)
    orchestrator = AgentOrchestrator(mock_llm_client)
    
    # Measure time for parallel execution
    result = benchmark(
        lambda: asyncio.run(orchestrator._collect_proposals(config))
    )
    
    # Should complete in reasonable time (5-10 seconds for 6 agents)
    assert result.stats.mean < 10.0  # seconds

@pytest.mark.asyncio
async def test_estimated_cost_tracking():
    """Test that system tracks estimated LLM costs."""
    config = UserConfig(...)
    orchestrator = AgentOrchestrator(mock_llm_client)
    
    context = WorkflowContext(config, "resume...")
    await orchestrator.generate_report(config)
    
    # Each agent: ~1000 tokens prompt + 500 tokens response
    # 6 agents + forum + report = ~10 LLM calls
    # ~25k input tokens + 10k output tokens
    # Cost: 0.003 * 25 + 0.015 * 10 = ~$0.225
    estimated_cost = context.state.total_cost_estimate
    assert 0.15 < estimated_cost < 0.35  # Allow flexibility

def test_token_counting_accuracy():
    """Test accurate token counting for cost estimation."""
    from app.core.token_counter import count_tokens_approx
    
    text = "This is a sample text for token counting"
    estimated = count_tokens_approx(text)  # ~8 tokens
    
    assert 7 <= estimated <= 9
```

### 7.5 Mock/Fixture Strategy

```python
# tests/conftest.py
@pytest.fixture
def mock_llm_client():
    """Mock LLMClient for testing."""
    class MockLLMClient:
        async def call_json(self, prompt: str) -> Dict:
            # Return deterministic responses for testing
            if "technical_interviewer" in prompt:
                return {
                    "questions": [
                        {
                            "question": "Explain your distributed system design",
                            "rationale": "Test system design knowledge",
                            "tags": ["system_design"],
                            "confidence": 0.85
                        }
                    ]
                }
            # ... handle other cases
            return {"questions": []}
    
    return MockLLMClient()

@pytest.fixture
def sample_configs():
    """Load sample configurations for testing."""
    return {
        "job": UserConfig(mode="job", target_desc="后端开发", ...),
        "grad": UserConfig(mode="grad", target_desc="图像分割方向", ...),
        "mixed": UserConfig(mode="mixed", target_desc="后端+研究", ...),
    }

@pytest.fixture
def sample_resumes():
    """Load sample resumes for testing."""
    return {
        "backend": "后端开发经验...",
        "research": "研究经验...",
        "mixed": "同时有工程和研究经验...",
    }
```

### 7.6 End-to-End Smoke Tests

```python
# tests/test_e2e/test_full_pipeline.py
@pytest.mark.asyncio
@pytest.mark.slow
async def test_full_pipeline_job_mode():
    """E2E test: Complete workflow for job mode."""
    config = UserConfig(
        mode="job",
        target_desc="字节跳动后端工程师",
        domain="backend",
        level="junior",
        resume_text=SAMPLE_BACKEND_RESUME
    )
    
    orchestrator = AgentOrchestrator(LLMClient())  # Real LLM
    report = await orchestrator.generate_report(config)
    
    # Assertions
    assert report.mode == "job"
    assert len(report.questions) == 15  # ±2
    
    # Check question distribution
    roles = [q.view_role for q in report.questions]
    tech_count = sum(1 for r in roles if "技术" in r)
    assert tech_count >= 5  # ~40% for job mode
    
    # Check content quality
    for q in report.questions:
        assert len(q.baseline_answer) > 50
        assert len(q.support_notes) > 20
        assert "{your_experience}" in q.prompt_template

@pytest.mark.asyncio
@pytest.mark.slow
async def test_full_pipeline_grad_mode():
    """E2E test: Complete workflow for grad mode."""
    config = UserConfig(
        mode="grad",
        target_desc="清华大学计算机视觉方向硕士",
        domain="cv_segmentation",
        level="master",
        resume_text=SAMPLE_RESEARCH_RESUME
    )
    
    orchestrator = AgentOrchestrator(LLMClient())
    report = await orchestrator.generate_report(config)
    
    assert report.mode == "grad"
    assert len(report.questions) == 13  # ±2
    
    # Check advisor/reviewer dominance
    roles = [q.view_role for q in report.questions]
    advisor_reviewer = sum(1 for r in roles if "导师" in r or "评审" in r)
    assert advisor_reviewer >= 6  # ~70% for grad mode
```

---

## 8. EVOLUTION ROADMAP: FROM SINGLE-PROMPT TO MULTI-AGENT

### 8.1 Current State (M1-M4)

```python
# Single LLM call, all roles in one prompt
class ReportGenerator:
    def generate_report(self, config):
        prompt = PromptBuilder.build(config)  # 6 roles simulated
        response = LLMClient.call_json(prompt)  # 1 call
        return Report(**response)
```

**Advantages:** Simple, fast, cheap
**Disadvantages:** Less nuanced, no iteration, quality ceiling

### 8.2 Milestone 5: Multi-Agent Foundation

```python
# True multi-agent with synchronous orchestration
class AgentOrchestrator:
    async def generate_report(self, config):
        # Phase 1: Parallel proposals (6 agents, 6 calls)
        proposals = await asyncio.gather(...)
        
        # Phase 2: Forum discussion (1 call for consolidation)
        forum_result = ForumEngine.discuss(proposals)
        
        # Phase 3: Final report (1 call for enhancement)
        report = ReportAgent.generate(forum_result)
        
        return report
```

**Total calls:** 8 LLM calls
**Time:** ~15-30 seconds (parallel)
**Cost:** ~5x higher than M1-M4, justified by quality improvement

### 8.3 Future Enhancements (M6+)

1. **Multi-Round Discussion**
   - Agents argue and refine positions
   - ForumEngine enables debate
   - Higher quality but higher cost

2. **Adaptive Workflow**
   - Only activate agents relevant to domain
   - Skip agents with low confidence
   - Optimize cost vs. quality

3. **Caching & Reuse**
   - Cache agent responses for similar resumes
   - Reduce LLM calls by 50-70%
   - Improve performance

4. **Human-in-the-Loop**
   - Expert reviews intermediate results
   - Provides feedback for agent training
   - Hybrid human-AI workflow

---

## 9. KEY PATTERNS & BEST PRACTICES

### 9.1 Agent Design Patterns

1. **Specialization**: Each agent has a narrow, well-defined role
2. **Composability**: Agents can be combined in different configurations
3. **Observability**: Every agent logs decisions for debugging
4. **Resilience**: Graceful degradation on agent failures
5. **Testability**: Agents are unit-testable in isolation

### 9.2 Orchestration Patterns

1. **Fan-Out/Fan-In**: Parallel agent execution, then consolidation
2. **Circuit Breaker**: Prevent cascading failures
3. **Fallback**: Use defaults if agent fails
4. **Retry**: Exponential backoff for transient failures
5. **Timeout**: Prevent blocking on slow agents

### 9.3 Data Flow Patterns

1. **Immutable Messages**: Agents receive immutable inputs, produce outputs
2. **Versioning**: Track data versions for debugging
3. **Audit Trail**: Log all state transitions
4. **Serialization**: Use schemas (Pydantic) for type safety

---

## 10. IMPLEMENTATION PRIORITIES (for GrillRadar M5)

### Phase 1: Core Agents (Weeks 1-2)
- [ ] BaseAgent abstract class
- [ ] TechnicalInterviewerAgent
- [ ] HiringManagerAgent
- [ ] HRAgent
- [ ] AdvisorAgent
- [ ] ReviewerAgent
- [ ] AdvocateAgent

### Phase 2: Orchestration (Weeks 2-3)
- [ ] ForumEngine (deduplication, filtering, enhancement)
- [ ] AgentOrchestrator (main coordinator)
- [ ] State management (AgentState, WorkflowContext)
- [ ] Error handling & resilience

### Phase 3: Integration & Testing (Weeks 3-4)
- [ ] Unit tests for each agent
- [ ] Integration tests for multi-agent workflows
- [ ] Performance benchmarking
- [ ] Cost estimation and optimization

### Phase 4: Refinement & Deployment (Week 4+)
- [ ] API integration (existing report endpoints)
- [ ] Monitoring & observability
- [ ] Documentation
- [ ] Gradual rollout with A/B testing

---

## 11. REFERENCES & RELATED WORK

### Key Concepts
- **Multi-Agent Systems**: Coordination of independent agents toward common goals
- **ForumEngine**: BettaFish pattern for consensus-based decision making
- **Chain-of-Thought**: Intermediate reasoning steps improve LLM output quality
- **Prompt Composition**: Building complex prompts by combining templates

### Open Source Examples
- **LangChain**: Agent framework for LLM applications
- **AutoGPT**: Autonomous agent planning and execution
- **Multi-Agent Debate**: LLMs debating to improve output quality

### Papers
- "Large Language Models as Zero-Shot Planners" (Huang et al., 2023)
- "Multi-Agent Cooperation for Reasoning" (Li et al., 2023)
- "Constitutional AI" (Bai et al., 2022) - Principle-based oversight

---

## Conclusion

The evolution from GrillRadar's current single-prompt system (Milestones 1-4) to a BettaFish-style multi-agent architecture (Milestone 5) will significantly improve question quality through:

1. **Specialized Expertise**: Each agent becomes expert in its domain
2. **Collaborative Refinement**: ForumEngine enables cross-agent feedback
3. **Better Coverage**: Multiple perspectives ensure comprehensive evaluation
4. **Improved Fairness**: Advocate agent catches biased questions
5. **Scalability**: Modular design supports future enhancements

The implementation focuses on **clarity, reliability, and testability** to ensure the system is production-ready and maintainable.

