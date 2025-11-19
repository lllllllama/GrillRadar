"""
V2EX API 爬虫 / V2EX API Crawler

通过 newsnow API 获取 V2EX 热门技术讨论，避免直接爬虫的反爬虫问题
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


class V2EXAPICrawler(BaseCrawler):
    """V2EX爬虫 - 使用newsnow API获取技术讨论"""

    # 技术关键词映射 (用于筛选V2EX讨论)
    TECH_KEYWORDS = {
        # 编程语言
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++',
        'Swift', 'Kotlin', 'PHP', 'Ruby', 'Scala',

        # AI/ML相关
        'AI', '人工智能', 'ChatGPT', 'GPT', 'LLM', '大模型',
        'Machine Learning', '机器学习', '深度学习', 'Transformer',

        # 技术框架/工具
        'React', 'Vue', 'Spring', 'Django', 'Flask', 'FastAPI',
        'Docker', 'Kubernetes', 'k8s', 'Redis', 'MySQL', 'PostgreSQL',
        'MongoDB', 'Elasticsearch', 'Kafka', 'RabbitMQ',

        # 开发相关
        '开发', '编程', '代码', 'bug', '调试', 'debug', '测试',
        '部署', '运维', 'DevOps', 'CI/CD', 'Git', 'GitHub',

        # 架构/系统
        '架构', '微服务', '分布式', '高并发', '性能优化',
        '系统设计', 'API', '后端', '前端', '全栈',

        # 面试相关
        '面试', '算法', '数据结构', 'LeetCode', '刷题',
        '求职', '跳槽', 'offer', '薪资', 'TC',

        # 云/基础设施
        'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', 'CDN',

        # 其他技术
        '区块链', 'Web3', 'NFT', '爬虫', '自动化',
        'Linux', 'Mac', 'Windows', 'IDE', 'VSCode', 'Vim',
    }

    # 领域特定关键词映射
    DOMAIN_KEYWORDS = {
        # 工程领域
        'backend': ['后端', '微服务', 'API', 'Spring', 'Django', 'Flask', 'FastAPI'],
        'frontend': ['前端', 'React', 'Vue', 'JavaScript', 'TypeScript', 'CSS'],
        'llm_application': ['LLM', 'ChatGPT', 'GPT', '大模型', 'AI', '人工智能', 'Transformer'],
        'algorithm': ['算法', 'LeetCode', '数据结构', '刷题', '面试题'],
        'data_engineering': ['数据', 'ETL', 'Spark', 'Hadoop', 'Kafka', 'Flink'],
        'mobile': ['Android', 'iOS', 'Flutter', 'React Native', '移动开发'],
        'cloud_native': ['Kubernetes', 'Docker', 'k8s', 'DevOps', '容器', '云原生'],
        'embedded': ['嵌入式', 'IoT', '物联网', '单片机', 'Arduino'],
        'game_dev': ['游戏开发', 'Unity', 'Unreal', '游戏引擎'],
        'blockchain': ['区块链', 'Web3', '智能合约', 'DeFi', 'NFT', '以太坊'],
        'security': ['安全', '渗透', '漏洞', '加密', 'CTF', '网络安全'],
        'test_qa': ['测试', '自动化测试', 'QA', 'Selenium', 'Pytest'],

        # 研究领域
        'cv_segmentation': ['计算机视觉', '图像分割', 'CV', '目标检测'],
        'cv_detection': ['目标检测', 'YOLO', '计算机视觉', '图像识别'],
        'nlp': ['NLP', '自然语言处理', '文本', 'BERT', 'Transformer'],
        'multimodal': ['多模态', 'CLIP', 'Vision-Language', '图文'],
        'general_ml': ['机器学习', '深度学习', '神经网络', 'PyTorch', 'TensorFlow'],
        'reinforcement_learning': ['强化学习', 'RL', '策略梯度', 'Q-learning'],
        'robotics': ['机器人', 'ROS', 'SLAM', '自动驾驶'],
        'graph_learning': ['图神经网络', 'GNN', '知识图谱', 'Graph'],
        'time_series': ['时间序列', '预测', '异常检测', '时序'],
        'federated_learning': ['联邦学习', '差分隐私', '隐私计算'],
        'ai_safety': ['AI安全', '对齐', '可解释性', '模型安全'],
    }

    @property
    def source_name(self) -> str:
        return "v2ex"

    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger("V2EXAPICrawler")
        self.api_url = "https://newsnow.busiyi.world/api/s?id=v2ex&latest"

    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        """
        通过newsnow API爬取V2EX热门讨论

        Args:
            domain: 目标领域（如 "backend", "llm_application"）
            keywords: 关键词列表（用于搜索，V2EX不使用但需要保持接口一致）

        Returns:
            CrawlerResult: 爬取结果
        """

        start_time = time.time()
        self.logger.info(f"开始通过API获取V2EX数据 (domain={domain})")

        try:
            # 调用 newsnow API
            items = self._fetch_from_api()

            # 筛选技术相关内容
            filtered_items = self._filter_tech_items(items, domain)

            elapsed_ms = int((time.time() - start_time) * 1000)
            self.logger.info(
                f"V2EX API爬取完成: {len(filtered_items)} 条 (总 {len(items)} 条) "
                f"in {elapsed_ms}ms"
            )

            return CrawlerResult(
                source=self.source_name,
                items=filtered_items,
                success=True,
                error_message=None
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"V2EX API爬取失败: {e}")
            return CrawlerResult(
                source=self.source_name,
                items=[],
                success=False,
                error_message=str(e)
            )

    def _fetch_from_api(self) -> List[Dict]:
        """
        从newsnow API获取V2EX数据

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
        筛选技术相关的讨论

        Args:
            items: API返回的原始数据
            domain: 领域 (可选，用于精确筛选)

        Returns:
            List[RawItem]: 筛选后的技术相关讨论
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
        # 转换为小写进行不区分大小写的匹配
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
        mobile_url = api_item.get("mobileUrl", url)  # 移动端URL，如果没有则使用普通URL

        return RawItem(
            title=title,
            url=url,
            source=self.source_name,
            snippet=f"V2EX技术讨论 - {domain}",  # 使用snippet代替description
            metadata={
                "content_type": "discussion",  # V2EX是讨论帖
                "mobile_url": mobile_url,
                "domain": domain,
            }
        )
