"""
知乎(Zhihu)爬虫 - 获取技术问答和文章
"""
import logging
import time
from typing import List
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler
from .models import RawItem, CrawlerResult


class ZhihuCrawler(BaseCrawler):
    """知乎爬虫 - 专注技术问答和经验分享"""

    @property
    def source_name(self) -> str:
        return "zhihu"

    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger("ZhihuCrawler")

        # 知乎关键词映射（添加"面试"、"经验"等词提高相关性）
        self.domain_keywords_map = {
            # 工程领域
            'backend': ['后端面试', 'Java面试', 'Go面试', '微服务'],
            'frontend': ['前端面试', 'React', 'Vue', 'JavaScript'],
            'ios': ['iOS面试', 'Swift开发经验'],
            'android': ['Android面试', 'Kotlin'],
            'llm_application': ['大模型面试', 'LLM应用', 'ChatGPT', 'RAG'],
            'cv_classification': ['计算机视觉面试', '图像分类'],
            'cv_detection': ['目标检测', 'YOLO'],
            'cv_segmentation': ['图像分割', '语义分割'],
            'nlp': ['NLP面试', 'Transformer', 'BERT'],
            'recommendation': ['推荐系统面试', '召回排序'],
            'search': ['搜索引擎', 'Elasticsearch'],
            # 研究领域...
        }

    def crawl(self, domain: str = None, keywords: List[str] = None) -> CrawlerResult:
        """
        爬取知乎问答和文章

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

            self.logger.info(f"Crawling Zhihu for domain '{domain}' with keywords: {all_keywords}")

            # 2. 搜索问答和文章
            for keyword in all_keywords:
                try:
                    search_items = self._search_content(keyword)
                    items.extend(search_items)

                    # 睡眠避免过快请求
                    time.sleep(self.config.sleep_between_requests)
                except Exception as e:
                    self.logger.warning(f"Failed to search Zhihu for '{keyword}': {e}")
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

            self.logger.info(f"Zhihu crawl completed: {len(unique_items)} items in {duration_ms}ms")
            return result

        except Exception as e:
            self.logger.error(f"Zhihu crawl failed: {e}", exc_info=True)
            duration_ms = int((time.time() - start_time) * 1000)
            return CrawlerResult(
                source=self.source_name,
                items=[],
                success=False,
                error_message=str(e),
                duration_ms=duration_ms
            )

    def _search_content(self, keyword: str) -> List[RawItem]:
        """
        搜索知乎内容（问答+文章）

        Args:
            keyword: 搜索关键词

        Returns:
            RawItem列表
        """
        items = []

        try:
            # 知乎搜索URL（使用通用搜索）
            url = f"https://www.zhihu.com/search?type=content&q={quote(keyword)}"

            # 设置headers模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.zhihu.com/',
            }

            response = self._make_request(url, headers=headers)
            if not response:
                return items

            soup = BeautifulSoup(response.text, 'html.parser')

            # 知乎搜索结果卡片
            # 注意：知乎可能会返回React渲染的页面，部分内容在JSON中
            # 这里尝试解析HTML结构
            result_cards = soup.find_all('div', class_='List-item')[:10]

            # 如果没找到，尝试其他选择器
            if not result_cards:
                result_cards = soup.find_all('div', {'data-zop-feedtype': True})[:10]

            for card in result_cards:
                try:
                    # 提取标题和链接
                    title_elem = card.find('h2', class_='ContentItem-title')
                    if not title_elem:
                        title_elem = card.find('a', class_='ContentItem-link')

                    if not title_elem:
                        continue

                    # 获取链接
                    link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                    if not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    content_url = link_elem.get('href', '')
                    if not content_url.startswith('http'):
                        content_url = 'https://www.zhihu.com' + content_url

                    # 提取摘要
                    summary_elem = card.find('div', class_='ContentItem-excerpt')
                    if not summary_elem:
                        summary_elem = card.find('div', class_='RichContent-inner')

                    summary = summary_elem.get_text(strip=True) if summary_elem else ""

                    # 提取点赞数和评论数
                    vote_elem = card.find('button', {'aria-label': lambda x: x and '赞同' in x})
                    votes = 0
                    if vote_elem:
                        vote_text = vote_elem.get_text(strip=True)
                        votes = self._parse_number(vote_text)

                    # 提取标签
                    tags = [keyword]
                    tag_elems = card.find_all('a', class_='TopicLink')
                    for tag_elem in tag_elems[:3]:
                        tag = tag_elem.get_text(strip=True)
                        if tag:
                            tags.append(tag)

                    # 判断内容类型（问答/文章）
                    content_type = 'question'
                    if '/p/' in content_url or 'zhuanlan' in content_url:
                        content_type = 'article'

                    item = RawItem(
                        source="zhihu",
                        url=content_url,
                        title=title,
                        snippet=summary[:200],
                        tags=list(set(tags)),
                        engagement={'votes': votes},
                        metadata={'type': content_type, 'keyword': keyword}
                    )

                    items.append(item)

                except Exception as e:
                    self.logger.warning(f"Failed to parse Zhihu content: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to search Zhihu for '{keyword}': {e}")

        return items

    def _parse_number(self, text: str) -> int:
        """解析数字文本（支持k, w等单位）"""
        text = text.strip().lower().replace(',', '')
        try:
            if 'w' in text or '万' in text:
                return int(float(text.replace('w', '').replace('万', '').strip()) * 10000)
            elif 'k' in text or '千' in text:
                return int(float(text.replace('k', '').replace('千', '').strip()) * 1000)
            else:
                # 提取所有数字
                import re
                numbers = re.findall(r'\d+', text)
                return int(numbers[0]) if numbers else 0
        except:
            return 0
