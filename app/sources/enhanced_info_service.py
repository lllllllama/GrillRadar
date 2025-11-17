"""Enhanced External Information Service with Keyword Frequency Analysis

TrendRadar-style information acquisition with high-frequency keyword tracking.
"""
import logging
from typing import Optional, List, Tuple
from app.models.external_info import ExternalInfoSummary
from app.sources.json_data_provider import json_data_provider
from app.retrieval.info_aggregator import InfoAggregator

logger = logging.getLogger(__name__)


class EnhancedInfoService:
    """Enhanced external information service with keyword frequency analysis"""

    def __init__(self, use_json_data: bool = True):
        """
        Initialize enhanced info service

        Args:
            use_json_data: Whether to use JSON data provider (default True)
        """
        self.use_json_data = use_json_data
        self.data_provider = json_data_provider

    def retrieve_with_trends(
        self,
        company: Optional[str] = None,
        position: Optional[str] = None,
        domain: Optional[str] = None,
        enable_jd: bool = True,
        enable_interview_exp: bool = True
    ) -> Tuple[Optional[ExternalInfoSummary], List[Tuple[str, int]]]:
        """
        Retrieve external info with keyword frequency analysis

        Args:
            company: Target company (optional)
            position: Target position (optional)
            domain: Target domain for relevance weighting
            enable_jd: Whether to enable JD retrieval
            enable_interview_exp: Whether to enable interview experience retrieval

        Returns:
            Tuple of (ExternalInfoSummary, high_frequency_keywords)
            high_frequency_keywords is a list of (keyword, frequency) tuples
        """
        try:
            jds = []
            experiences = []

            if enable_jd and self.use_json_data:
                jds = self.data_provider.get_jds(company, position, domain)
                logger.info(f"Retrieved {len(jds)} JDs from JSON data")

            if enable_interview_exp and self.use_json_data:
                experiences = self.data_provider.get_experiences(company, position)
                logger.info(f"Retrieved {len(experiences)} interview experiences from JSON data")

            # If nothing found, return None
            if not jds and not experiences:
                logger.info("No external information found")
                return None, []

            # Aggregate information
            summary = InfoAggregator.aggregate(jds, experiences)

            # Analyze keyword frequency
            high_freq_keywords = self.data_provider.get_high_frequency_keywords(
                jds,
                domain=domain,
                top_k=15,
                min_frequency=2
            )

            logger.info(f"Identified {len(high_freq_keywords)} high-frequency keywords")

            return summary, high_freq_keywords

        except Exception as e:
            logger.error(f"Failed to retrieve external info with trends: {e}", exc_info=True)
            return None, []

    def format_for_prompt(
        self,
        summary: Optional[ExternalInfoSummary],
        high_freq_keywords: List[Tuple[str, int]]
    ) -> str:
        """
        Format external info for prompt with keyword frequency highlights

        Args:
            summary: External info summary
            high_freq_keywords: List of (keyword, frequency) tuples

        Returns:
            Formatted text for prompt injection
        """
        if summary is None and not high_freq_keywords:
            return ""

        lines = []
        lines.append("### External Information & Trend Analysis (TrendRadar)")

        # Basic summary
        if summary:
            if summary.job_descriptions:
                lines.append(f"\n**Retrieved JDs**: {len(summary.job_descriptions)}")

            if summary.interview_experiences:
                lines.append(f"**Retrieved Interview Experiences**: {len(summary.interview_experiences)}")

            # Aggregated keywords
            if summary.aggregated_keywords:
                keywords_str = "、".join(summary.aggregated_keywords[:12])
                lines.append(f"**Core Skills**: {keywords_str}")

            # Sample JDs
            if summary.job_descriptions:
                lines.append("\n**Sample JDs**:")
                for jd in summary.job_descriptions[:2]:
                    lines.append(f"- **{jd.company} - {jd.position}**")
                    if jd.requirements:
                        lines.append(f"  Requirements: {'; '.join(jd.requirements[:3])}")

            # High-frequency questions
            if summary.high_frequency_questions:
                lines.append("\n**High-Frequency Interview Questions**:")
                for q in summary.high_frequency_questions[:5]:
                    lines.append(f"- {q}")

        # 🔥 Keyword Frequency Analysis (TrendRadar-style)
        if high_freq_keywords:
            lines.append("\n**🔥 High-Frequency Keywords (TrendRadar Analysis)**:")
            lines.append("The following keywords appear most frequently in target domain JDs:")

            # Format as: keyword (frequency: N times)
            keyword_lines = []
            for keyword, freq in high_freq_keywords[:10]:
                if freq >= 3:
                    keyword_lines.append(f"**{keyword}** (频次: {freq})")
                else:
                    keyword_lines.append(f"{keyword} (频次: {freq})")

            lines.append("- " + "、".join(keyword_lines))

            lines.append("\n**📊 Instruction for support_notes Enhancement**:")
            lines.append(
                "When generating support_notes for each question, if the question involves any of the "
                "high-frequency keywords above, explicitly mark them as '高频技能' or '行业热点' in support_notes. "
                "For example: '该问题涉及{keyword}（高频技能，在{freq}个JD中出现），建议重点准备...'"
            )

        lines.append(
            "\n**Note**: Use this external data to make questions more aligned with real interview scenarios."
        )

        return "\n".join(lines)

    def get_keyword_frequency_hint(
        self,
        high_freq_keywords: List[Tuple[str, int]]
    ) -> str:
        """
        Get a concise hint about high-frequency keywords for support_notes

        Args:
            high_freq_keywords: List of (keyword, frequency) tuples

        Returns:
            Concise hint text
        """
        if not high_freq_keywords:
            return ""

        # Get top 5 keywords
        top_keywords = high_freq_keywords[:5]
        keyword_str = "、".join([kw for kw, _ in top_keywords])

        hint = f"高频技能（在多个JD中出现）: {keyword_str}。在support_notes中遇到这些关键词时，请标注为'高频技能'。"
        return hint


# Global singleton
enhanced_info_service = EnhancedInfoService(use_json_data=True)
