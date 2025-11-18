"""
GrillRadar Pipeline - Central Orchestration

This module provides a clean abstraction for the entire report generation pipeline.
It decouples CLI/API from implementation details (document parsing, agent orchestration, etc.)

Usage:
    pipeline = GrillRadarPipeline(request_id="req_abc123")
    report = pipeline.run(resume_path="resume.pdf", user_config=config)
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Union

from app.models import UserConfig, Report
from app.core.report_generator import ReportGenerator
from app.core.agent_orchestrator import AgentOrchestrator
from app.core.llm_client import LLMClient
from app.utils.document_parser import parse_resume, is_supported_format, DocumentParseError
from app.config.settings import settings
from app.core.logging import get_logger, log_stage_timing, set_request_context, generate_request_id

logger = get_logger(__name__)


class GrillRadarPipeline:
    """
    Central Pipeline for Report Generation

    This class orchestrates the entire flow:
    1. Resume parsing (PDF/Word/TXT/Markdown)
    2. External info fetching (if enabled)
    3. Single-agent or multi-agent generation
    4. Final report assembly

    Design goals:
    - Single entry point for all report generation
    - Isolate CLI/API from implementation details
    - Easy to test and extend
    """

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        enable_multi_agent: Optional[bool] = None,
        request_id: Optional[str] = None
    ):
        """
        Initialize pipeline

        Args:
            llm_provider: LLM provider (anthropic/openai), defaults to settings
            llm_model: LLM model name, defaults to settings
            enable_multi_agent: Enable multi-agent mode, defaults to settings.MULTI_AGENT_ENABLED
            request_id: Request ID for tracing (auto-generated if not provided)
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model or settings.DEFAULT_MODEL
        self.enable_multi_agent = enable_multi_agent if enable_multi_agent is not None else settings.MULTI_AGENT_ENABLED
        self.request_id = request_id or generate_request_id()
        self.logger = get_logger(__name__)

    def run(
        self,
        resume_path: Union[str, Path],
        user_config: UserConfig
    ) -> Report:
        """
        Main pipeline execution - synchronous wrapper

        Args:
            resume_path: Path to resume file (PDF/Word/TXT/MD)
            user_config: User configuration (must NOT include resume_text yet)

        Returns:
            Generated Report

        Raises:
            DocumentParseError: If resume parsing fails
            ValidationError: If config validation fails
            Exception: If report generation fails
        """
        # Set request context for logging
        set_request_context(
            request_id=self.request_id,
            mode=user_config.mode,
            domain=user_config.domain,
            target_desc=user_config.target_desc,
            llm_model=self.llm_model
        )

        self.logger.info(
            f"Pipeline started - mode={user_config.mode}, multi_agent={self.enable_multi_agent}",
            extra={'request_id': self.request_id}
        )

        # Parse resume with timing
        with log_stage_timing(self.logger, "resume_parsing", self.request_id):
            resume_text = self._parse_resume(resume_path)

        # Update user_config with parsed text
        user_config.resume_text = resume_text

        # Generate report (synchronous wrapper around async)
        with log_stage_timing(self.logger, "report_generation", self.request_id):
            if self.enable_multi_agent:
                report = asyncio.run(self._generate_multi_agent(user_config))
            else:
                report = self._generate_single_agent(user_config)

        self.logger.info(
            f"Pipeline completed - {len(report.questions)} questions generated",
            extra={'request_id': self.request_id}
        )

        return report

    async def run_async(
        self,
        resume_path: Union[str, Path],
        user_config: UserConfig
    ) -> Report:
        """
        Main pipeline execution - async version

        Args:
            resume_path: Path to resume file (PDF/Word/TXT/MD)
            user_config: User configuration (must NOT include resume_text yet)

        Returns:
            Generated Report

        Raises:
            DocumentParseError: If resume parsing fails
            ValidationError: If config validation fails
            Exception: If report generation fails
        """
        # Set request context for logging
        set_request_context(
            request_id=self.request_id,
            mode=user_config.mode,
            domain=user_config.domain,
            target_desc=user_config.target_desc,
            llm_model=self.llm_model
        )

        self.logger.info(
            f"Pipeline started (async) - mode={user_config.mode}, multi_agent={self.enable_multi_agent}",
            extra={'request_id': self.request_id}
        )

        # Parse resume with timing
        with log_stage_timing(self.logger, "resume_parsing", self.request_id):
            resume_text = self._parse_resume(resume_path)

        # Update user_config with parsed text
        user_config.resume_text = resume_text

        # Generate report
        with log_stage_timing(self.logger, "report_generation", self.request_id):
            if self.enable_multi_agent:
                report = await self._generate_multi_agent(user_config)
            else:
                report = self._generate_single_agent(user_config)

        self.logger.info(
            f"Pipeline completed - {len(report.questions)} questions generated",
            extra={'request_id': self.request_id}
        )

        return report

    def run_with_text(
        self,
        resume_text: str,
        user_config: UserConfig
    ) -> Report:
        """
        Run pipeline with pre-parsed resume text

        Useful for API endpoints that receive resume as text.

        Args:
            resume_text: Pre-parsed resume text
            user_config: User configuration (must NOT include resume_text yet)

        Returns:
            Generated Report
        """
        # Set request context for logging
        set_request_context(
            request_id=self.request_id,
            mode=user_config.mode,
            domain=user_config.domain,
            target_desc=user_config.target_desc,
            llm_model=self.llm_model
        )

        self.logger.info(
            f"Pipeline started (with text) - mode={user_config.mode}, multi_agent={self.enable_multi_agent}",
            extra={'request_id': self.request_id}
        )

        # Update user_config with text
        user_config.resume_text = resume_text

        # Generate report
        with log_stage_timing(self.logger, "report_generation", self.request_id):
            if self.enable_multi_agent:
                report = asyncio.run(self._generate_multi_agent(user_config))
            else:
                report = self._generate_single_agent(user_config)

        self.logger.info(
            f"Pipeline completed - {len(report.questions)} questions generated",
            extra={'request_id': self.request_id}
        )

        return report

    async def run_with_text_async(
        self,
        resume_text: str,
        user_config: UserConfig
    ) -> Report:
        """
        Run pipeline with pre-parsed resume text - async version

        Args:
            resume_text: Pre-parsed resume text
            user_config: User configuration (must NOT include resume_text yet)

        Returns:
            Generated Report
        """
        # Set request context for logging
        set_request_context(
            request_id=self.request_id,
            mode=user_config.mode,
            domain=user_config.domain,
            target_desc=user_config.target_desc,
            llm_model=self.llm_model
        )

        self.logger.info(
            f"Pipeline started (async with text) - mode={user_config.mode}, multi_agent={self.enable_multi_agent}",
            extra={'request_id': self.request_id}
        )

        # Update user_config with text
        user_config.resume_text = resume_text

        # Generate report
        with log_stage_timing(self.logger, "report_generation", self.request_id):
            if self.enable_multi_agent:
                report = await self._generate_multi_agent(user_config)
            else:
                report = self._generate_single_agent(user_config)

        self.logger.info(
            f"Pipeline completed - {len(report.questions)} questions generated",
            extra={'request_id': self.request_id}
        )

        return report

    def _parse_resume(self, resume_path: Union[str, Path]) -> str:
        """
        Parse resume from file

        Args:
            resume_path: Path to resume file

        Returns:
            Extracted text

        Raises:
            DocumentParseError: If parsing fails
        """
        resume_path = Path(resume_path)

        # Check file exists
        if not resume_path.exists():
            raise DocumentParseError(f"Resume file not found: {resume_path}")

        # Check format supported
        if not is_supported_format(str(resume_path)):
            raise DocumentParseError(
                f"Unsupported format: {resume_path.suffix}\n"
                f"Supported formats: .pdf, .docx, .txt, .md"
            )

        # Parse document
        self.logger.info(f"Parsing resume: {resume_path.name}")
        text = parse_resume(str(resume_path))

        # Validate extracted text
        if not text or len(text.strip()) < 50:
            raise DocumentParseError(
                f"Resume content too short or empty ({len(text.strip())} chars)\n"
                f"Please ensure file contains valid resume content"
            )

        self.logger.info(f"✓ Successfully parsed resume: {len(text)} chars")
        return text

    def _generate_single_agent(self, user_config: UserConfig) -> Report:
        """
        Generate report using single-agent mode (fallback)

        Args:
            user_config: User configuration with resume_text

        Returns:
            Generated Report
        """
        self.logger.info("Using single-agent mode", extra={'request_id': self.request_id})
        generator = ReportGenerator(
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            request_id=self.request_id
        )
        return generator.generate_report(user_config)

    async def _generate_multi_agent(self, user_config: UserConfig) -> Report:
        """
        Generate report using multi-agent mode

        Args:
            user_config: User configuration with resume_text

        Returns:
            Generated Report
        """
        self.logger.info("Using multi-agent mode", extra={'request_id': self.request_id})
        llm_client = LLMClient(
            provider=self.llm_provider,
            model=self.llm_model,
            request_id=self.request_id
        )
        orchestrator = AgentOrchestrator(llm_client, request_id=self.request_id)
        return await orchestrator.generate_report(user_config, enable_multi_agent=True)


# Convenience function for simple usage
def generate_report(
    resume_path: Union[str, Path],
    user_config: UserConfig,
    enable_multi_agent: Optional[bool] = None
) -> Report:
    """
    Convenience function for simple report generation

    Args:
        resume_path: Path to resume file
        user_config: User configuration
        enable_multi_agent: Enable multi-agent mode (defaults to settings)

    Returns:
        Generated Report

    Example:
        >>> config = UserConfig(mode="job", target_desc="Backend Engineer", ...)
        >>> report = generate_report("resume.pdf", config)
    """
    pipeline = GrillRadarPipeline(enable_multi_agent=enable_multi_agent)
    return pipeline.run(resume_path, user_config)
