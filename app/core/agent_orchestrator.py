"""
Agent Orchestrator - Multi-Agent Workflow Coordinator

Orchestrates the entire multi-agent workflow:
1. Initialize all agents
2. Collect proposals in parallel
3. Forum discussion and consolidation
4. Final report generation
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional

from app.agents.models import DraftQuestion, AgentOutput, WorkflowContext
from app.agents.technical_interviewer import TechnicalInterviewerAgent
from app.agents.hiring_manager import HiringManagerAgent
from app.agents.hr_agent import HRAgent
from app.agents.advisor_agent import AdvisorAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.advocate_agent import AdvocateAgent
from app.core.forum_engine import ForumEngine
from app.models.user_config import UserConfig
from app.models.report import Report, ReportMeta
from app.models.question_item import QuestionItem
from app.utils.debug_dumper import get_debug_dumper

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Multi-Agent Orchestrator

    Coordinates all agents and manages the workflow from
    proposal to final report generation.

    Architecture:
    - Phase 1: Parallel agent proposals
    - Phase 2: Forum discussion & consolidation
    - Phase 3: Final report assembly
    """

    def __init__(self, llm_client):
        """
        Initialize orchestrator with all agents

        Args:
            llm_client: LLM client for agent communication
        """
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

        # Initialize all 6 agents
        # Core agents (job + grad)
        self.technical = TechnicalInterviewerAgent(llm_client)
        self.hiring_manager = HiringManagerAgent(llm_client)

        # Soft skills & culture (job focus)
        self.hr = HRAgent(llm_client)

        # Academic agents (grad focus)
        self.advisor = AdvisorAgent(llm_client)
        self.reviewer = ReviewerAgent(llm_client)

        # Quality control (all modes)
        self.advocate = AdvocateAgent(llm_client)

        # Forum engine for coordination
        self.forum_engine = ForumEngine(llm_client)

        self.logger.info("AgentOrchestrator initialized with 6 agents")

    async def generate_report(
        self,
        user_config: UserConfig,
        enable_multi_agent: bool = True
    ) -> Report:
        """
        Orchestrate multi-agent workflow to generate final report

        Args:
            user_config: User configuration
            enable_multi_agent: If False, fallback to single-agent mode

        Returns:
            Generated Report

        Raises:
            Exception: If generation fails
        """
        if not enable_multi_agent:
            # Fallback to single-agent mode
            self.logger.info("Multi-agent disabled, using fallback")
            return await self._fallback_generation(user_config)

        self.logger.info("=" * 70)
        self.logger.info("MULTI-AGENT REPORT GENERATION")
        self.logger.info("=" * 70)

        start_time = time.time()
        context = WorkflowContext(user_config, user_config.resume_text)

        try:
            # Phase 1: Collect agent proposals
            self.logger.info("\n=== PHASE 1: Agent Proposals ===")
            draft_questions = await self._collect_proposals(context)

            # Phase 2: Forum discussion
            self.logger.info("\n=== PHASE 2: Forum Discussion ===")
            final_questions = await self.forum_engine.discuss(
                draft_questions,
                user_config.resume_text,
                user_config
            )

            # Phase 3: Assemble final report
            self.logger.info("\n=== PHASE 3: Report Assembly ===")
            report = self._assemble_report(final_questions, user_config, context)

            elapsed = time.time() - start_time
            self.logger.info("=" * 70)
            self.logger.info(f"✅ Report generated successfully in {elapsed:.2f}s")
            self.logger.info(f"📊 Questions: {len(report.questions)}")
            self.logger.info(f"💰 Estimated cost: ${context.state.total_cost_estimate:.3f}")
            self.logger.info(f"🔧 LLM calls: {context.state.total_llm_calls}")
            self.logger.info("=" * 70)

            # Debug: dump workflow summary
            context.state.final_question_count = len(report.questions)
            context.state.report_generated = True
            debug_dumper = get_debug_dumper()
            debug_dumper.dump_workflow_summary(context.state)

            return report

        except Exception as e:
            self.logger.error(f"Multi-agent generation failed: {e}", exc_info=True)
            # Fallback to single-agent mode
            self.logger.info("Falling back to single-agent mode...")
            return await self._fallback_generation(user_config)

    async def _collect_proposals(
        self,
        context: WorkflowContext
    ) -> Dict[str, List[DraftQuestion]]:
        """
        Collect proposals from all agents in parallel

        Args:
            context: Workflow context

        Returns:
            Dict mapping agent names to their draft questions
        """
        user_config = context.user_config
        resume_text = context.resume_text

        self.logger.info(f"Collecting proposals from {6} agents in parallel...")

        # Run all 6 agents in parallel
        results = await asyncio.gather(
            self._run_agent_with_tracking(
                self.technical,
                resume_text,
                user_config,
                context
            ),
            self._run_agent_with_tracking(
                self.hiring_manager,
                resume_text,
                user_config,
                context
            ),
            self._run_agent_with_tracking(
                self.hr,
                resume_text,
                user_config,
                context
            ),
            self._run_agent_with_tracking(
                self.advisor,
                resume_text,
                user_config,
                context
            ),
            self._run_agent_with_tracking(
                self.reviewer,
                resume_text,
                user_config,
                context
            ),
            self._run_agent_with_tracking(
                self.advocate,
                resume_text,
                user_config,
                context
            ),
            return_exceptions=True  # Don't fail if one agent fails
        )

        # Collect results
        proposals = {}
        agent_names = [
            "technical_interviewer",
            "hiring_manager",
            "hr_specialist",
            "academic_advisor",
            "academic_reviewer",
            "candidate_advocate"
        ]

        debug_dumper = get_debug_dumper()

        for idx, result in enumerate(results):
            agent_name = agent_names[idx]

            if isinstance(result, Exception):
                self.logger.error(f"Agent '{agent_name}' failed: {result}")
                context.record_error(agent_name, str(result))
                proposals[agent_name] = []
                # Debug: dump error
                debug_dumper.dump_agent_output(agent_name, [], success=False, error=str(result))
            elif isinstance(result, list):
                proposals[agent_name] = result
                context.record_proposal(agent_name, result)
                self.logger.info(f"  ✓ {agent_name}: {len(result)} questions")
                # Debug: dump agent output
                debug_dumper.dump_agent_output(agent_name, result, success=True)
            else:
                self.logger.warning(f"Unexpected result from {agent_name}: {type(result)}")
                proposals[agent_name] = []

        return proposals

    async def _run_agent_with_tracking(
        self,
        agent,
        resume_text: str,
        user_config: UserConfig,
        context: WorkflowContext
    ) -> List[DraftQuestion]:
        """
        Run agent and track metrics

        Args:
            agent: Agent instance
            resume_text: Resume text
            user_config: User configuration
            context: Workflow context

        Returns:
            List of draft questions
        """
        start_time = time.time()

        try:
            questions = await agent.generate_with_fallback(resume_text, user_config)

            elapsed = time.time() - start_time
            context.record_llm_call(tokens=2000, cost=0.02)  # Estimate

            return questions

        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Agent {agent.config.name} failed after {elapsed:.2f}s: {e}")
            raise

    def _assemble_report(
        self,
        questions: List[QuestionItem],
        user_config: UserConfig,
        context: WorkflowContext
    ) -> Report:
        """
        Assemble final report from questions

        Args:
            questions: Final list of QuestionItems
            user_config: User configuration
            context: Workflow context

        Returns:
            Complete Report object
        """
        # Generate summary based on mode
        if user_config.mode == "job":
            summary = self._generate_job_summary(questions, user_config)
            highlights = self._generate_job_highlights(user_config)
            risks = self._generate_job_risks(user_config)
        elif user_config.mode == "grad":
            summary = self._generate_grad_summary(questions, user_config)
            highlights = self._generate_grad_highlights(user_config)
            risks = self._generate_grad_risks(user_config)
        else:  # mixed
            summary = self._generate_mixed_summary(questions, user_config)
            highlights = self._generate_mixed_highlights(user_config)
            risks = self._generate_mixed_risks(user_config)

        # Create report metadata
        meta = ReportMeta(
            num_questions=len(questions),
            model=self.llm_client.__class__.__name__ if hasattr(self.llm_client, '__class__') else "multi-agent",
            workflow_id=context.state.workflow_id,
            multi_agent_enabled=True,
            agent_count=len(context.state.proposals),
            total_llm_calls=context.state.total_llm_calls
        )

        return Report(
            summary=summary,
            mode=user_config.mode,
            target_desc=user_config.target_desc,
            highlights=highlights,
            risks=risks,
            questions=questions,
            meta=meta
        )

    def _generate_job_summary(self, questions: List[QuestionItem], config: UserConfig) -> str:
        """Generate summary for job mode"""
        return f"""基于简历分析和多智能体评估，为{config.target_desc}生成了{len(questions)}个核心面试问题。

**评估维度：**
- 技术深度与广度
- 项目经验与impact
- 岗位匹配度
- 软技能与团队协作

**准备建议：**
本报告采用多智能体协作生成，综合了技术面试官、招聘经理等多个角色的视角。
建议针对每个问题准备具体的项目案例，重点展示技术深度和业务价值。
"""

    def _generate_job_highlights(self, config: UserConfig) -> str:
        """Generate highlights for job mode"""
        return """**候选人优势：**
- 相关项目经验与目标岗位匹配
- 具备核心技术栈基础
- 展现出一定的技术深度

**注意**：以上是基于简历的初步判断，需要通过回答具体问题来验证。
"""

    def _generate_job_risks(self, config: UserConfig) -> str:
        """Generate risks for job mode"""
        return """**潜在风险点：**
- 部分技术细节可能会被深入追问
- 项目的实际贡献度和复杂度需要证明
- 系统设计和架构能力需要验证

**准备重点**：准备好回答"为什么"和"怎么做"的问题，而非仅仅描述"做了什么"。
"""

    def _generate_grad_summary(self, questions: List[QuestionItem], config: UserConfig) -> str:
        """Generate summary for grad mode"""
        return f"""基于简历分析和多智能体评估，为{config.target_desc}生成了{len(questions)}个核心面试问题。

**评估维度：**
- 研究兴趣与方向匹配
- 学术素养与批判性思维
- 实验设计与方法论
- 学术诚信与合作能力
"""

    def _generate_grad_highlights(self, config: UserConfig) -> str:
        """Generate highlights for grad mode"""
        return """**候选人优势：**
- 研究方向与目标项目相关
- 具备基础的研究素养
- 表现出学术兴趣

**注意**：以上是基于简历的初步判断。
"""

    def _generate_grad_risks(self, config: UserConfig) -> str:
        """Generate risks for grad mode"""
        return """**潜在风险点：**
- 研究深度和广度需要验证
- 论文阅读和批判性思维能力
- 实验设计和方法论理解
"""

    def _generate_mixed_summary(self, questions: List[QuestionItem], config: UserConfig) -> str:
        """Generate summary for mixed mode"""
        return f"""基于多智能体评估，从工程和学术双重视角生成了{len(questions)}个面试问题。

**工程视角**: 技术实践、项目经验、工程能力
**学术视角**: 研究潜力、方法论、学术素养
"""

    def _generate_mixed_highlights(self, config: UserConfig) -> str:
        """Generate highlights for mixed mode"""
        return """**候选人优势（双视角）：**
- 同时具备工程实践和研究经验
- 技术基础扎实，有学术潜力
"""

    def _generate_mixed_risks(self, config: UserConfig) -> str:
        """Generate risks for mixed mode"""
        return """**潜在风险点：**
- 需要明确职业规划方向（工程 vs 学术）
- 两个方向的深度都需要验证
"""

    async def _fallback_generation(self, user_config: UserConfig) -> Report:
        """
        Fallback to single-agent generation

        Used when multi-agent mode fails or is disabled.

        Args:
            user_config: User configuration

        Returns:
            Report generated by fallback method
        """
        from app.core.report_generator import ReportGenerator

        self.logger.warning("Using fallback single-agent generation")
        generator = ReportGenerator()
        return generator.generate_report(user_config)
