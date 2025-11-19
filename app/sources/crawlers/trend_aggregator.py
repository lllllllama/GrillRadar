"""
趋势聚合器 / Trend Aggregator

将多源RawItem数据聚合、清洗、转换为ExternalInfoSummary

优化版本 (V2):
- 智能去重（URL + 标题相似度）
- 多源加权评分（GitHub/V2EX/IT之家）
- 时序优先（新鲜度加分）
- 质量过滤
"""
from typing import List, Dict, Tuple
from collections import Counter
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher

from app.sources.crawlers.models import RawItem
from app.models.external_info import (
    ExternalInfoSummary,
    JobDescription,
    InterviewExperience
)

import logging
logger = logging.getLogger(__name__)


class TrendAggregator:
    """趋势聚合器 V2 - 优化版"""

    # 数据源权重配置
    SOURCE_WEIGHTS = {
        'github': 1.5,     # GitHub项目权重高（代码质量和stars说明价值）
        'v2ex': 1.2,       # V2EX讨论权重中等（实时讨论有价值）
        'ithome': 1.0,     # IT之家新闻权重中等（新闻时效性）
        'csdn': 0.8,       # CSDN权重较低（内容质量参差）
        'juejin': 1.0,     # 掘金权重中等
        'zhihu': 1.1,      # 知乎权重较高（专业内容多）
    }

    # 内容类型权重
    CONTENT_TYPE_WEIGHTS = {
        'code': 1.5,       # 代码/项目
        'discussion': 1.2, # 技术讨论
        'news': 1.0,       # 新闻
        'article': 1.1,    # 文章
        'interview': 1.3,  # 面试经验
    }

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

        # 1. 智能去重（URL + 标题相似度）
        unique_items = TrendAggregator._deduplicate_smart(raw_items)
        logger.info(f"After smart deduplication: {len(unique_items)} items")

        # 2. 计算质量分数（综合评分）
        for item in unique_items:
            item.metadata['quality_score'] = TrendAggregator._calculate_quality_score(item)

        # 3. 按质量分数排序
        unique_items.sort(key=lambda x: x.metadata.get('quality_score', 0), reverse=True)

        # 4. 分组：技术项目 vs 讨论 vs 新闻 vs 文章
        github_items = [item for item in unique_items if item.source == 'github']
        v2ex_items = [item for item in unique_items if item.source == 'v2ex']
        ithome_items = [item for item in unique_items if item.source == 'ithome']
        csdn_items = [item for item in unique_items if item.source == 'csdn']

        # 5. 转换为JD和面经
        # JD来源：GitHub项目 + V2EX讨论 + IT之家新闻 + CSDN文章
        jd_source_items = github_items + v2ex_items[:3] + ithome_items[:3] + csdn_items[:5]
        job_descriptions = TrendAggregator._convert_to_jds(
            jd_source_items,
            domain,
            max_jd
        )

        # 面经来源：V2EX面试讨论 + CSDN面经文章
        exp_source_items = v2ex_items + csdn_items
        interview_experiences = TrendAggregator._convert_to_experiences(
            exp_source_items,
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
        """根据URL去重（基础版）"""
        seen_urls = set()
        unique = []

        for item in items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique.append(item)

        return unique

    @staticmethod
    def _deduplicate_smart(items: List[RawItem], similarity_threshold: float = 0.85) -> List[RawItem]:
        """
        智能去重：URL + 标题相似度

        Args:
            items: 原始数据项
            similarity_threshold: 标题相似度阈值（0-1），默认0.85

        Returns:
            去重后的数据项列表
        """
        seen_urls = set()
        seen_titles = []
        unique = []

        for item in items:
            # 1. URL精确去重
            if item.url in seen_urls:
                continue

            # 2. 标题相似度去重
            is_duplicate = False
            for prev_title in seen_titles:
                similarity = SequenceMatcher(None, item.title.lower(), prev_title.lower()).ratio()
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    logger.debug(f"Duplicate title detected (similarity={similarity:.2f}): {item.title}")
                    break

            if not is_duplicate:
                seen_urls.add(item.url)
                seen_titles.append(item.title)
                unique.append(item)

        return unique

    @staticmethod
    def _calculate_quality_score(item: RawItem) -> float:
        """
        计算数据项的质量分数（综合评分）

        评分因素：
        1. 数据源权重 (SOURCE_WEIGHTS)
        2. 内容类型权重 (CONTENT_TYPE_WEIGHTS)
        3. 互动分数 (engagement: stars, likes, views, comments)
        4. 新鲜度加分 (created_at, crawled_at)

        Returns:
            float: 质量分数 (0-100+)
        """
        score = 0.0

        # 1. 基础分
        score += 10.0

        # 2. 数据源权重
        source_weight = TrendAggregator.SOURCE_WEIGHTS.get(item.source, 1.0)
        score *= source_weight

        # 3. 内容类型权重
        content_type = item.metadata.get('content_type', 'article')
        content_weight = TrendAggregator.CONTENT_TYPE_WEIGHTS.get(content_type, 1.0)
        score *= content_weight

        # 4. 互动分数（归一化到0-50分）
        engagement_score = item.get_engagement_score()
        # 对数归一化，避免极端值主导
        import math
        normalized_engagement = min(50.0, math.log10(max(1, engagement_score)) * 10)
        score += normalized_engagement

        # 5. 新鲜度加分（最近7天的内容加分）
        if item.created_at:
            age_days = (datetime.utcnow() - item.created_at).days
            if age_days <= 1:
                score *= 1.3  # 24小时内 +30%
            elif age_days <= 3:
                score *= 1.2  # 3天内 +20%
            elif age_days <= 7:
                score *= 1.1  # 7天内 +10%
        elif item.crawled_at:
            # 如果没有created_at，用crawled_at估算
            age_days = (datetime.utcnow() - item.crawled_at).days
            if age_days == 0:
                score *= 1.1  # 今天爬取的内容 +10%

        # 6. 标题长度合理性（太短或太长都扣分）
        title_len = len(item.title)
        if title_len < 10:
            score *= 0.7  # 标题太短
        elif title_len > 150:
            score *= 0.8  # 标题太长

        # 7. 有tags加分
        if item.tags:
            score += min(10.0, len(item.tags) * 2)  # 每个tag +2分，最多+10分

        return round(score, 2)

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

                # 根据来源生成更具体的公司名
                company_names = {
                    'github': 'GitHub热门项目',
                    'v2ex': 'V2EX技术社区',
                    'ithome': 'IT之家科技资讯',
                    'csdn': 'CSDN技术社区',
                    'juejin': '掘金技术社区',
                    'zhihu': '知乎技术圈',
                }
                company = company_names.get(item.source, f'{item.source.upper()}')

                # 生成JD
                jd = JobDescription(
                    company=company,
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

        # 优先处理面试相关的内容（CSDN面经 + V2EX讨论）
        interview_items = [
            item for item in items
            if (item.metadata.get('is_interview') == 'True' or
                item.source == 'v2ex' or
                '面试' in item.title or '面经' in item.title)
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

                # 根据来源确定公司名
                source_names = {
                    'csdn': 'CSDN技术社区',
                    'v2ex': 'V2EX技术社区',
                    'juejin': '掘金技术社区',
                    'zhihu': '知乎技术圈',
                }
                company = source_names.get(item.source, '技术社区')

                exp = InterviewExperience(
                    company=company,
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
