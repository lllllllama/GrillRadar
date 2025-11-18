# 多源爬虫系统 / Multi-Source Crawler System

> **TrendRadar风格的多源信息采集和聚合系统**
>
> *实时抓取GitHub、CSDN等真实数据源，提供准确的技术趋势和面试经验*

---

## 📖 概述

GrillRadar的多源爬虫系统实现了真实的、可用的信息采集功能，能够从多个数据源（GitHub、CSDN等）自动抓取技术趋势、热门项目和面试经验，为面试准备提供最新、最准确的参考信息。

### 核心特性

- ✅ **多源并行爬取** - 同时从GitHub和CSDN抓取数据
- ✅ **智能去重和聚合** - 自动去重、排序、提取关键信息
- ✅ **领域定制** - 23个专业领域的精准关键词映射
- ✅ **缓存机制** - 智能缓存减少重复请求
- ✅ **无缝集成** - 兼容现有ExternalInfo接口
- ✅ **可扩展架构** - 易于添加新的数据源

---

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                  MultiSourceCrawlerProvider              │
│  (协调多个爬虫，并行执行，聚合结果)                        │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴───────────┐
        │                        │
        ▼                        ▼
┌──────────────┐         ┌──────────────┐
│ GitHubCrawler│         │ CSDNCrawler  │
│              │         │              │
│ • Trending   │         │ • 面试题     │
│ • Search     │         │ • 技术文章   │
└──────┬───────┘         └──────┬───────┘
       │                        │
       └────────────┬───────────┘
                    │ RawItem[]
                    ▼
          ┌──────────────────┐
          │  TrendAggregator │
          │                  │
          │  • 去重          │
          │  • 关键词提取    │
          │  • 转换格式      │
          └────────┬─────────┘
                   │
                   ▼
          ExternalInfoSummary
```

### 核心组件

#### 1. **BaseCrawler** - 爬虫基类

```python
class BaseCrawler(ABC):
    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        """抓取数据（子类实现）"""
        pass

    def _make_request(self, url: str) -> Response:
        """HTTP请求（带重试和限流）"""
        pass
```

**特性：**
- 统一的接口定义
- 自动重试机制
- 请求限流保护
- 简单内存缓存

#### 2. **RawItem** - 统一数据模型

```python
class RawItem(BaseModel):
    source: str          # 数据源（github/csdn）
    url: str             # 原始URL
    title: str           # 标题
    snippet: str         # 摘要
    tags: List[str]      # 标签/关键词
    engagement: Dict     # 互动指标（star/view/like）
    metadata: Dict       # 额外元数据
```

**设计理念：**
- 所有爬虫返回统一格式
- 便于后续聚合和转换
- 包含足够的元数据用于排序和过滤

#### 3. **GitHubCrawler** - GitHub数据采集

```python
class GitHubCrawler(BaseCrawler):
    def _crawl_trending(self, language: str) -> List[RawItem]:
        """抓取GitHub Trending"""

    def _crawl_search(self, keywords: List[str]) -> List[RawItem]:
        """搜索GitHub仓库"""
```

**数据来源：**
- GitHub Trending页面（按语言过滤）
- GitHub搜索结果（按star排序）

**提取信息：**
- 仓库名称、描述
- Star数量
- 编程语言
- 技术标签

#### 4. **CSDNCrawler** - CSDN数据采集

```python
class CSDNCrawler(BaseCrawler):
    def _crawl_search(self, keyword: str) -> List[RawItem]:
        """搜索CSDN文章"""
```

**数据来源：**
- CSDN搜索结果（面试题、技术文章）

**提取信息：**
- 文章标题、摘要
- 浏览量、点赞数
- 是否为面试相关
- 技术关键词

#### 5. **TrendAggregator** - 数据聚合器

```python
class TrendAggregator:
    @staticmethod
    def aggregate(raw_items: List[RawItem]) -> ExternalInfoSummary:
        """聚合原始数据为ExternalInfoSummary"""
