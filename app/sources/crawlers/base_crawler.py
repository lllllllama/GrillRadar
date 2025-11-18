"""
爬虫基类 / Base Crawler

定义所有爬虫的统一接口
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging
import time
import httpx
from app.sources.crawlers.models import RawItem, CrawlerConfig, CrawlerResult

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    爬虫基类 / Base Crawler

    所有具体爬虫都应继承此类并实现 crawl 方法
    """

    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        初始化爬虫

        Args:
            config: 爬虫配置，如果为None则使用默认配置
        """
        self.config = config or CrawlerConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = {}  # 简单的内存缓存

    @abstractmethod
    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        """
        抓取数据（子类必须实现）

        Args:
            domain: 目标领域（如 "backend", "llm_application"）
            keywords: 关键词列表（用于搜索）

        Returns:
            CrawlerResult: 抓取结果
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源名称（子类必须实现）"""
        pass

    def _get_cache_key(self, domain: str, keywords: List[str]) -> str:
        """生成缓存键"""
        keywords_str = "_".join(sorted(keywords))
        return f"{self.source_name}:{domain}:{keywords_str}"

    def _get_from_cache(self, cache_key: str) -> Optional[CrawlerResult]:
        """从缓存获取"""
        if not self.config.use_cache:
            return None

        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                self.logger.info(f"Cache hit for {cache_key}")
                return result
            else:
                # 缓存过期
                del self._cache[cache_key]

        return None

    def _save_to_cache(self, cache_key: str, result: CrawlerResult):
        """保存到缓存"""
        if self.config.use_cache:
            self._cache[cache_key] = (result, time.time())

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Optional[httpx.Response]:
        """
        发起HTTP请求（带重试和超时控制）

        Args:
            url: 目标URL
            method: HTTP方法
            **kwargs: 传递给httpx的其他参数

        Returns:
            Response对象，失败返回None
        """
        headers = kwargs.pop('headers', {})
        headers.setdefault('User-Agent', self.config.user_agent)

        for attempt in range(self.config.retry_times + 1):
            try:
                with httpx.Client(timeout=self.config.timeout) as client:
                    response = client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        **kwargs
                    )
                    response.raise_for_status()

                    # 请求成功，休眠避免被封
                    if self.config.sleep_between_requests > 0:
                        time.sleep(self.config.sleep_between_requests)

                    return response

            except httpx.HTTPStatusError as e:
                self.logger.warning(
                    f"HTTP error {e.response.status_code} for {url} "
                    f"(attempt {attempt + 1}/{self.config.retry_times + 1})"
                )
                if attempt < self.config.retry_times:
                    time.sleep(2 ** attempt)  # 指数退避

            except Exception as e:
                self.logger.error(
                    f"Request failed for {url}: {e} "
                    f"(attempt {attempt + 1}/{self.config.retry_times + 1})"
                )
                if attempt < self.config.retry_times:
                    time.sleep(2 ** attempt)

        return None

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        从文本中提取关键词（简单实现）

        Args:
            text: 输入文本

        Returns:
            关键词列表
        """
        # 技术关键词列表（可扩展）
        tech_keywords = {
            # 编程语言
            'Python', 'Java', 'Go', 'JavaScript', 'TypeScript', 'C++', 'Rust',
            'Kotlin', 'Swift', 'Ruby', 'PHP', 'Scala',

            # 框架和库
            'React', 'Vue', 'Angular', 'Django', 'Flask', 'FastAPI',
            'Spring', 'SpringBoot', 'MyBatis', 'Gin', 'Express',
            'TensorFlow', 'PyTorch', 'Transformers', 'LangChain', 'LlamaIndex',

            # 数据库
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Cassandra', 'DynamoDB', 'Oracle', 'SQL Server',

            # 中间件
            'Kafka', 'RabbitMQ', 'RocketMQ', 'Nginx', 'Envoy',

            # 云原生
            'Docker', 'Kubernetes', 'K8s', 'Istio', 'Prometheus', 'Grafana',
            'Jenkins', 'GitLab', 'GitHub Actions',

            # 大数据
            'Spark', 'Flink', 'Hadoop', 'Hive', 'HBase',

            # AI/ML
            'LLM', 'GPT', 'BERT', 'Transformer', 'RAG', 'Agent',
            'CNN', 'RNN', 'GAN', 'Diffusion', 'LoRA', 'PEFT',
            'Segmentation', 'Detection', 'Classification',

            # 概念
            '分布式', '微服务', '高并发', '负载均衡', '缓存',
            '消息队列', '服务网格', 'DevOps', 'CI/CD',
            '系统设计', '架构', '性能优化', '算法', '数据结构'
        }

        found_keywords = []
        text_lower = text.lower()

        for keyword in tech_keywords:
            # 检查关键词及其小写形式
            if keyword in text or keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return found_keywords[:10]  # 最多返回10个关键词
