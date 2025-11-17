"""
Data models for multi-agent system

Defines the core data structures used for agent communication,
state tracking, and workflow management.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class DraftQuestion(BaseModel):
    """
    Initial question proposal from an agent

    This is the intermediate format before consolidation
    """
    question: str = Field(..., min_length=10, description="The question text")
    rationale: str = Field(..., min_length=20, description="Why ask this question")
    role_name: str = Field(..., description="Agent role identifier")
    role_display: str = Field(..., description="Human-readable role name")
    tags: List[str] = Field(default_factory=list, description="Question tags/categories")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent's confidence in relevance")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "请详细描述你在分布式系统项目中遇到的最大技术挑战是什么，如何解决的？",
                "rationale": "考察候选人对分布式系统实际问题的理解和解决能力",
                "role_name": "technical_interviewer",
                "role_display": "技术面试官",
                "tags": ["分布式系统", "问题解决"],
                "confidence": 0.85,
                "metadata": {"complexity": "high"}
            }
        }


class AgentOutput(BaseModel):
    """Output from a single agent"""
    agent_name: str
    agent_display_name: str
    questions: List[DraftQuestion]
    processing_time: float  # seconds
    success: bool
    error_message: Optional[str] = None
    llm_calls: int = 0
    tokens_used: int = 0


class AgentState(BaseModel):
    """
    Tracks execution state across multi-agent workflow

    Used for monitoring, debugging, and cost estimation
    """
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    mode: str = "job"  # job, grad, mixed

    # Phase 1: Proposal state
    proposals: Dict[str, List[DraftQuestion]] = Field(default_factory=dict)
    proposal_errors: Dict[str, str] = Field(default_factory=dict)
    proposal_latencies: Dict[str, float] = Field(default_factory=dict)

    # Phase 2: Forum discussion state
    merged_questions: List[DraftQuestion] = Field(default_factory=list)
    filtered_questions: List[DraftQuestion] = Field(default_factory=list)
    quality_issues: List[str] = Field(default_factory=list)
    coverage_gaps: List[str] = Field(default_factory=list)

    # Phase 3: Final report state
    final_question_count: int = 0
    report_generated: bool = False

    # Debug/monitoring
    total_llm_calls: int = 0
    total_tokens: int = 0
    total_cost_estimate: float = 0.0
    errors: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "mode": "job",
                "total_llm_calls": 8,
                "total_tokens": 25000,
                "total_cost_estimate": 0.225
            }
        }


class WorkflowContext:
    """
    Context passed between agents to maintain state

    This class wraps the mutable AgentState and provides
    utility methods for state management.
    """

    def __init__(self, user_config, resume_text: str):
        self.state = AgentState(mode=user_config.mode)
        self.user_config = user_config
        self.resume_text = resume_text
        self.config_cache: Dict[str, Any] = {}  # Domain, mode configs

    def record_proposal(self, agent_name: str, questions: List[DraftQuestion], latency: float = 0.0):
        """Record agent proposals"""
        self.state.proposals[agent_name] = questions
        self.state.proposal_latencies[agent_name] = latency

    def record_error(self, agent_name: str, error: str):
        """Record agent error"""
        self.state.proposal_errors[agent_name] = error
        self.state.errors.append(f"{agent_name}: {error}")

    def record_llm_call(self, tokens: int = 0, cost: float = 0.0):
        """Record LLM call for tracking"""
        self.state.total_llm_calls += 1
        self.state.total_tokens += tokens
        self.state.total_cost_estimate += cost

    def get_summary(self) -> Dict[str, Any]:
        """Get workflow summary"""
        return {
            "workflow_id": self.state.workflow_id,
            "mode": self.state.mode,
            "agents_called": len(self.state.proposals),
            "total_questions_proposed": sum(len(q) for q in self.state.proposals.values()),
            "errors": len(self.state.errors),
            "llm_calls": self.state.total_llm_calls,
            "estimated_cost": f"${self.state.total_cost_estimate:.3f}"
        }