```

**聚合流程：**
1. 去重（基于URL）
2. 按互动分数排序
3. 分组（项目 vs 文章）
4. 转换为JD和面经格式
5. 提取关键词和主题
6. 生成高频问题列表

---

## 🚀 使用指南

### 快速开始

#### 1. 安装依赖

```bash
pip install beautifulsoup4==4.12.2 lxml==4.9.3
```

#### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 启用多源爬虫（默认为mock）
EXTERNAL_INFO_PROVIDER=multi_source_crawler

# 爬虫配置（可选）
CRAWLER_MAX_ITEMS=20           # 每个源最多抓取条目数
CRAWLER_TIMEOUT=10             # 请求超时（秒）
CRAWLER_SLEEP=1.0              # 请求间隔（秒）
CRAWLER_USE_CACHE=true         # 是否使用缓存
```

#### 3. 使用示例

**方式1：通过ExternalInfoService**

```python
from app.sources.external_info_service import ExternalInfoService
from app.models.user_config import UserConfig

# 创建服务（会自动读取环境变量EXTERNAL_INFO_PROVIDER）
service = ExternalInfoService(provider_type='multi_source_crawler')

# 创建用户配置
user_config = UserConfig(
    mode='job',
    target_desc='后端开发工程师',
    domain='backend',
    resume_text='简历内容...'
)

# 检索外部信息
summary = service.retrieve_external_info(
    user_config=user_config,
    resume_keywords=['Python', 'Django', 'Redis']
)

# 获取Prompt摘要
prompt_text = service.get_prompt_summary(summary)
print(prompt_text)
```

**方式2：直接使用MultiSourceCrawlerProvider**

```python
from app.sources.multi_source_provider import MultiSourceCrawlerProvider
from app.sources.crawlers.models import CrawlerConfig

# 自定义配置
config = CrawlerConfig(
    max_items=15,
    timeout=10,
    sleep_between_requests=0.5,
    use_cache=True
)

# 创建提供者
provider = MultiSourceCrawlerProvider(
    config=config,
    enable_github=True,
    enable_csdn=True
)

# 检索信息
summary = provider.retrieve_external_info(
    user_config=user_config,
    resume_keywords=['LLM', 'RAG']
)
```

#### 4. 测试脚本

运行测试脚本验证功能：

```bash
python scripts/test_multi_source_crawler.py
```

**测试选项：**
1. LLM应用开发场景
2. 后端开发场景
3. 计算机视觉场景
4. 测试所有场景
5. 仅测试单个爬虫

---

## 📊 领域关键词映射

系统为23个专业领域提供了精心设计的关键词映射：

### 工程领域示例

```python
DOMAIN_KEYWORDS = {
    'backend': ['backend', 'microservice', 'distributed-system', 'api'],
    'frontend': ['frontend', 'react', 'vue', 'javascript', 'typescript'],
    'llm_application': ['LLM', 'RAG', 'langchain', 'GPT', 'chatbot'],
    # ... 更多领域
}
```

### 研究领域示例

```python
DOMAIN_KEYWORDS = {
    'cv_segmentation': ['segmentation', 'computer-vision', 'semantic-segmentation'],
    'nlp': ['nlp', 'natural-language', 'transformers', 'bert'],
    # ... 更多领域
}
```

---

## ⚙️ 配置选项

### CrawlerConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_items` | int | 20 | 每个源最多抓取的条目数 |
| `timeout` | int | 10 | 请求超时时间（秒） |
| `retry_times` | int | 2 | 失败重试次数 |
| `sleep_between_requests` | float | 1.0 | 请求间隔（秒），避免被封 |
| `use_cache` | bool | True | 是否使用缓存 |
| `cache_ttl` | int | 3600 | 缓存有效期（秒） |
| `user_agent` | str | Mozilla/5.0... | User-Agent字符串 |

### 环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `EXTERNAL_INFO_PROVIDER` | 提供者类型 | `multi_source_crawler` 或 `mock` |
| `CRAWLER_MAX_ITEMS` | 最大条目数 | `20` |
| `CRAWLER_TIMEOUT` | 超时时间 | `10` |
| `CRAWLER_SLEEP` | 请求间隔 | `1.0` |
| `CRAWLER_USE_CACHE` | 是否缓存 | `true` |

