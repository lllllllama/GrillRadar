"""JSON Data Provider - TrendRadar-style information acquisition

This module provides real data from JSON files with keyword frequency analysis.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import Counter
from datetime import datetime

from app.models.external_info import JobDescription, InterviewExperience

logger = logging.getLogger(__name__)


class JSONDataProvider:
    """Provides JD and interview data from JSON files with trend analysis"""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize JSON data provider

        Args:
            data_dir: Directory containing JSON data files
        """
        if data_dir is None:
            # Default to app/sources/data/
            data_dir = Path(__file__).parent / "data"

        self.data_dir = data_dir
        self.jd_file = data_dir / "jd_database.json"
        self.interview_file = data_dir / "interview_database.json"

        # Load data
        self._load_data()

    def _load_data(self):
        """Load data from JSON files"""
        try:
            # Load JD database
            with open(self.jd_file, 'r', encoding='utf-8') as f:
                jd_data = json.load(f)
                self.jds = [self._parse_jd(jd) for jd in jd_data.get('job_descriptions', [])]
                logger.info(f"Loaded {len(self.jds)} JDs from {self.jd_file}")

            # Load interview database
            with open(self.interview_file, 'r', encoding='utf-8') as f:
                interview_data = json.load(f)
                self.experiences = [
                    self._parse_experience(exp)
                    for exp in interview_data.get('interview_experiences', [])
                ]
                logger.info(f"Loaded {len(self.experiences)} interview experiences from {self.interview_file}")

        except FileNotFoundError as e:
            logger.error(f"Data file not found: {e}")
            self.jds = []
            self.experiences = []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            self.jds = []
            self.experiences = []
        except Exception as e:
            logger.error(f"Failed to load data: {e}", exc_info=True)
            self.jds = []
            self.experiences = []

    def _parse_jd(self, jd_dict: Dict) -> JobDescription:
        """Parse JD from dictionary"""
        # Parse crawled_at timestamp
        crawled_at = None
        if 'crawled_at' in jd_dict:
            try:
                crawled_at = datetime.fromisoformat(jd_dict['crawled_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                crawled_at = None

        return JobDescription(
            company=jd_dict['company'],
            position=jd_dict['position'],
            location=jd_dict.get('location'),
            salary_range=jd_dict.get('salary_range'),
            requirements=jd_dict.get('requirements', []),
            responsibilities=jd_dict.get('responsibilities', []),
            keywords=jd_dict.get('keywords', []),
            source_url=jd_dict.get('source_url'),
            crawled_at=crawled_at
        )

    def _parse_experience(self, exp_dict: Dict) -> InterviewExperience:
        """Parse interview experience from dictionary"""
        # Parse shared_at timestamp
        shared_at = None
        if 'shared_at' in exp_dict:
            try:
                shared_at = datetime.fromisoformat(exp_dict['shared_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                shared_at = None

        return InterviewExperience(
            company=exp_dict['company'],
            position=exp_dict['position'],
            interview_type=exp_dict['interview_type'],
            questions=exp_dict.get('questions', []),
            difficulty=exp_dict.get('difficulty'),
            topics=exp_dict.get('topics', []),
            tips=exp_dict.get('tips'),
            source_url=exp_dict.get('source_url'),
            shared_at=shared_at
        )

    def get_jds(
        self,
        company: Optional[str] = None,
        position: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[JobDescription]:
        """
        Get JDs with filtering

        Args:
            company: Filter by company name (fuzzy match)
            position: Filter by position (fuzzy match)
            domain: Filter by domain keywords

        Returns:
            Filtered JD list
        """
        filtered_jds = self.jds

        # Filter by company
        if company:
            filtered_jds = [
                jd for jd in filtered_jds
                if company.lower() in jd.company.lower()
            ]

        # Filter by position
        if position:
            position_keywords = position.lower().split()
            filtered_jds = [
                jd for jd in filtered_jds
                if any(kw in jd.position.lower() for kw in position_keywords)
            ]

        # Filter by domain (check keywords)
        if domain:
            domain_mapping = {
                'backend': ['后端', 'java', 'go', 'python', 'c++'],
                'frontend': ['前端', 'react', 'vue', 'javascript'],
                'ml': ['机器学习', 'machine learning', 'ml'],
                'nlp': ['nlp', '自然语言处理', 'natural language'],
                'cv_segmentation': ['计算机视觉', 'computer vision', '图像分割', 'segmentation']
            }

            domain_keywords = domain_mapping.get(domain, [domain.lower()])
            filtered_jds = [
                jd for jd in filtered_jds
                if any(
                    kw in jd.position.lower() or
                    any(kw in keyword.lower() for keyword in jd.keywords)
                    for kw in domain_keywords
                )
            ]

        logger.info(f"Filtered {len(filtered_jds)}/{len(self.jds)} JDs (company={company}, position={position}, domain={domain})")
        return filtered_jds

    def get_experiences(
        self,
        company: Optional[str] = None,
        position: Optional[str] = None
    ) -> List[InterviewExperience]:
        """
        Get interview experiences with filtering

        Args:
            company: Filter by company name (fuzzy match)
            position: Filter by position (fuzzy match)

        Returns:
            Filtered experience list
        """
        filtered_exps = self.experiences

        # Filter by company
        if company:
            filtered_exps = [
                exp for exp in filtered_exps
                if company.lower() in exp.company.lower()
            ]

        # Filter by position
        if position:
            position_keywords = position.lower().split()
            filtered_exps = [
                exp for exp in filtered_exps
                if any(kw in exp.position.lower() for kw in position_keywords)
            ]

        logger.info(f"Filtered {len(filtered_exps)}/{len(self.experiences)} experiences (company={company}, position={position})")
        return filtered_exps

    def analyze_keyword_frequency(
        self,
        jds: List[JobDescription],
        domain: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Analyze keyword frequency from JDs with domain-specific weighting

        Args:
            jds: List of job descriptions
            domain: Target domain for relevance weighting

        Returns:
            Dictionary of keyword -> frequency count
        """
        keyword_counter = Counter()

        for jd in jds:
            # Count each keyword
            for keyword in jd.keywords:
                keyword_counter[keyword] += 1

        # Domain-specific boosting
        if domain and domain in ['backend', 'frontend', 'ml', 'nlp', 'cv_segmentation']:
            boost_keywords = self._get_domain_boost_keywords(domain)
            for keyword in boost_keywords:
                if keyword in keyword_counter:
                    keyword_counter[keyword] = int(keyword_counter[keyword] * 1.5)  # 50% boost

        return dict(keyword_counter)

    def _get_domain_boost_keywords(self, domain: str) -> List[str]:
        """Get keywords to boost for a specific domain"""
        boost_map = {
            'backend': ['分布式系统', '高并发', '微服务', 'MySQL', 'Redis', 'Kafka'],
            'frontend': ['React', 'Vue', 'TypeScript', 'Webpack', '性能优化'],
            'ml': ['机器学习', '深度学习', 'PyTorch', 'TensorFlow', '模型训练'],
            'nlp': ['NLP', 'Transformer', 'BERT', '大语言模型', 'Prompt工程'],
            'cv_segmentation': ['计算机视觉', '图像分割', 'CNN', 'Transformer', 'PyTorch']
        }
        return boost_map.get(domain, [])

    def get_high_frequency_keywords(
        self,
        jds: List[JobDescription],
        domain: Optional[str] = None,
        top_k: int = 15,
        min_frequency: int = 2
    ) -> List[Tuple[str, int]]:
        """
        Get high-frequency keywords from JDs

        Args:
            jds: List of job descriptions
            domain: Target domain for relevance weighting
            top_k: Return top K keywords
            min_frequency: Minimum frequency threshold

        Returns:
            List of (keyword, frequency) tuples, sorted by frequency
        """
        keyword_freq = self.analyze_keyword_frequency(jds, domain)

        # Filter by minimum frequency
        filtered = {k: v for k, v in keyword_freq.items() if v >= min_frequency}

        # Sort and return top K
        sorted_keywords = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_k]

    def get_trending_topics(
        self,
        experiences: List[InterviewExperience],
        top_k: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Get trending topics from interview experiences

        Args:
            experiences: List of interview experiences
            top_k: Return top K topics

        Returns:
            List of (topic, frequency) tuples
        """
        topic_counter = Counter()

        for exp in experiences:
            for topic in exp.topics:
                topic_counter[topic] += 1

        return topic_counter.most_common(top_k)


# Global singleton
json_data_provider = JSONDataProvider()
