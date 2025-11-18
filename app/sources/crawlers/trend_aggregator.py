"""
趋势聚合器 / Trend Aggregator

将多源RawItem数据聚合、清洗、转换为ExternalInfoSummary
"""
from typing import List, Dict, Tuple
from collections import Counter
import re
from datetime import datetime

from app.sources.crawlers.models import RawItem
from app.models.external_info import (
    ExternalInfoSummary,
    JobDescription,
    InterviewExperience
)

import logging
logger = logging.getLogger(__name__)


class TrendAggregator:
    """趋势聚合器"""

    @staticmethod
    def aggregate(
        raw_items: List[RawItem],
        domain: str,
        max_jd: int = 5,
        max_exp: int = 5,
        max_keywords: int = 20
    ) -> ExternalInfoSummary:
        """
        聚合多源数据为ExternalInfoSummary

        Args:
            raw_items: 原始数据项列表
            domain: 目标领域
            max_jd: 最多生成的JD数量
            max_exp: 最多生成的面经数量
            max_keywords: 最多保留的关键词数量

        Returns:
            ExternalInfoSummary
        """
        logger.info(f"Aggregating {len(raw_items)} raw items")

        # 1. 去重（基于URL）
        unique_items = TrendAggregator._deduplicate(raw_items)
        logger.info(f"After deduplication: {len(unique_items)} items")

        # 2. 按互动分数排序
        unique_items.sort(key=lambda x: x.get_engagement_score(), reverse=True)

        # 3. 分组：技术项目(GitHub) vs 文章/面经(CSDN)
        github_items = [item for item in unique_items if item.source == 'github']
        csdn_items = [item for item in unique_items if item.source == 'csdn']

        # 4. 转换为JD和面经
        job_descriptions = TrendAggregator._convert_to_jds(
            github_items + csdn_items[:5],
            domain,
            max_jd
        )

        interview_experiences = TrendAggregator._convert_to_experiences(
            csdn_items,
            domain,
            max_exp
        )

        # 5. 提取和聚合关键词
        aggregated_keywords = TrendAggregator._extract_keywords(
            unique_items,
            max_keywords
        )

        # 6. 提取主题
        aggregated_topics = TrendAggregator._extract_topics(
            unique_items,
            max_topics=15
        )

        # 7. 提取高频问题（从CSDN面试文章）
        high_frequency_questions = TrendAggregator._extract_questions(
            csdn_items,
            max_questions=10
        )

        summary = ExternalInfoSummary(
            job_descriptions=job_descriptions,
            interview_experiences=interview_experiences,
            aggregated_keywords=aggregated_keywords,
            aggregated_topics=aggregated_topics,
            high_frequency_questions=high_frequency_questions,
            retrieved_at=datetime.utcnow()
        )

        logger.info(
            f"Aggregation complete: {len(job_descriptions)} JDs, "
            f"{len(interview_experiences)} experiences, "
            f"{len(aggregated_keywords)} keywords"
        )

        return summary

    @staticmethod
    def _deduplicate(items: List[RawItem]) -> List[RawItem]:
        """根据URL去重"""
        seen_urls = set()
        unique = []

        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique.append(item)

        return unique

    @staticmethod
    def _convert_to_jds(
        items: List[RawItem],
        domain: str,
        max_count: int
    ) -> List[JobDescription]:
        """
        将RawItem转换为JobDescription

        主要从GitHub项目和技术文章中推断技能要求
        """
        jds = []

        for item in items[:max_count * 2]:  # 多取一些以便过滤
            try:
                # 从tags提取技术栈
                keywords = [tag for tag in item.tags if tag]

                # 从snippet提取要求
                requirements = TrendAggregator._extract_requirements(item)

                if not keywords and not requirements:
                    continue

                # 生成JD
                jd = JobDescription(
                    company=f"技术趋势来源 ({item.source.upper()})",
                    position=f"{domain} - 相关技术岗位",
                    location="全国",
                    salary_range="面议",
                    requirements=requirements[:5],  # 最多5条要求
                    responsibilities=[
                        f"基于 {item.title} 相关技术的开发和应用",
                        "参与技术选型和架构设计",
                        "保持对新技术的学习和实践"
                    ],
                    keywords=keywords[:10],  # 最多10个关键词
                    source_url=item.url,
                    crawled_at=item.crawled_at
                )

                jds.append(jd)

                if len(jds) >= max_count:
                    break

            except Exception as e:
                logger.warning(f"Failed to convert item to JD: {e}")
                continue

        return jds

    @staticmethod
    def _convert_to_experiences(
        items: List[RawItem],
        domain: str,
        max_count: int
    ) -> List[InterviewExperience]:
        """
        将RawItem转换为InterviewExperience

        主要从CSDN面试文章中提取
        """
        experiences = []

        # 优先处理面试相关的内容
        interview_items = [
            item for item in items
            if item.metadata.get('is_interview') == 'True'
        ]

        for item in interview_items[:max_count]:
            try:
                # 从snippet推断问题
                questions = TrendAggregator._extract_questions_from_text(item.snippet)

                if not questions:
                    # 生成一些通用问题基于标题
                    questions = [
                        f"请介绍 {item.title} 相关的项目经验",
                        f"{domain} 领域的核心技术栈有哪些？",
                        "遇到过哪些技术难点，如何解决的？"
                    ]

                # 提取主题
                topics = item.tags[:5]

                exp = InterviewExperience(
                    company="技术社区面经汇总 (CSDN)",
                    position=f"{domain} - 技术岗位",
                    interview_type="技术面",
                    questions=questions[:6],  # 最多6个问题
                    difficulty="中等",
                    topics=topics,
                    tips=f"参考资料：{item.title}",
                    source_url=item.url,
                    shared_at=item.crawled_at
                )

                experiences.append(exp)

            except Exception as e:
                logger.warning(f"Failed to convert item to experience: {e}")
                continue

        return experiences

    @staticmethod
    def _extract_keywords(items: List[RawItem], max_count: int) -> List[str]:
        """提取和聚合关键词"""
        all_keywords = []

        for item in items:
            all_keywords.extend(item.tags)

        # 计数并排序
        keyword_counter = Counter(all_keywords)

        # 过滤太短的关键词
        filtered_keywords = [
            (kw, count) for kw, count in keyword_counter.items()
            if len(kw) > 1 and kw not in ['技术', '开发', '系统']
        ]

        # 按频率排序
        top_keywords = [kw for kw, _ in sorted(filtered_keywords, key=lambda x: x[1], reverse=True)]

        return top_keywords[:max_count]

    @staticmethod
    def _extract_topics(items: List[RawItem], max_topics: int) -> List[str]:
        """提取主题"""
        all_topics = []

        for item in items:
            # 从metadata提取
            if 'search_keyword' in item.metadata:
                all_topics.append(item.metadata['search_keyword'])

            # 从tags提取
            all_topics.extend(item.tags[:3])

        # 去重并计数
        topic_counter = Counter(all_topics)
        top_topics = [topic for topic, _ in topic_counter.most_common(max_topics)]

        return top_topics

    @staticmethod
    def _extract_questions(items: List[RawItem], max_questions: int) -> List[str]:
        """从面试相关文章中提取高频问题"""
        questions = []

        for item in items:
            if item.metadata.get('is_interview') == 'True':
                extracted = TrendAggregator._extract_questions_from_text(
                    f"{item.title} {item.snippet}"
                )
                questions.extend(extracted)

        # 去重（保持顺序）
        seen = set()
        unique_questions = []
        for q in questions:
            if q not in seen and len(q) > 10:  # 过滤太短的
                seen.add(q)
                unique_questions.append(q)

        return unique_questions[:max_questions]

    @staticmethod
    def _extract_requirements(item: RawItem) -> List[str]:
        """从RawItem提取技能要求"""
        requirements = []

        # 基于tags生成要求
        if item.tags:
            tech_stack = ', '.join(item.tags[:3])
            requirements.append(f"熟悉 {tech_stack} 等技术")

        # 从snippet提取
        snippet_lower = item.snippet.lower()

        if any(lang in snippet_lower for lang in ['python', 'java', 'go', 'javascript']):
            requirements.append("具备扎实的编程基础")

        if any(kw in snippet_lower for kw in ['distributed', '分布式', 'microservice', '微服务']):
            requirements.append("有分布式系统开发经验")

        if any(kw in snippet_lower for kw in ['high performance', '高性能', 'scalable', '可扩展']):
            requirements.append("关注系统性能和可扩展性")

        return requirements

    @staticmethod
    def _extract_questions_from_text(text: str) -> List[str]:
        """从文本中提取面试问题"""
        questions = []

        # 匹配问题模式（带问号）
        question_patterns = [
            r'[？?]',  # 问号结尾
            r'\d+[.、][\s]*(.*?[？?])',  # 编号问题
        ]

        # 按句子分割
        sentences = re.split(r'[。！\n]', text)

        for sentence in sentences:
            sentence = sentence.strip()

            # 检查是否包含问号
            if '？' in sentence or '?' in sentence:
                # 清理并添加
                cleaned = sentence.strip()
                if 10 < len(cleaned) < 200:  # 合理长度
                    questions.append(cleaned)

        return questions[:10]
