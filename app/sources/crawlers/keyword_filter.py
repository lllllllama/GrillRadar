"""
关键词过滤器 / Keyword Filter

TrendRadar风格的关键词过滤语法：
- normal_word: 普通关键词（可选，增加相关性分数）
- +required_word: 必须包含的关键词
- !exclude_word: 必须排除的关键词
"""
from typing import List, Set, Tuple
import re


class KeywordFilter:
    """
    关键词过滤器

    支持TrendRadar风格的语法：
    - "Python" - 普通关键词（可选）
    - "+必须" - 必须包含
    - "!排除" - 必须不包含

    示例:
        filter = KeywordFilter(["Python", "+后端", "!前端"])
        filter.matches("Python后端开发工程师")  # True (有Python, 有后端)
        filter.matches("前端开发")  # False (有排除词"前端")
        filter.matches("Java后端")  # True (有必须词"后端", 虽然没有Python)
    """

    def __init__(self, keywords: List[str]):
        """
        初始化关键词过滤器

        Args:
            keywords: 关键词列表，支持 +required 和 !exclude 前缀
        """
        self.normal_keywords: Set[str] = set()
        self.required_keywords: Set[str] = set()
        self.exclude_keywords: Set[str] = set()

        # 解析关键词
        for keyword in keywords:
            if not keyword:
                continue

            keyword = keyword.strip()

            if keyword.startswith('+'):
                # 必须包含的关键词
                self.required_keywords.add(keyword[1:].strip())
            elif keyword.startswith('!'):
                # 必须排除的关键词
                self.exclude_keywords.add(keyword[1:].strip())
            else:
                # 普通关键词
                self.normal_keywords.add(keyword)

    def matches(self, text: str, case_sensitive: bool = False) -> bool:
        """
        判断文本是否匹配过滤条件

        Args:
            text: 待检测的文本
            case_sensitive: 是否区分大小写（默认不区分）

        Returns:
            bool: 是否匹配
        """
        if not text:
            return False

        # 转换大小写
        if not case_sensitive:
            text = text.lower()

        # 1. 检查排除关键词（任意一个存在就排除）
        for exclude_kw in self.exclude_keywords:
            check_kw = exclude_kw if case_sensitive else exclude_kw.lower()
            if check_kw in text:
                return False

        # 2. 检查必须包含的关键词（全部都要存在）
        for required_kw in self.required_keywords:
            check_kw = required_kw if case_sensitive else required_kw.lower()
            if check_kw not in text:
                return False

        # 3. 通过了排除和必须关键词的检查，就匹配
        # 注意：普通关键词只影响分数，不影响是否匹配
        return True

    def calculate_score(self, text: str, case_sensitive: bool = False) -> float:
        """
        计算文本的相关性分数

        Args:
            text: 待评分的文本
            case_sensitive: 是否区分大小写（默认不区分）

        Returns:
            float: 相关性分数（0-100），不匹配返回0
        """
        if not self.matches(text, case_sensitive):
            return 0.0

        score = 0.0

        # 转换大小写
        if not case_sensitive:
            text = text.lower()

        # 必须关键词: 每个 +20 分
        for required_kw in self.required_keywords:
            check_kw = required_kw if case_sensitive else required_kw.lower()
            if check_kw in text:
                score += 20.0

        # 普通关键词: 每个 +10 分
        for normal_kw in self.normal_keywords:
            check_kw = normal_kw if case_sensitive else normal_kw.lower()
            if check_kw in text:
                score += 10.0

        # 基础分
        score += 10.0

        # 最高100分
        return min(score, 100.0)

    def filter_items(
        self,
        items: List[dict],
        text_field: str = 'title',
        score_field: str = 'relevance_score',
        min_score: float = 0.0
    ) -> List[dict]:
        """
        过滤并评分数据项

        Args:
            items: 数据项列表
            text_field: 用于匹配的文本字段名（默认 'title'）
            score_field: 添加分数的字段名（默认 'relevance_score'）
            min_score: 最低分数阈值（默认0，即只要匹配就保留）

        Returns:
            List[dict]: 过滤并评分后的数据项（按分数降序排列）
        """
        filtered = []

        for item in items:
            # 获取文本
            text = item.get(text_field, '')
            if not text:
                continue

            # 计算分数
            score = self.calculate_score(text)

            if score > min_score:
                # 创建副本并添加分数
                item_copy = item.copy()
                item_copy[score_field] = score
                filtered.append(item_copy)

        # 按分数降序排列
        filtered.sort(key=lambda x: x.get(score_field, 0), reverse=True)

        return filtered

    def __repr__(self) -> str:
        """字符串表示"""
        parts = []
        if self.required_keywords:
            parts.append(f"required={list(self.required_keywords)}")
        if self.exclude_keywords:
            parts.append(f"exclude={list(self.exclude_keywords)}")
        if self.normal_keywords:
            parts.append(f"normal={list(self.normal_keywords)}")

        return f"KeywordFilter({', '.join(parts)})"

    @property
    def is_empty(self) -> bool:
        """是否为空过滤器（没有任何关键词）"""
        return (
            not self.normal_keywords and
            not self.required_keywords and
            not self.exclude_keywords
        )

    @staticmethod
    def parse_keyword_string(keyword_string: str) -> List[str]:
        """
        解析关键词字符串（空格或逗号分隔）

        Args:
            keyword_string: 关键词字符串，如 "Python +后端 !前端,Java"

        Returns:
            List[str]: 关键词列表

        Example:
            >>> KeywordFilter.parse_keyword_string("Python +后端 !前端,Java")
            ['Python', '+后端', '!前端', 'Java']
        """
        if not keyword_string:
            return []

        # 替换逗号为空格
        keyword_string = keyword_string.replace(',', ' ')

        # 分割并去除空白
        keywords = [kw.strip() for kw in keyword_string.split() if kw.strip()]

        return keywords


# 便捷函数
def create_filter(keywords: List[str]) -> KeywordFilter:
    """
    创建关键词过滤器的便捷函数

    Args:
        keywords: 关键词列表

    Returns:
        KeywordFilter: 关键词过滤器实例
    """
    return KeywordFilter(keywords)


def create_filter_from_string(keyword_string: str) -> KeywordFilter:
    """
    从字符串创建关键词过滤器

    Args:
        keyword_string: 关键词字符串

    Returns:
        KeywordFilter: 关键词过滤器实例
    """
    keywords = KeywordFilter.parse_keyword_string(keyword_string)
    return KeywordFilter(keywords)
