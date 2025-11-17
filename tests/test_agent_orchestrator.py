"""Tests for AgentOrchestrator"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.core.agent_orchestrator import AgentOrchestrator
from app.agents.models import DraftQuestion, WorkflowContext
from app.models.user_config import UserConfig
from app.models.report import Report
from app.models.question_item import QuestionItem


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator"""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all 6 agents"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        assert orchestrator.technical is not None
        assert orchestrator.hiring_manager is not None
        assert orchestrator.hr is not None
        assert orchestrator.advisor is not None
        assert orchestrator.reviewer is not None
        assert orchestrator.advocate is not None
        assert orchestrator.forum_engine is not None

    @pytest.mark.asyncio
    async def test_orchestrator_generate_report_multi_agent_disabled(self):
        """Test orchestrator falls back when multi-agent is disabled"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        # Mock the fallback generation
        with patch.object(orchestrator, '_fallback_generation', new_callable=AsyncMock) as mock_fallback:
            mock_fallback.return_value = Mock(spec=Report)

            report = await orchestrator.generate_report(user_config, enable_multi_agent=False)

            mock_fallback.assert_called_once()
            assert report is not None

    @pytest.mark.asyncio
    async def test_collect_proposals_handles_agent_failure(self):
        """Test proposal collection handles individual agent failures gracefully"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        context = WorkflowContext(user_config, "Test resume")

        # Mock one agent to fail
        with patch.object(orchestrator.technical, 'generate_with_fallback', new_callable=AsyncMock) as mock_tech:
            with patch.object(orchestrator.hiring_manager, 'generate_with_fallback', new_callable=AsyncMock) as mock_hm:
                with patch.object(orchestrator.hr, 'generate_with_fallback', new_callable=AsyncMock) as mock_hr:
                    with patch.object(orchestrator.advisor, 'generate_with_fallback', new_callable=AsyncMock) as mock_adv:
                        with patch.object(orchestrator.reviewer, 'generate_with_fallback', new_callable=AsyncMock) as mock_rev:
                            with patch.object(orchestrator.advocate, 'generate_with_fallback', new_callable=AsyncMock) as mock_advo:
                                # Technical agent fails
                                mock_tech.side_effect = Exception("Agent failed")

                                # Other agents succeed
                                mock_hm.return_value = [
                                    DraftQuestion(
                                        question="Valid question?",
                                        rationale="This is a valid rationale with sufficient length",
                                        role_name="hiring_manager",
                                        role_display="招聘经理",
                                        confidence=0.8
                                    )
                                ]
                                mock_hr.return_value = []
                                mock_adv.return_value = []
                                mock_rev.return_value = []
                                mock_advo.return_value = []

                                proposals = await orchestrator._collect_proposals(context)

                                # Should have collected proposals from successful agents
                                assert "hiring_manager" in proposals
                                # Failed agent should have empty list
                                assert "technical_interviewer" in proposals
                                assert len(proposals["technical_interviewer"]) == 0

    @pytest.mark.asyncio
    async def test_run_agent_with_tracking_success(self):
        """Test agent tracking records metrics"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        context = WorkflowContext(user_config, "Test resume")

        # Mock agent
        mock_agent = Mock()
        mock_agent.generate_with_fallback = AsyncMock(return_value=[
            DraftQuestion(
                question="Test question?",
                rationale="This is a valid test rationale with sufficient length",
                role_name="test",
                role_display="Test",
                confidence=0.8
            )
        ])
        mock_agent.config = Mock(name="test_agent")

        questions = await orchestrator._run_agent_with_tracking(
            mock_agent,
            "Test resume",
            user_config,
            context
        )

        assert len(questions) == 1
        assert context.state.total_llm_calls > 0

    def test_assemble_report_job_mode(self):
        """Test report assembly for job mode"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        context = WorkflowContext(user_config, "Test resume")

        questions = [
            QuestionItem(
                id=1,
                view_role="技术面试官",
                tag="test",
                question="Test question 1?",
                rationale="This is a test rationale for question 1",
                baseline_answer="This is a baseline answer structure for testing purposes only",
                support_notes="Test support notes",
                prompt_template="This is a test prompt template for testing"
            ),
            QuestionItem(
                id=2,
                view_role="招聘经理",
                tag="test",
                question="Test question 2?",
                rationale="This is a test rationale for question 2",
                baseline_answer="This is a baseline answer structure for testing purposes only",
                support_notes="Test support notes",
                prompt_template="This is a test prompt template for testing"
            )
        ]

        report = orchestrator._assemble_report(questions, user_config, context)

        assert report is not None
        assert report.mode == "job"
        assert len(report.questions) == 2
        assert report.meta.multi_agent_enabled is True
        assert "技术深度与广度" in report.summary

    def test_assemble_report_grad_mode(self):
        """Test report assembly for grad mode"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="PhD Program",
            mode="grad",
            resume_text="Test resume"
        )

        context = WorkflowContext(user_config, "Test resume")

        questions = [
            QuestionItem(
                id=1,
                view_role="学术导师",
                tag="research",
                question="Research question?",
                rationale="This is a research test rationale",
                baseline_answer="This is a baseline answer for research testing purposes",
                support_notes="Research support notes",
                prompt_template="This is a research test prompt template"
            )
        ]

        report = orchestrator._assemble_report(questions, user_config, context)

        assert report is not None
        assert report.mode == "grad"
        assert "研究兴趣与方向匹配" in report.summary

    def test_generate_job_summary(self):
        """Test job mode summary generation"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume"
        )

        questions = [
            QuestionItem(id=1, view_role="Test", tag="test", question="Test question 1", rationale="Test rationale for this question", baseline_answer="Baseline answer for testing purposes", support_notes="Test support notes here", prompt_template="Test prompt template here"),
            QuestionItem(id=1, view_role="Test", tag="test", question="Test question 2", rationale="Test rationale for this question", baseline_answer="Baseline answer for testing purposes", support_notes="Test support notes here", prompt_template="Test prompt template here")
        ]

        summary = orchestrator._generate_job_summary(questions, user_config)

        assert "Software Engineer" in summary
        assert "技术深度与广度" in summary
        assert "多智能体" in summary

    def test_generate_grad_summary(self):
        """Test grad mode summary generation"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="PhD in CS",
            mode="grad",
            resume_text="Test resume"
        )

        questions = [
            QuestionItem(id=1, view_role="Test", tag="test", question="Test question 1", rationale="Test rationale for this question", baseline_answer="Baseline answer for testing purposes", support_notes="Test support notes here", prompt_template="Test prompt template here")
        ]

        summary = orchestrator._generate_grad_summary(questions, user_config)

        assert "PhD in CS" in summary
        assert "研究兴趣" in summary
        assert "学术素养" in summary

    def test_generate_mixed_summary(self):
        """Test mixed mode summary generation"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Research Engineer",
            mode="mixed",
            resume_text="Test resume"
        )

        questions = [
            QuestionItem(id=1, view_role="Test", tag="test", question="Test question 1", rationale="Test rationale for this question", baseline_answer="Baseline answer for testing purposes", support_notes="Test support notes here", prompt_template="Test prompt template here")
        ]

        summary = orchestrator._generate_mixed_summary(questions, user_config)

        assert "工程" in summary
        assert "学术" in summary
        assert "双重视角" in summary or "双视角" in summary


