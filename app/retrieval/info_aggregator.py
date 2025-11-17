"""信息聚合器（Milestone 4）

从多个JD和面经中提取和聚合关键信息
"""
from typing import List, Dict
from collections import Counter
from app.models.external_info import (
    JobDescription,
    InterviewExperience,
    ExternalInfoSummary
)


class InfoAggregator:
    """信息聚合器"""

    @staticmethod
    def aggregate(
        jds: List[JobDescription],
        experiences: List[InterviewExperience]
    ) -> ExternalInfoSummary:
        """
        聚合JD和面经信息

        Args:
            jds: JD列表
            experiences: 面经列表

        Returns:
            聚合后的信息摘要
        """
        # 聚合关键词
        all_keywords = []
        for jd in jds:
            all_keywords.extend(jd.keywords)

        # 计数并排序
        keyword_counter = Counter(all_keywords)
        aggregated_keywords = [kw for kw, _ in keyword_counter.most_common(20)]

        # 聚合主题
        all_topics = []
        for exp in experiences:
            all_topics.extend(exp.topics)

        topic_counter = Counter(all_topics)
        aggregated_topics = [topic for topic, _ in topic_counter.most_common(15)]

        # 提取高频问题
        high_frequency_questions = InfoAggregator._extract_high_frequency_questions(
            experiences
        )

        return ExternalInfoSummary(
            job_descriptions=jds,
            interview_experiences=experiences,
            aggregated_keywords=aggregated_keywords,
            aggregated_topics=aggregated_topics,
            high_frequency_questions=high_frequency_questions
        )

    @staticmethod
    def _extract_high_frequency_questions(
        experiences: List[InterviewExperience]
    ) -> List[str]:
        """
        提取高频面试问题

        使用简单的关键词匹配和频率统计
        """
        all_questions = []
        for exp in experiences:
            all_questions.extend(exp.questions)

        # 简化：直接返回前面的问题（实际应用中会做更复杂的去重和聚类）
        return all_questions[:10]

    @staticmethod
    def extract_requirements_keywords(jd: JobDescription) -> List[str]:
        """
        从单个JD中提取关键要求

        Args:
            jd: 职位描述

        Returns:
            关键词列表
        """
        keywords = set()

        # 从requirements中提取
        for req in jd.requirements:
            # 简单的关键词提取（实际应用中会使用NLP技术）
            if "年" in req and "经验" in req:
                keywords.add("工作经验")
            if any(lang in req for lang in ["Java", "Go", "Python", "C++"]):
                keywords.add("编程语言")
            if "分布式" in req:
                keywords.add("分布式系统")
            if "高并发" in req:
                keywords.add("高并发")
            if "数据库" in req or "MySQL" in req or "Redis" in req:
                keywords.add("数据库")

        # 添加明确的技术栈keywords
        keywords.update(jd.keywords)

        return list(keywords)

    @staticmethod
    def get_summary_for_prompt(summary: ExternalInfoSummary) -> str:
        """
        生成用于Prompt的格式化摘要

        Args:
            summary: 外部信息摘要

        Returns:
            格式化的字符串，可直接注入到Prompt中
        """
        lines = []

        if not summary.job_descriptions and not summary.interview_experiences:
            return "未检索到外部信息。"

        lines.append("### 外部信息参考（来自真实JD和面经）")

        # JD信息
        if summary.job_descriptions:
            lines.append(f"\n**相关JD数量**: {len(summary.job_descriptions)}个")
            lines.append("**核心技能要求**:")
            if summary.aggregated_keywords:
                keywords_str = "、".join(summary.aggregated_keywords[:12])
                lines.append(f"- {keywords_str}")

            # 显示部分JD
            lines.append("\n**典型JD示例**:")
            for jd in summary.job_descriptions[:2]:
                lines.append(f"- **{jd.company} - {jd.position}**")
                if jd.requirements:
                    lines.append(f"  要求：{'; '.join(jd.requirements[:3])}")

        # 面经信息
        if summary.interview_experiences:
            lines.append(f"\n**相关面经数量**: {len(summary.interview_experiences)}条")
            lines.append("**高频考察主题**:")
            if summary.aggregated_topics:
                topics_str = "、".join(summary.aggregated_topics[:10])
                lines.append(f"- {topics_str}")

            if summary.high_frequency_questions:
                lines.append("\n**高频面试题示例**:")
                for q in summary.high_frequency_questions[:5]:
                    lines.append(f"- {q}")

        lines.append("\n**提示**: 根据以上真实JD和面经，生成的问题应更贴近实际面试场景。")

        return "\n".join(lines)
