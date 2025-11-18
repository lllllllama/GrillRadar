"""
Draft Question Model

Intermediate format for questions proposed by agents before consolidation.
Moved from app/agents/models.py to centralize all core models.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class DraftQuestion(BaseModel):
    """
    Initial question proposal from an agent

    This is the intermediate format before consolidation
    into the final QuestionItem format.
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
