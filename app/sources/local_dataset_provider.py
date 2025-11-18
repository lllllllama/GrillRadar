"""Local dataset backed provider for ExternalInfoService."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.models.external_info import (
    ExternalInfoSummary,
    InterviewExperience,
    JobDescription,
    KeywordTrend,
    TopicTrend,
)
from app.models.user_config import UserConfig
from app.retrieval.info_aggregator import InfoAggregator
from app.sources.json_data_provider import JSONDataProvider


class LocalDatasetProvider:
    """Provide deterministic external info from curated JSON datasets."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_provider = JSONDataProvider(data_dir=data_dir)
        self._latest_keyword_trends: List[KeywordTrend] = []
        self._latest_topic_trends: List[TopicTrend] = []

    def retrieve_external_info(
        self,
        user_config: Optional[UserConfig] = None,
        *,
        company: Optional[str] = None,
        position: Optional[str] = None,
        domain: Optional[str] = None,
        enable_jd: bool = True,
        enable_interview_exp: bool = True,
    ) -> Optional[ExternalInfoSummary]:
        """Load curated data and convert to ExternalInfoSummary."""

        target_domain = domain or (user_config.domain if user_config else None)
        company = company or (user_config.target_company if user_config else None)
        raw_position = position or (user_config.target_desc if user_config else None)
        position = self._infer_position_keyword(raw_position, target_domain)

        jds: List[JobDescription] = []
        experiences: List[InterviewExperience] = []

        if enable_jd:
            jds = self.data_provider.get_jds(company=company, position=position, domain=target_domain)

        if enable_interview_exp:
            experiences = self.data_provider.get_experiences(company=company, position=position)

        if not jds and not experiences:
            self._latest_keyword_trends = []
            self._latest_topic_trends = []
            return None

        summary = InfoAggregator.aggregate(jds, experiences)
        keyword_trends = self._build_keyword_trends(jds, target_domain)
        topic_trends = self._build_topic_trends(experiences)

        summary.keyword_trends = keyword_trends
        summary.topic_trends = topic_trends

        self._latest_keyword_trends = keyword_trends
        self._latest_topic_trends = topic_trends

        return summary

    def _build_keyword_trends(
        self,
        jds,
        domain: Optional[str],
    ) -> List[KeywordTrend]:
        high_freq = self.data_provider.get_high_frequency_keywords(
            jds,
            domain=domain,
            top_k=20,
            min_frequency=1,
        )
        jd_sources = self._build_keyword_source_map(jds)
        trends: List[KeywordTrend] = []
        for keyword, freq in high_freq:
            sources = jd_sources.get(keyword.lower(), [])
            weight = float(freq)
            if domain and domain.lower() in keyword.lower():
                weight *= 1.2
            trends.append(
                KeywordTrend(
                    keyword=keyword,
                    frequency=freq,
                    weight=round(weight, 2),
                    sources=sources,
                )
            )
        return trends

    def _build_topic_trends(self, experiences) -> List[TopicTrend]:
        topic_counter: Dict[str, int] = {}
        for exp in experiences:
            for topic in exp.topics:
                topic_counter[topic] = topic_counter.get(topic, 0) + 1
        return [TopicTrend(topic=topic, frequency=freq) for topic, freq in sorted(
            topic_counter.items(), key=lambda item: item[1], reverse=True
        )]

    @staticmethod
    def _build_keyword_source_map(jds) -> Dict[str, List[str]]:
        mapping: Dict[str, List[str]] = {}
        for jd in jds:
            company = jd.company
            for keyword in jd.keywords:
                mapping.setdefault(keyword.lower(), [])
                if company not in mapping[keyword.lower()]:
                    mapping[keyword.lower()].append(company)
        return mapping

    def format_prompt(self, summary: Optional[ExternalInfoSummary]) -> str:
        if summary is None:
            return "未找到相关外部信息"

        lines = ["### External Intelligence (Local Dataset)"]
        lines.append(summary.get_summary_text())

        if self._latest_keyword_trends:
            lines.append("\n**高频技能（近30天样本）**:")
            for trend in self._latest_keyword_trends[:8]:
                source_hint = ", ".join(trend.sources[:3]) if trend.sources else "多家公司"
                lines.append(
                    f"- {trend.keyword}: {trend.frequency} 次 (来源: {source_hint})"
                )

        if self._latest_topic_trends:
            lines.append("\n**常见面试主题**:")
            for topic in self._latest_topic_trends[:5]:
                lines.append(f"- {topic.topic}: {topic.frequency} 次")

        lines.append("\n提示：优先关注高频技能，生成 support_notes 时显式标注。")
        return "\n".join(lines)

    def get_trend_payload(self) -> Dict[str, List[dict]]:
        return {
            "keyword_trends": [trend.model_dump() for trend in self._latest_keyword_trends],
            "topic_trends": [trend.model_dump() for trend in self._latest_topic_trends],
        }

    @staticmethod
    def _infer_position_keyword(text: Optional[str], domain: Optional[str]) -> Optional[str]:
        if not text and not domain:
            return None

        text = text or ""
        if "后端" in text or (domain == "backend"):
            return "后端"
        if "前端" in text or (domain == "frontend"):
            return "前端"
        if any(key in text.lower() for key in ["nlp", "自然语言", "llm"]):
            return "NLP"
        if "算法" in text:
            return "算法"
        if domain == "ml":
            return "机器学习"
        if domain == "cv_segmentation":
            return "计算机视觉"
        return text.split()[0] if text else None
