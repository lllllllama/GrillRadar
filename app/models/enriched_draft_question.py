"""
Enriched Draft Question Model

This model wraps a DraftQuestion with additional metadata for scoring and selection.
"""
from app.models.draft_question import DraftQuestion


class EnrichedDraftQuestion:
    """Draft question with enhanced metadata for selection"""

    def __init__(
        self,
        draft: DraftQuestion,
        agent_name: str,
        dimension: str,
        difficulty: str,
        score: float
    ):
        """
        Initialize enriched draft question

        Args:
            draft: Original draft question from agent
            agent_name: Name of the agent that proposed this question
            dimension: Question dimension (foundation, engineering, project_depth, etc.)
            difficulty: Question difficulty (basic, intermediate, killer)
            score: Relevance score (1.0-5.0)
        """
        self.draft = draft
        self.agent_name = agent_name
        self.dimension = dimension
        self.difficulty = difficulty
        self.score = score
