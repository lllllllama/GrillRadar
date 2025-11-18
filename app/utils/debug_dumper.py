"""
Debug Dumper - Saves multi-agent artifacts for debugging

When GRILLRADAR_DEBUG_AGENTS=1, this module saves intermediate
artifacts to help iterate on agent prompts and selection logic.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.config.settings import settings
from app.agents.models import DraftQuestion, AgentOutput, AgentState
from app.core.forum_engine import EnrichedDraftQuestion

logger = logging.getLogger(__name__)


class DebugDumper:
    """
    Debug artifact dumper for multi-agent workflow

    Saves intermediate artifacts to debug/ directory:
    - Each agent's raw DraftQuestions
    - ForumEngine pre-selection candidate set
    - Final selected questions
    - Advocate's feedback
    """

    def __init__(self, enabled: Optional[bool] = None):
        """
        Initialize debug dumper

        Args:
            enabled: Override default enabled state (from settings.GRILLRADAR_DEBUG_AGENTS)
        """
        self.enabled = enabled if enabled is not None else settings.GRILLRADAR_DEBUG_AGENTS
        self.debug_dir = settings.DEBUG_DIR
        self.session_dir: Optional[Path] = None

        if self.enabled:
            self._setup_debug_dir()

    def _setup_debug_dir(self):
        """Create debug directory structure"""
        try:
            self.debug_dir.mkdir(parents=True, exist_ok=True)

            # Create session-specific directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_dir = self.debug_dir / f"session_{timestamp}"
            self.session_dir.mkdir(exist_ok=True)

            logger.info(f"Debug artifacts will be saved to: {self.session_dir}")
        except Exception as e:
            logger.warning(f"Failed to create debug directory: {e}")
            self.enabled = False

    def dump_agent_output(
        self,
        agent_name: str,
        questions: List[DraftQuestion],
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Dump individual agent's output

        Args:
            agent_name: Agent identifier
            questions: Draft questions from agent
            success: Whether agent succeeded
            error: Error message if failed
        """
        if not self.enabled or not self.session_dir:
            return

        try:
            output_data = {
                "agent_name": agent_name,
                "success": success,
                "error": error,
                "question_count": len(questions),
                "questions": [
                    {
                        "question": q.question,
                        "rationale": q.rationale,
                        "role_name": q.role_name,
                        "role_display": q.role_display,
                        "tags": q.tags,
                        "confidence": q.confidence,
                        "metadata": q.metadata
                    }
                    for q in questions
                ]
            }

            filename = self.session_dir / f"{agent_name}_output.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Dumped {agent_name} output to {filename}")

        except Exception as e:
            logger.warning(f"Failed to dump agent output for {agent_name}: {e}")

    def dump_pre_selection_candidates(
        self,
        enriched_questions: List[EnrichedDraftQuestion]
    ):
        """
        Dump pre-selection candidate set with scores

        Args:
            enriched_questions: Enriched draft questions before final selection
        """
        if not self.enabled or not self.session_dir:
            return

        try:
            candidates_data = {
                "total_candidates": len(enriched_questions),
                "candidates": [
                    {
                        "question": eq.draft.question,
                        "rationale": eq.draft.rationale,
                        "agent_name": eq.agent_name,
                        "dimension": eq.dimension,
                        "difficulty": eq.difficulty,
                        "score": eq.score,
                        "tags": eq.draft.tags,
                        "confidence": eq.draft.confidence
                    }
                    for eq in enriched_questions
                ]
            }

            filename = self.session_dir / "pre_selection_candidates.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(candidates_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Dumped pre-selection candidates to {filename}")

        except Exception as e:
            logger.warning(f"Failed to dump pre-selection candidates: {e}")

    def dump_selected_questions(
        self,
        selected: List[EnrichedDraftQuestion]
    ):
        """
        Dump final selected questions

        Args:
            selected: Final selected questions
        """
        if not self.enabled or not self.session_dir:
            return

        try:
            selected_data = {
                "total_selected": len(selected),
                "selected": [
                    {
                        "question": eq.draft.question,
                        "rationale": eq.draft.rationale,
                        "agent_name": eq.agent_name,
                        "dimension": eq.dimension,
                        "difficulty": eq.difficulty,
                        "score": eq.score,
                        "tags": eq.draft.tags
                    }
                    for eq in selected
                ]
            }

            filename = self.session_dir / "final_selected.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(selected_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Dumped final selected questions to {filename}")

        except Exception as e:
            logger.warning(f"Failed to dump selected questions: {e}")

    def dump_advocate_feedback(
        self,
        before_count: int,
        after_count: int,
        filtered_questions: List[str]
    ):
        """
        Dump advocate's filtering feedback

        Args:
            before_count: Number of questions before advocate review
            after_count: Number of questions after advocate review
            filtered_questions: List of filtered question texts
        """
        if not self.enabled or not self.session_dir:
            return

        try:
            feedback_data = {
                "before_count": before_count,
                "after_count": after_count,
                "filtered_count": before_count - after_count,
                "filtered_questions": filtered_questions
            }

            filename = self.session_dir / "advocate_feedback.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Dumped advocate feedback to {filename}")

        except Exception as e:
            logger.warning(f"Failed to dump advocate feedback: {e}")

    def dump_workflow_summary(
        self,
        state: AgentState
    ):
        """
        Dump overall workflow summary

        Args:
            state: Agent workflow state
        """
        if not self.enabled or not self.session_dir:
            return

        try:
            summary_data = {
                "workflow_id": state.workflow_id,
                "timestamp": state.timestamp.isoformat(),
                "mode": state.mode,
                "total_llm_calls": state.total_llm_calls,
                "total_tokens": state.total_tokens,
                "total_cost_estimate": state.total_cost_estimate,
                "final_question_count": state.final_question_count,
                "errors": state.errors,
                "proposal_latencies": state.proposal_latencies
            }

            filename = self.session_dir / "workflow_summary.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Debug artifacts saved to: {self.session_dir}")

        except Exception as e:
            logger.warning(f"Failed to dump workflow summary: {e}")


# Global singleton instance
_debug_dumper: Optional[DebugDumper] = None


def get_debug_dumper() -> DebugDumper:
    """Get or create global debug dumper instance"""
    global _debug_dumper
    if _debug_dumper is None:
        _debug_dumper = DebugDumper()
    return _debug_dumper
