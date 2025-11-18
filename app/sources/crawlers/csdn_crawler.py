"""
CSDN爬虫 / CSDN Crawler

抓取CSDN技术文章和面试题，获取中文技术社区的热门话题和面试经验
"""
from typing import List
import re
import time
from bs4 import BeautifulSoup
from app.sources.crawlers.base_crawler import BaseCrawler
from app.sources.crawlers.models import RawItem, CrawlerResult

import logging
logger = logging.getLogger(__name__)


class CSDNCrawler(BaseCrawler):
    """CSDN爬虫"""

    # 领域到CSDN搜索关键词的映射
    DOMAIN_KEYWORDS = {
        # 工程领域
        'backend': ['后端开发', '微服务', '分布式系统', 'Java面试'],
        'frontend': ['前端开发', 'Vue', 'React', '前端面试'],
        'llm_application': ['大模型', 'LLM', 'RAG', 'ChatGPT应用'],
        'algorithm': ['算法工程师', '推荐系统', '搜索算法'],
        'data_engineering': ['数据工程', 'ETL', '数据仓库'],
        'mobile': ['Android开发', 'iOS开发', '移动开发'],
        'cloud_native': ['云原生', 'Kubernetes', 'Docker'],
        'embedded': ['嵌入式开发', '物联网', 'STM32'],
        'game_dev': ['游戏开发', 'Unity', '游戏引擎'],
        'blockchain': ['区块链', '智能合约', 'Web3'],
        'security': ['网络安全', '渗透测试', '安全漏洞'],
        'test_qa': ['软件测试', '自动化测试', '测试开发'],

        # 研究领域
        'cv_segmentation': ['图像分割', '语义分割', '实例分割'],
        'cv_detection': ['目标检测', 'YOLO', '检测算法'],
        'nlp': ['自然语言处理', 'NLP', 'BERT', 'Transformer'],
        'multimodal': ['多模态学习', '视觉语言模型'],
        'general_ml': ['机器学习', '深度学习', '神经网络'],
        'reinforcement_learning': ['强化学习', 'RL', '深度强化学习'],
        'robotics': ['机器人', 'SLAM', 'ROS'],
        'graph_learning': ['图神经网络', 'GNN', '知识图谱'],
        'time_series': ['时间序列', '时序预测', '异常检测'],
        'federated_learning': ['联邦学习', '隐私计算', '差分隐私'],
        'ai_safety': ['AI安全', '模型可解释性', '对抗样本'],
    }

    @property
    def source_name(self) -> str:
        return "csdn"

    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        """
        抓取CSDN数据

        Args:
            domain: 领域名称
            keywords: 额外关键词

        Returns:
            CrawlerResult
        """
        start_time = time.time()

        # 检查缓存
        cache_key = self._get_cache_key(domain, keywords)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result

        items = []

        try:
            # 1. 获取领域默认关键词
            domain_keywords = self.DOMAIN_KEYWORDS.get(domain, [])
            all_keywords = list(set(domain_keywords + keywords))[:3]  # 最多3个关键词

            self.logger.info(f"Crawling CSDN for domain '{domain}' with keywords: {all_keywords}")

            # 2. 重点抓取面试相关文章
            for keyword in all_keywords[:2]:  # 最多搜索2个关键词
                # 搜索面试题
                interview_items = self._crawl_search(f"{keyword} 面试题")
                items.extend(interview_items[:5])

                # 搜索技术深度文章
                tech_items = self._crawl_search(f"{keyword} 原理")
                items.extend(tech_items[:3])

            # 3. 去重
            seen_urls = set()
            unique_items = []
            for item in items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    unique_items.append(item)

            # 4. 按浏览量/点赞数排序，取top N
            unique_items.sort(key=lambda x: x.get_engagement_score(), reverse=True)
            unique_items = unique_items[:self.config.max_items]

            duration_ms = int((time.time() - start_time) * 1000)

            result = CrawlerResult(
                source=self.source_name,
                items=unique_items,
                success=True,
                crawled_count=len(unique_items),
                duration_ms=duration_ms
            )

            # 保存到缓存
            self._save_to_cache(cache_key, result)

            self.logger.info(f"CSDN crawl completed: {len(unique_items)} items in {duration_ms}ms")
            return result

        except Exception as e:
            self.logger.error(f"CSDN crawl failed: {e}", exc_info=True)
            duration_ms = int((time.time() - start_time) * 1000)
            return CrawlerResult(
                source=self.source_name,
                items=[],
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    def _crawl_search(self, keyword: str) -> List[RawItem]:
        """
        抓取CSDN搜索结果

        Args:
            keyword: 搜索关键词

        Returns:
            RawItem列表
        """
        items = []

        try:
            # CSDN搜索URL
            # 注意：实际URL可能需要调整，这里提供一个示例
            url = f"https://so.csdn.net/so/search?q={keyword}&t=&u="

            response = self._make_request(url)
            if not response:
                return items

            soup = BeautifulSoup(response.text, 'html.parser')

            # CSDN搜索结果的HTML结构（可能会变化，需要根据实际情况调整）
            # 这里提供一个通用的解析逻辑
            article_items = soup.find_all('div', class_='search-list-item')

            if not article_items:
                # 尝试另一种选择器
                article_items = soup.find_all('div', class_='search-item')

            for article in article_items[:8]:  # 每个关键词最多取8篇
                try:
                    # 提取标题和链接
                    title_elem = article.find('a', class_='search-title') or article.find('h3')
                    if not title_elem:
                        continue

                    link = title_elem.get('href', '')
                    title = title_elem.get_text(strip=True)

                    if not link or not title:
                        continue

                    # 确保URL是完整的
                    if not link.startswith('http'):
                        if link.startswith('/'):
                            link = f"https://blog.csdn.net{link}"
                        else:
                            continue

                    # 提取摘要
                    desc_elem = article.find('div', class_='search-desc') or article.find('p')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    # 提取浏览量、点赞数等
                    view_count = 0
                    like_count = 0

                    # 尝试提取浏览量
                    view_elem = article.find('span', class_='view-num')
                    if view_elem:
                        view_text = view_elem.get_text(strip=True)
                        view_count = self._parse_csdn_number(view_text)

                    # 尝试提取点赞数
                    like_elem = article.find('span', class_='like-num')
                    if like_elem:
                        like_text = like_elem.get_text(strip=True)
                        like_count = self._parse_csdn_number(like_text)

                    # 提取标签
                    tags = self._extract_keywords_from_text(f"{title} {description}")

                    # 判断是否为面试相关
                    is_interview = any(kw in title or kw in description
                                     for kw in ['面试', '八股', '面经', '笔试'])

                    item = RawItem(
                        source="csdn",
                        url=link,
                        title=title,
                        snippet=description[:300],
                        tags=list(set(tags)),
                        engagement={
                            'view': view_count,
                            'like': like_count
                        },
                        metadata={
                            'search_keyword': keyword,
                            'is_interview': str(is_interview)
                        }
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Failed to parse CSDN article: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to search CSDN for '{keyword}': {e}")

        return items

    def _parse_csdn_number(self, text: str) -> int:
        """
        解析CSDN的数字格式

        Args:
            text: 数字文本（如 "1234", "1.2万"）

        Returns:
            整数值
        """
        text = text.strip().replace(',', '')

        # 匹配中文数字格式：1.2万, 3.4千
        match = re.search(r'([\d.]+)\s*([万千]?)', text)
        if not match:
            # 尝试直接提取数字
            num_match = re.search(r'\d+', text)
            if num_match:
                return int(num_match.group())
            return 0

        number = float(match.group(1))
        unit = match.group(2)

        if unit == '万':
            return int(number * 10000)
        elif unit == '千':
            return int(number * 1000)
        else:
            return int(number)