class TestAgentOrchestratorIntegration:
    """Integration tests for AgentOrchestrator"""

    @pytest.mark.asyncio
    async def test_full_workflow_job_mode(self):
        """Test complete multi-agent workflow for job mode"""
        mock_llm = Mock()
        orchestrator = AgentOrchestrator(mock_llm)

        user_config = UserConfig(
            target_desc="Software Engineer",
            mode="job",
            resume_text="Test resume with Python and Django experience"
        )

        # Mock all agent responses
        mock_question = DraftQuestion(
            question="Can you describe your Python experience?",
            rationale="This is a valid test rationale with sufficient length",
            role_name="technical_interviewer",
            role_display="技术面试官",
            confidence=0.85
        )

        with patch.object(orchestrator.technical, 'generate_with_fallback', new_callable=AsyncMock) as mock_tech:
            with patch.object(orchestrator.hiring_manager, 'generate_with_fallback', new_callable=AsyncMock) as mock_hm:
                with patch.object(orchestrator.hr, 'generate_with_fallback', new_callable=AsyncMock) as mock_hr:
                    with patch.object(orchestrator.advisor, 'generate_with_fallback', new_callable=AsyncMock) as mock_adv:
                        with patch.object(orchestrator.reviewer, 'generate_with_fallback', new_callable=AsyncMock) as mock_rev:
                            with patch.object(orchestrator.advocate, 'generate_with_fallback', new_callable=AsyncMock) as mock_advo:
                                with patch.object(orchestrator.forum_engine, 'discuss', new_callable=AsyncMock) as mock_forum:
                                    mock_tech.return_value = [mock_question]
                                    mock_hm.return_value = [mock_question]
                                    mock_hr.return_value = [mock_question]
                                    mock_adv.return_value = []  # Skip for job mode
                                    mock_rev.return_value = []  # Skip for job mode
                                    mock_advo.return_value = [mock_question]

                                    # Mock forum discussion result
                                    mock_forum.return_value = [
                                        QuestionItem(
                                            id=1,
                                            view_role="Multi-Agent",
                                            tag="final",
                                            question="Final question?",
                                            rationale="Final test rationale from multi-agent system",
                                            baseline_answer="Final baseline answer for testing purposes",
                                            support_notes="Final support notes",
                                            prompt_template="Final test prompt template"
                                        )
                                    ]

                                    report = await orchestrator.generate_report(user_config, enable_multi_agent=True)

                                    assert report is not None
                                    assert report.mode == "job"
                                    assert len(report.questions) > 0
                                    assert report.meta.multi_agent_enabled is True
                                    mock_forum.assert_called_once()