---

## 🔧 扩展新数据源

### 步骤1：创建爬虫类

```python
# app/sources/crawlers/your_crawler.py
from app.sources.crawlers.base_crawler import BaseCrawler
from app.sources.crawlers.models import RawItem, CrawlerResult

class YourCrawler(BaseCrawler):
    @property
    def source_name(self) -> str:
        return "your_source"

    def crawl(self, domain: str, keywords: List[str]) -> CrawlerResult:
        items = []

        # 实现你的爬取逻辑
        # ...

        return CrawlerResult(
            source=self.source_name,
            items=items,
            success=True,
            crawled_count=len(items)
        )
```

### 步骤2：注册到MultiSourceProvider

```python
# app/sources/multi_source_provider.py
from app.sources.crawlers.your_crawler import YourCrawler

class MultiSourceCrawlerProvider:
    def __init__(self, enable_your_source: bool = True):
        # ...
        if enable_your_source:
            self.crawlers.append(YourCrawler(self.config))
```

---

## 📈 性能优化

### 并行爬取

系统使用`ThreadPoolExecutor`并行执行多个爬虫：

```python
with ThreadPoolExecutor(max_workers=len(self.crawlers)) as executor:
    futures = [executor.submit(crawler.crawl, ...) for crawler in self.crawlers]
    results = [f.result() for f in as_completed(futures)]
```

### 缓存策略

- **内存缓存**：简单的字典缓存，生命周期与进程相同
- **缓存键**：`source:domain:keywords`
- **TTL控制**：默认1小时，可配置

### 限流保护

- **请求间隔**：每个请求后休眠（默认1秒）
- **重试机制**：失败后指数退避重试
- **超时控制**：防止长时间等待

---

## 🐛 调试和故障排查

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 常见问题

**Q1: 爬虫返回空结果**
- 检查网络连接
- 确认目标网站可访问
- 检查关键词是否合适
- 查看日志中的错误信息

**Q2: 请求被拒绝/封禁**
- 增加`sleep_between_requests`
- 使用代理（需要自己实现）
- 减少`max_items`

**Q3: 解析错误**
- 目标网站HTML结构可能已变化
- 更新对应爬虫的选择器
- 参考最新的网页结构

---

## 🧪 测试

### 单元测试

```bash
# 运行爬虫相关测试
pytest tests/test_crawlers.py -v

# 测试特定爬虫
pytest tests/test_github_crawler.py -v
```

### 集成测试

```bash
# 使用测试脚本
python scripts/test_multi_source_crawler.py
```

---

## 📝 最佳实践

1. **合理设置请求间隔**：避免过于频繁的请求
2. **使用缓存**：减少重复爬取
3. **限制条目数**：按需设置`max_items`
4. **监控日志**：及时发现问题
5. **尊重robots.txt**：遵守网站爬取规则

---

## 🔒 法律和道德

- ✅ 仅爬取公开可访问的数据
- ✅ 遵守网站的robots.txt规则
- ✅ 合理控制请求频率
- ✅ 仅用于个人学习和面试准备
- ❌ 不用于商业目的
- ❌ 不进行大规模数据采集

---

## 🚀 未来规划

### 近期计划

- [ ] 添加更多数据源（知乎、牛客、LeetCode）
- [ ] 实现更智能的关键词提取（NLP）
- [ ] 添加代理池支持
- [ ] 持久化缓存（Redis）

### 长期计划

- [ ] 使用官方API替代HTML解析
- [ ] 增量更新机制
- [ ] 数据质量评分系统
- [ ] 用户自定义数据源

---

## 📚 相关文档

- [主README](../README.md) - 项目主页
- [EXTERNAL_INFO.md](../EXTERNAL_INFO.md) - 外部信息源集成说明
- [CONFIGURATION.md](../CONFIGURATION.md) - 配置指南

---

最后更新: 2025-11-18
版本: 1.0.0
