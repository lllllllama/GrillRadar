"""
GitHub爬虫 / GitHub Crawler

抓取GitHub trending和搜索结果，获取热门项目和技术趋势
"""
from typing import List, Dict
import re
import time
from bs4 import BeautifulSoup
from app.sources.crawlers.base_crawler import BaseCrawler
from app.sources.crawlers.models import RawItem, CrawlerResult

import logging
logger = logging.getLogger(__name__)


class GitHubCrawler(BaseCrawler):
    """GitHub爬虫"""

    # 领域到GitHub搜索关键词的映射
    DOMAIN_KEYWORDS = {
        # 工程领域
        'backend': ['backend', 'microservice', 'distributed-system', 'api'],
        'frontend': ['frontend', 'react', 'vue', 'javascript', 'typescript'],
        'llm_application': ['LLM', 'RAG', 'langchain', 'GPT', 'chatbot', 'agent'],
        'algorithm': ['algorithm', 'recommendation', 'search', 'ranking'],
        'data_engineering': ['data-pipeline', 'ETL', 'data-warehouse', 'airflow'],
        'mobile': ['android', 'ios', 'flutter', 'react-native'],
        'cloud_native': ['kubernetes', 'docker', 'k8s', 'devops', 'terraform'],
        'embedded': ['embedded', 'iot', 'arduino', 'raspberry-pi'],
        'game_dev': ['game-engine', 'unity', 'unreal', 'game-development'],
        'blockchain': ['blockchain', 'web3', 'smart-contract', 'defi', 'nft'],
        'security': ['security', 'penetration-testing', 'vulnerability', 'cyber'],
        'test_qa': ['testing', 'automation', 'selenium', 'cypress', 'qa'],

        # 研究领域
        'cv_segmentation': ['segmentation', 'computer-vision', 'semantic-segmentation'],
        'cv_detection': ['object-detection', 'yolo', 'detection', 'computer-vision'],
        'nlp': ['nlp', 'natural-language', 'transformers', 'bert', 'text-generation'],
        'multimodal': ['multimodal', 'vision-language', 'clip', 'vit'],
        'general_ml': ['machine-learning', 'deep-learning', 'neural-network'],
        'reinforcement_learning': ['reinforcement-learning', 'rl', 'policy-gradient'],
        'robotics': ['robotics', 'slam', 'ros', 'robot'],
        'graph_learning': ['graph-neural-network', 'gnn', 'knowledge-graph'],
        'time_series': ['time-series', 'forecasting', 'anomaly-detection'],
        'federated_learning': ['federated-learning', 'differential-privacy'],
        'ai_safety': ['ai-safety', 'alignment', 'interpretability', 'explainability'],
    }

    @property
    def source_name(self) -> str:
        return "github"

    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        """
        抓取GitHub数据

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

            self.logger.info(f"Crawling GitHub for domain '{domain}' with keywords: {all_keywords}")

            # 2. 抓取trending repositories (不过滤语言，获取全部trending)
            trending_items = self._crawl_trending(language=None)
            items.extend(trending_items)

            # 3. 抓取搜索结果
            if all_keywords:
                search_items = self._crawl_search(all_keywords[:2])  # 最多搜索2个关键词
                items.extend(search_items)

            # 4. 去重（根据URL）
            seen_urls = set()
            unique_items = []
            for item in items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    unique_items.append(item)

            # 5. 按star数排序，取top N
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

            self.logger.info(f"GitHub crawl completed: {len(unique_items)} items in {duration_ms}ms")
            return result

        except Exception as e:
            self.logger.error(f"GitHub crawl failed: {e}", exc_info=True)
            duration_ms = int((time.time() - start_time) * 1000)
            return CrawlerResult(
                source=self.source_name,
                items=[],
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    def _crawl_trending(self, language: str = 'python') -> List[RawItem]:
        """
        抓取GitHub Trending页面

        Args:
            language: 编程语言过滤

        Returns:
            RawItem列表
        """
        items = []

        try:
            # GitHub Trending URL (不使用语言过滤，获取所有trending)
            url = "https://github.com/trending?since=daily"

            response = self._make_request(url)
            if not response:
                return items

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找trending repositories
            repo_articles = soup.find_all('article', class_='Box-row')

            for article in repo_articles[:10]:  # 最多取10个
                try:
                    # 提取repo名称和URL
                    h2 = article.find('h2', class_='h3')
                    if not h2:
                        continue

                    link = h2.find('a')
                    if not link:
                        continue

                    repo_path = link.get('href', '').strip()
                    repo_url = f"https://github.com{repo_path}"
                    repo_name = repo_path.strip('/')

                    # 提取描述
                    desc_p = article.find('p', class_='col-9')
                    description = desc_p.get_text(strip=True) if desc_p else ""

                    # 提取star数 - 在stargazers链接中
                    star_link = article.find('a', href=lambda x: x and '/stargazers' in x)
                    star_text = star_link.get_text(strip=True) if star_link else "0"
                    star_count = self._parse_github_number(star_text)

                    # 提取语言 - 在repo-language-color之后的文本
                    lang_color = article.find('span', class_='repo-language-color')
                    language_name = "Unknown"
                    if lang_color and lang_color.next_sibling:
                        # 语言名通常紧随颜色点之后
                        lang_text = lang_color.next_sibling
                        if isinstance(lang_text, str):
                            language_name = lang_text.strip()
                        elif hasattr(lang_text, 'get_text'):
                            language_name = lang_text.get_text(strip=True)

                    # 提取标签
                    tags = self._extract_keywords_from_text(f"{repo_name} {description}")
                    tags.append(language_name)

                    item = RawItem(
                        source="github",
                        url=repo_url,
                        title=repo_name,
                        snippet=description[:200],
                        tags=list(set(tags)),
                        engagement={'star': star_count},
                        metadata={'language': language_name, 'type': 'trending'}
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Failed to parse trending repo: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to crawl GitHub trending: {e}")

        return items

    def _crawl_search(self, keywords: List[str]) -> List[RawItem]:
        """
        抓取GitHub搜索结果

        Args:
            keywords: 搜索关键词

        Returns:
            RawItem列表
        """
        items = []

        for keyword in keywords[:2]:  # 最多搜索2个关键词
            try:
                # GitHub搜索URL（按star排序）
                url = f"https://github.com/search?q={keyword}&type=repositories&s=stars&o=desc"

                response = self._make_request(url)
                if not response:
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')

                # 查找搜索结果
                repo_items = soup.find_all('div', class_='Box-sc')

                for repo_div in repo_items[:5]:  # 每个关键词最多取5个
                    try:
                        # 查找repo链接
                        link = repo_div.find('a', class_='v-align-middle')
                        if not link:
                            continue

                        repo_path = link.get('href', '').strip()
                        if not repo_path.startswith('/'):
                            continue

                        repo_url = f"https://github.com{repo_path}"
                        repo_name = repo_path.strip('/')

                        # 提取描述
                        desc_elem = repo_div.find('p', class_='mb-1')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""

                        # 提取star数（搜索结果页面格式可能不同）
                        star_count = 0
                        star_link = repo_div.find('a', href=re.compile(r'/stargazers$'))
                        if star_link:
                            star_text = star_link.get_text(strip=True)
                            star_count = self._parse_github_number(star_text)

                        # 提取标签
                        tags = self._extract_keywords_from_text(f"{repo_name} {description}")
                        tags.append(keyword)

                        item = RawItem(
                            source="github",
                            url=repo_url,
                            title=repo_name,
                            snippet=description[:200],
                            tags=list(set(tags)),
                            engagement={'star': star_count},
                            metadata={'search_keyword': keyword, 'type': 'search'}
                        )

                        items.append(item)

                    except Exception as e:
                        self.logger.warning(f"Failed to parse search result: {e}")
                        continue

            except Exception as e:
                self.logger.error(f"Failed to search GitHub for '{keyword}': {e}")
                continue

        return items

    def _parse_github_number(self, text: str) -> int:
        """
        解析GitHub的数字格式（如 "1.2k", "234"）

        Args:
            text: 数字文本

        Returns:
            整数值
        """
        text = text.strip().replace(',', '')

        # 匹配 1.2k, 3.4m 等格式
        match = re.search(r'([\d.]+)([km]?)', text.lower())
        if not match:
            return 0

        number = float(match.group(1))
        unit = match.group(2)

        if unit == 'k':
            return int(number * 1000)
        elif unit == 'm':
            return int(number * 1000000)
        else:
            return int(number)
