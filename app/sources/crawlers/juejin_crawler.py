"""
掘金(Juejin)爬虫 - 获取技术文章和面试经验
"""
import logging
import time
from typing import List
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .models import RawItem, CrawlerResult
from .anti_detection import AntiDetectionHelper


class JuejinCrawler(BaseCrawler):
    """掘金爬虫 - 专注技术文章和面试经验"""

    @property
    def source_name(self) -> str:
        return "juejin"

    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger("JuejinCrawler")
        self.anti_detect = AntiDetectionHelper()

        # 掘金关键词映射
        self.domain_keywords_map = {
            # 工程领域
            'backend': ['后端开发', 'Spring', 'Node.js', '微服务'],
            'frontend': ['前端开发', 'React', 'Vue', 'TypeScript'],
            'ios': ['iOS开发', 'Swift', 'SwiftUI'],
            'android': ['Android开发', 'Kotlin', 'Jetpack'],
            'llm_application': ['大模型', 'LLM', 'ChatGPT', 'RAG'],
            'cv_classification': ['计算机视觉', 'CNN', '图像分类'],
            'cv_detection': ['目标检测', 'YOLO', 'Faster RCNN'],
            'cv_segmentation': ['图像分割', '语义分割', 'UNet'],
            'nlp': ['NLP', '自然语言处理', 'BERT', 'Transformer'],
            'recommendation': ['推荐系统', '协同过滤', '召回排序'],
            'search': ['搜索引擎', 'Elasticsearch', '全文检索'],
            # 研究领域...
        }

    def crawl(self, domain: str = None, keywords: List[str] = None) -> CrawlerResult:
        """
        爬取掘金文章

        Args:
            domain: 领域
            keywords: 关键词列表

        Returns:
            CrawlerResult
        """
        start_time = time.time()
        items = []

        try:
            # 1. 获取领域关键词
            domain_keywords = self.domain_keywords_map.get(domain, [])
            all_keywords = list(set(domain_keywords + (keywords or [])))[:3]

            self.logger.info(f"Crawling Juejin for domain '{domain}' with keywords: {all_keywords}")

            # 2. 搜索文章
            for keyword in all_keywords:
                try:
                    search_items = self._search_articles(keyword)
                    items.extend(search_items)

                    # 睡眠避免过快请求
                    time.sleep(self.config.sleep_between_requests)
                except Exception as e:
                    self.logger.warning(f"Failed to search Juejin for '{keyword}': {e}")
                    continue

            # 3. 去重
            seen_urls = set()
            unique_items = []
            for item in items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    unique_items.append(item)

            # 4. 限制数量
            unique_items = unique_items[:self.config.max_items]

            duration_ms = int((time.time() - start_time) * 1000)

            result = CrawlerResult(
                source=self.source_name,
                items=unique_items,
                success=True,
                crawled_count=len(unique_items),
                duration_ms=duration_ms
            )

            # 保存缓存
            self._save_to_cache(f"{domain}_{','.join(all_keywords)}", result)

            self.logger.info(f"Juejin crawl completed: {len(unique_items)} items in {duration_ms}ms")
            return result

        except Exception as e:
            self.logger.error(f"Juejin crawl failed: {e}", exc_info=True)
            duration_ms = int((time.time() - start_time) * 1000)
            return CrawlerResult(
                source=self.source_name,
                items=[],
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    def _search_articles(self, keyword: str) -> List[RawItem]:
        """
        搜索掘金文章

        Args:
            keyword: 搜索关键词

        Returns:
            RawItem列表
        """
        items = []

        try:
            # 掘金搜索URL
            url = f"https://juejin.cn/search?query={quote(keyword)}&type=0"

            # 使用反检测工具获取完整的浏览器请求头
            headers = self.anti_detect.get_browser_headers(
                referer='https://juejin.cn/',
                accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            )

            # 添加随机延迟
            delay = self.anti_detect.get_random_delay(0.5, 1.5)
            time.sleep(delay)

            response = self._make_request(url, headers=headers)
            if not response:
                return items

            soup = BeautifulSoup(response.text, 'html.parser')

            # 掘金文章卡片
            # 注意：这里的选择器需要根据实际页面结构调整
            article_cards = soup.find_all('div', class_='result-item')[:10]

            for card in article_cards:
                try:
                    # 提取标题和链接
                    title_elem = card.find('a', class_='title')
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    article_url = 'https://juejin.cn' + title_elem.get('href', '')

                    # 提取摘要
                    summary_elem = card.find('div', class_='abstract')
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""

                    # 提取作者
                    author_elem = card.find('a', class_='username')
                    author = author_elem.get_text(strip=True) if author_elem else "Unknown"

                    # 提取点赞数
                    like_elem = card.find('span', class_='count')
                    likes = 0
                    if like_elem:
                        like_text = like_elem.get_text(strip=True)
                        likes = self._parse_number(like_text)

                    # 提取标签
                    tags = [keyword]
                    tag_elems = card.find_all('a', class_='tag')
                    for tag_elem in tag_elems[:3]:
                        tag = tag_elem.get_text(strip=True)
                        if tag:
                            tags.append(tag)

                    item = RawItem(
                        source="juejin",
                        url=article_url,
                        title=title,
                        snippet=summary[:200],
                        tags=list(set(tags)),
                        engagement={'likes': likes},
                        metadata={'author': author, 'keyword': keyword}
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Failed to parse Juejin article: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to search Juejin for '{keyword}': {e}")

        return items

    def _parse_number(self, text: str) -> int:
        """解析数字文本（支持k, w等单位）"""
        text = text.strip().lower()
        try:
            if 'w' in text or '万' in text:
                return int(float(text.replace('w', '').replace('万', '')) * 10000)
            elif 'k' in text or '千' in text:
                return int(float(text.replace('k', '').replace('千', '')) * 1000)
            else:
                return int(text)
        except:
            return 0
