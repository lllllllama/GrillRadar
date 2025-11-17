"""Tests for multi-agent system"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.base_agent import BaseAgent, AgentConfig
from app.agents.models import DraftQuestion, AgentState, WorkflowContext
from app.agents.technical_interviewer import TechnicalInterviewerAgent
from app.agents.hiring_manager import HiringManagerAgent
from app.agents.hr_agent import HRAgent
from app.agents.advisor_agent import AdvisorAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.advocate_agent import AdvocateAgent
from app.models.user_config import UserConfig


class TestAgentConfig:
    """Tests for AgentConfig model"""

    def test_agent_config_creation(self):
        """Test basic agent config creation"""
        config = AgentConfig(
            name="test_agent",
            display_name="Test Agent",
            role_description="Test role"
        )

        assert config.name == "test_agent"
        assert config.display_name == "Test Agent"
        assert config.temperature == 0.7  # Default
        assert config.max_tokens == 2000  # Default
        assert config.min_questions == 2  # Default

    def test_agent_config_custom_values(self):
        """Test agent config with custom values"""
        config = AgentConfig(
            name="custom_agent",
            display_name="Custom Agent",
            role_description="Custom role",
            temperature=0.5,
            max_tokens=3000,
            min_questions=3,
            max_questions=10
        )

        assert config.temperature == 0.5
        assert config.max_tokens == 3000
        assert config.min_questions == 3
        assert config.max_questions == 10


class TestDraftQuestion:
    """Tests for DraftQuestion model"""

    def test_draft_question_creation(self):
        """Test basic draft question creation"""
        draft = DraftQuestion(
            question="Test question?",
            rationale="Test rationale for this question",
            role_name="test_agent",
            role_display="Test Agent",
            tags=["test"],
            confidence=0.85
        )

        assert draft.question == "Test question?"
        assert draft.rationale == "Test rationale for this question"
        assert draft.confidence == 0.85
        assert "test" in draft.tags

    def test_draft_question_validation_min_length(self):
        """Test question validation for minimum length"""
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            DraftQuestion(
                question="Too short",  # Less than 10 chars
                rationale="Valid rationale here",
                role_name="test",
                role_display="Test",
                confidence=0.8
            )

    def test_draft_question_confidence_range(self):
        """Test confidence must be between 0 and 1"""
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            DraftQuestion(
                question="Valid question here?",
                rationale="Valid rationale here",
                role_name="test",
                role_display="Test",
                confidence=1.5  # Invalid
            )


class TestAgentState:
    """Tests for AgentState model"""

    def test_agent_state_initialization(self):
        """Test agent state initialization"""
        state = AgentState(mode="job")

        assert state.mode == "job"
        assert len(state.proposals) == 0
        assert state.total_llm_calls == 0
        assert state.total_cost_estimate == 0.0
        assert state.workflow_id  # Should have a UUID

    def test_agent_state_tracks_proposals(self):
        """Test agent state tracks proposals"""
        state = AgentState(mode="job")

        draft = DraftQuestion(
            question="Test question?",
            rationale="This is a valid test rationale with sufficient length",
            role_name="test",
            role_display="Test",
            confidence=0.8
        )

        state.proposals["test_agent"] = [draft]

        assert len(state.proposals) == 1
        assert "test_agent" in state.proposals


class TestWorkflowContext:
    """Tests for WorkflowContext"""

    def test_workflow_context_initialization(self):
        """Test workflow context initialization"""
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        context = WorkflowContext(user_config, "Test resume")

        assert context.user_config == user_config
        assert context.resume_text == "Test resume"
        assert context.state.mode == "job"

    def test_workflow_context_record_proposal(self):
        """Test recording proposals"""
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )
        context = WorkflowContext(user_config, "Test resume")

        draft = DraftQuestion(
            question="Test question?",
            rationale="This is a valid test rationale with sufficient length",
            role_name="test",
            role_display="Test",
            confidence=0.8
        )

        context.record_proposal("test_agent", [draft], latency=1.5)

        assert "test_agent" in context.state.proposals
        assert context.state.proposal_latencies["test_agent"] == 1.5

    def test_workflow_context_record_error(self):
        """Test recording errors"""
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )
        context = WorkflowContext(user_config, "Test resume")

        context.record_error("test_agent", "Test error")

        assert "test_agent" in context.state.proposal_errors
        assert len(context.state.errors) == 1

    def test_workflow_context_record_llm_call(self):
        """Test recording LLM calls"""
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )
        context = WorkflowContext(user_config, "Test resume")

        context.record_llm_call(tokens=1000, cost=0.05)
        context.record_llm_call(tokens=2000, cost=0.10)

        assert context.state.total_llm_calls == 2
        assert context.state.total_tokens == 3000
        assert abs(context.state.total_cost_estimate - 0.15) < 0.001  # Floating point comparison


class TestTechnicalInterviewerAgent:
    """Tests for TechnicalInterviewerAgent"""

    def test_technical_agent_initialization(self):
        """Test technical agent initialization"""
        mock_llm = Mock()
        agent = TechnicalInterviewerAgent(mock_llm)

        assert agent.config.name == "technical_interviewer"
        assert agent.config.display_name == "技术面试官"
        assert agent.llm_client == mock_llm

    @pytest.mark.asyncio
    async def test_technical_agent_propose_questions_success(self):
        """Test technical agent proposes questions successfully"""
        mock_llm = Mock()
        mock_llm.call_json = AsyncMock(return_value={
            "questions": [
                {
                    "question": "请描述你在分布式系统项目中遇到的最大技术挑战是什么？",
                    "rationale": "考察候选人对分布式系统的深入理解和实践能力",
                    "tags": ["分布式系统", "问题解决"],
                    "confidence": 0.85,
                    "complexity": "high"
                }
            ]
        })

        agent = TechnicalInterviewerAgent(mock_llm)
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        questions = await agent.propose_questions("Test resume", user_config)

        assert len(questions) > 0
        assert isinstance(questions[0], DraftQuestion)
        assert questions[0].role_name == "technical_interviewer"


class TestHiringManagerAgent:
    """Tests for HiringManagerAgent"""

    def test_hiring_manager_initialization(self):
        """Test hiring manager initialization"""
        mock_llm = Mock()
        agent = HiringManagerAgent(mock_llm)

        assert agent.config.name == "hiring_manager"
        assert agent.config.display_name == "招聘经理"


class TestHRAgent:
    """Tests for HRAgent"""

    def test_hr_agent_initialization(self):
        """Test HR agent initialization"""
        mock_llm = Mock()
        agent = HRAgent(mock_llm)

        assert agent.config.name == "hr_specialist"
        assert agent.config.display_name == "HR专员"

    @pytest.mark.asyncio
    async def test_hr_agent_propose_questions(self):
        """Test HR agent proposes soft skill questions"""
        mock_llm = Mock()
        mock_llm.call_json = AsyncMock(return_value={
            "questions": [
                {
                    "question": "请描述一次你在团队中遇到意见分歧的经历，你是如何处理的？",
                    "rationale": "评估候选人的冲突解决能力和团队协作意识，了解其处理问题的方式",
                    "tags": ["软技能", "团队协作"],
                    "confidence": 0.8,
                    "category": "teamwork"
                }
            ]
        })

        agent = HRAgent(mock_llm)
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        questions = await agent.propose_questions("Test resume", user_config)

        assert len(questions) > 0
        assert "软技能" in questions[0].tags or "团队协作" in questions[0].tags


class TestAdvisorAgent:
    """Tests for AdvisorAgent"""

    def test_advisor_agent_initialization(self):
        """Test advisor agent initialization"""
        mock_llm = Mock()
        agent = AdvisorAgent(mock_llm)

        assert agent.config.name == "academic_advisor"
        assert agent.config.display_name == "学术导师"

    @pytest.mark.asyncio
    async def test_advisor_agent_skips_job_mode(self):
        """Test advisor agent returns empty for job mode"""
        mock_llm = Mock()
        agent = AdvisorAgent(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        questions = await agent.propose_questions("Test resume", user_config)

        assert len(questions) == 0  # Should skip for job mode


class TestReviewerAgent:
    """Tests for ReviewerAgent"""

    def test_reviewer_agent_initialization(self):
        """Test reviewer agent initialization"""
        mock_llm = Mock()
        agent = ReviewerAgent(mock_llm)

        assert agent.config.name == "academic_reviewer"
        assert agent.config.display_name == "学术评审"

    @pytest.mark.asyncio
    async def test_reviewer_agent_skips_job_mode(self):
        """Test reviewer agent returns empty for job mode"""
        mock_llm = Mock()
        agent = ReviewerAgent(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        questions = await agent.propose_questions("Test resume", user_config)

        assert len(questions) == 0  # Should skip for job mode


class TestAdvocateAgent:
    """Tests for AdvocateAgent"""

    def test_advocate_agent_initialization(self):
        """Test advocate agent initialization"""
        mock_llm = Mock()
        agent = AdvocateAgent(mock_llm)

        assert agent.config.name == "candidate_advocate"
        assert agent.config.display_name == "候选人倡导者"

    @pytest.mark.asyncio
    async def test_advocate_agent_proposes_questions(self):
        """Test advocate agent proposes fairness questions"""
        mock_llm = Mock()
        mock_llm.call_json = AsyncMock(return_value={
            "questions": [
                {
                    "question": "你简历中最引以为豪的成就是什么？",
                    "rationale": "给候选人机会展示核心优势和问题解决能力，确保其亮点得到充分评估",
                    "tags": ["优势展示"],
                    "confidence": 0.8,
                    "purpose": "highlight_strengths"
                }
            ]
        })

        agent = AdvocateAgent(mock_llm)
        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        questions = await agent.propose_questions("Test resume", user_config)

        assert len(questions) > 0
        assert questions[0].metadata.get("purpose") == "highlight_strengths"


class TestBaseAgentValidation:
    """Tests for BaseAgent validation methods"""

    def test_validate_draft_question_success(self):
        """Test validation accepts valid question"""
        mock_llm = Mock()
        agent = TechnicalInterviewerAgent(mock_llm)

        draft = DraftQuestion(
            question="This is a valid question with sufficient length?",
            rationale="This is a valid rationale with sufficient detail",
            role_name="test",
            role_display="Test",
            confidence=0.85
        )

        assert agent.validate_draft_question(draft) is True

    def test_validate_draft_question_too_short(self):
        """Test Pydantic validation rejects too short question"""
        from pydantic import ValidationError
        
        # Pydantic should catch this at construction time
        with pytest.raises(ValidationError):
            DraftQuestion(
                question="Too short",  # Less than 10 chars
                rationale="This is a valid rationale with sufficient length",
                role_name="test",
                role_display="Test",
                confidence=0.85
            )

    def test_validate_draft_question_invalid_confidence(self):
        """Test validation rejects invalid confidence"""
        mock_llm = Mock()
        agent = TechnicalInterviewerAgent(mock_llm)

        # Confidence outside 0-1 range should be caught by Pydantic
        # But we test the validate method's own checks
        draft = DraftQuestion(
            question="Valid question here?",
            rationale="This is a valid rationale with sufficient length",
            role_name="test",
            role_display="Test",
            confidence=0.5  # Valid value
        )

        # Manually set invalid confidence (bypassing Pydantic)
        draft.confidence = 1.5

        assert agent.validate_draft_question(draft) is False
