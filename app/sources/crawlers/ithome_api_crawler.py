"""
IT之家 API 爬虫 / ITHome API Crawler

通过 newsnow API 获取 IT之家 科技新闻，专注产品发布、技术新闻等内容
API来源: https://newsnow.busiyi.world/api/s (TrendRadar项目使用的聚合API)
"""
from typing import List, Dict, Optional
import logging
import requests
import time
import random

from app.sources.crawlers.base_crawler import BaseCrawler
from app.sources.crawlers.models import RawItem, CrawlerResult


logger = logging.getLogger(__name__)


class ITHomeAPICrawler(BaseCrawler):
    """IT之家爬虫 - 使用newsnow API获取科技新闻"""

    # 技术关键词映射 (用于筛选IT之家新闻)
    TECH_KEYWORDS = {
        # AI/ML相关
        'AI', '人工智能', 'ChatGPT', 'GPT', 'LLM', '大模型',
        'Machine Learning', '机器学习', '深度学习', 'Transformer',

        # 编程语言和框架
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust',
        'React', 'Vue', 'Spring', 'Django', 'Node.js',

        # 硬件和产品
        'CPU', 'GPU', '芯片', '处理器', '显卡', 'NVIDIA', 'AMD', 'Intel',
        '手机', 'iPhone', '华为', '小米', 'OPPO', 'vivo',

        # 云和基础设施
        'Docker', 'Kubernetes', 'k8s', 'AWS', 'Azure', '阿里云', '腾讯云',

        # 开发工具
        'GitHub', 'Git', 'IDE', 'VSCode', 'Linux', 'Mac', 'Windows',

        # 数据库和存储
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',

        # 技术趋势
        '开源', '区块链', 'Web3', 'NFT', '元宇宙', 'VR', 'AR',
        '5G', '6G', '物联网', 'IoT', '自动驾驶',

        # 科技公司
        'Google', '谷歌', 'Microsoft', '微软', 'Apple', '苹果',
        '字节跳动', '阿里巴巴', '腾讯', '百度',
    }

    # 领域特定关键词映射
    DOMAIN_KEYWORDS = {
        # 工程领域
        'backend': ['后端', '服务器', 'API', 'Spring', 'Django', '微服务'],
        'frontend': ['前端', 'React', 'Vue', 'JavaScript', 'CSS', '浏览器'],
        'llm_application': ['LLM', 'ChatGPT', 'GPT', '大模型', 'AI', '人工智能'],
        'algorithm': ['算法', '性能', '优化', 'AI', '机器学习'],
        'data_engineering': ['数据', 'Spark', 'Hadoop', 'Kafka', '数据库'],
        'mobile': ['Android', 'iOS', 'Flutter', '手机', '移动'],
        'cloud_native': ['Kubernetes', 'Docker', 'k8s', '云原生', '容器'],
        'embedded': ['嵌入式', 'IoT', '物联网', '芯片', '单片机'],
        'game_dev': ['游戏', 'Unity', 'Unreal', '游戏引擎'],
        'blockchain': ['区块链', 'Web3', 'NFT', '加密', '以太坊'],
        'security': ['安全', '漏洞', '加密', '防护', '网络安全'],

        # 研究领域
        'cv_segmentation': ['计算机视觉', '图像', 'CV', '视觉'],
        'cv_detection': ['目标检测', '图像识别', 'YOLO'],
        'nlp': ['NLP', '自然语言', '文本', 'BERT'],
        'multimodal': ['多模态', 'CLIP', '图文'],
        'general_ml': ['机器学习', '深度学习', '神经网络', 'AI'],
        'robotics': ['机器人', '自动驾驶', 'ROS'],
    }

    @property
    def source_name(self) -> str:
        return "ithome"

    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger("ITHomeAPICrawler")
        self.api_url = "https://newsnow.busiyi.world/api/s?id=ithome&latest"

    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        """
        通过newsnow API爬取IT之家科技新闻

        Args:
            domain: 目标领域（如 "backend", "llm_application"）
            keywords: 关键词列表（用于搜索，IT之家不使用但需要保持接口一致）

        Returns:
            CrawlerResult: 爬取结果
        """
        start_time = time.time()
        self.logger.info(f"开始通过API获取IT之家数据 (domain={domain})")

        try:
            # 调用 newsnow API
            items = self._fetch_from_api()

            # 筛选技术相关内容
            filtered_items = self._filter_tech_items(items, domain)

            elapsed_ms = int((time.time() - start_time) * 1000)
            self.logger.info(
                f"IT之家 API爬取完成: {len(filtered_items)} 条 (总 {len(items)} 条) "
                f"in {elapsed_ms}ms"
            )

            return CrawlerResult(
                source=self.source_name,
                items=filtered_items,
                success=True,
                error_message=None,
                crawled_count=len(filtered_items),
                duration_ms=elapsed_ms
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"IT之家 API爬取失败: {e}")
            return CrawlerResult(
                source=self.source_name,
                items=[],
                success=False,
                error_message=str(e),
                crawled_count=0,
                duration_ms=elapsed_ms
            )

    def _fetch_from_api(self) -> List[Dict]:
        """
        从newsnow API获取IT之家数据

        Returns:
            List[Dict]: API返回的原始数据列表
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }

        # 带重试的请求
        max_retries = 3
        for retry in range(max_retries):
            try:
                response = requests.get(
                    self.api_url,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()
                status = data.get("status", "unknown")

                if status not in ["success", "cache"]:
                    raise ValueError(f"API状态异常: {status}")

                status_info = "最新数据" if status == "success" else "缓存数据"
                self.logger.info(f"API请求成功 ({status_info})")

                return data.get("items", [])

            except Exception as e:
                if retry < max_retries - 1:
                    wait_time = (retry + 1) * 2 + random.uniform(0, 1)
                    self.logger.warning(
                        f"API请求失败 (重试 {retry + 1}/{max_retries}): {e}. "
                        f"{wait_time:.1f}秒后重试..."
                    )
                    time.sleep(wait_time)
                else:
                    raise

        return []

    def _filter_tech_items(
        self,
        items: List[Dict],
        domain: Optional[str] = None
    ) -> List[RawItem]:
        """
        筛选技术相关的新闻

        Args:
            items: API返回的原始数据
            domain: 领域 (可选，用于精确筛选)

        Returns:
            List[RawItem]: 筛选后的技术相关新闻
        """
        filtered = []

        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")

            if not title or not url:
                continue

            # 如果指定了domain，使用domain关键词筛选
            if domain and domain in self.DOMAIN_KEYWORDS:
                if self._matches_domain(title, domain):
                    filtered.append(self._create_raw_item(item, domain))
            # 否则使用通用技术关键词筛选
            elif self._is_tech_related(title):
                filtered.append(self._create_raw_item(item, "general"))

        return filtered

    def _matches_domain(self, title: str, domain: str) -> bool:
        """
        判断标题是否匹配指定领域

        Args:
            title: 标题文本
            domain: 领域名称

        Returns:
            bool: 是否匹配
        """
        keywords = self.DOMAIN_KEYWORDS.get(domain, [])
        return any(keyword.lower() in title.lower() for keyword in keywords)

    def _is_tech_related(self, title: str) -> bool:
        """
        判断标题是否与技术相关

        Args:
            title: 标题文本

        Returns:
            bool: 是否技术相关
        """
        title_lower = title.lower()

        for keyword in self.TECH_KEYWORDS:
            if keyword.lower() in title_lower:
                return True

        return False

    def _create_raw_item(self, api_item: Dict, domain: str) -> RawItem:
        """
        将API数据转换为RawItem

        Args:
            api_item: API返回的单条数据
            domain: 领域标识

        Returns:
            RawItem: 标准化的爬虫数据项
        """
        title = api_item.get("title", "")
        url = api_item.get("url", "")
        mobile_url = api_item.get("mobileUrl", url)

        return RawItem(
            title=title,
            url=url,
            source=self.source_name,
            snippet=f"IT之家科技新闻 - {domain}",
            metadata={
                "content_type": "news",  # IT之家是新闻
                "mobile_url": mobile_url,
                "domain": domain,
            }
        )
