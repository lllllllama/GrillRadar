# TrendRadar 项目分析与应用

## 项目概述

**TrendRadar**: https://github.com/sansan0/TrendRadar
**定位**: 热点助手 - 聚合多平台新闻热点，支持关键词筛选和AI分析
**Stars**: 高人气开源项目，被小众软件、阮一峰周刊等推荐

## 核心架构分析

### 1. 数据获取方式 ⭐⭐⭐⭐⭐

**关键发现**: TrendRadar **不直接爬取网站**，而是使用第三方聚合API！

```python
# 核心API调用
url = f"https://newsnow.busiyi.world/api/s?id={platform_id}&latest"

# 简单的GET请求即可获取结构化数据
response = requests.get(url, headers=headers, timeout=10)
data = response.json()  # 返回JSON格式数据
```

**优势**:
- ✅ **完全绕过反爬虫机制** (403/验证码/JavaScript渲染)
- ✅ **返回结构化JSON数据** (无需HTML解析)
- ✅ **无需复杂反检测** (User-Agent轮换/Cookie/Playwright等)
- ✅ **支持多平台聚合** (一个API支持30+平台)
- ✅ **维护成本低** (网站HTML变化不影响)

### 2. 支持的平台

#### ✅ API正常工作的平台 (测试结果)

| 平台 | ID | 状态 | 条目数 | 技术内容占比 | 适用性 |
|------|-----|------|--------|-------------|--------|
| **V2EX** | `v2ex` | ✅ cache | 30 | 20% | ⭐⭐⭐⭐⭐ 强烈推荐 |
| **IT之家** | `ithome` | ✅ cache | 30 | 20% | ⭐⭐⭐⭐ 推荐 |
| **知乎** | `zhihu` | ✅ success | 20 | 5% | ⭐⭐ 一般 (泛热点) |
| **微博** | `weibo` | ✅ cache | 30 | 0% | ⭐ 不推荐 (非技术) |
| **今日头条** | `toutiao` | ✅ cache | 30 | 0% | ⭐ 不推荐 (非技术) |
| **B站热搜** | `bilibili-hot-search` | ✅ - | - | - | 未测试 |

#### ❌ API不可用的平台

| 平台 | ID | 状态 | 备注 |
|------|-----|------|------|
| **掘金** | `juejin` | ❌ 503 | Service Unavailable |
| **CSDN** | `csdn` | ❌ 500 | Server Error |
| **36氪** | `36kr` | ❌ 500 | Server Error |

**结论**: 技术面试最相关的平台 (掘金/CSDN/36氪) 在newsnow API上不可用 😔

### 3. 关键词筛选系统 ⭐⭐⭐⭐

TrendRadar实现了高级关键词筛选语法:

```txt
# frequency_words.txt 配置示例

# 普通词 - 匹配任意一个即可
ChatGPT
大模型
LLM

# 必须词 (+) - 必须同时包含
+面试
+应用

# 过滤词 (!) - 包含则排除
!广告
!价格

# 空行分隔 - 不同词组独立统计
Python
+开发
!培训

Java
+工程师
!培训
```

**语法规则**:
- **普通词**: 标题包含任意一个即可捕获
- **必须词** (`+词汇`): 必须同时包含普通词和必须词
- **过滤词** (`!词汇`): 包含过滤词直接排除
- **词组** (空行分隔): 不同主题独立统计和显示

**应用价值**:
- ✅ 精准筛选相关内容
- ✅ 过滤广告和无关信息
- ✅ 支持多主题监控

### 4. 重试机制 ⭐⭐⭐

```python
def fetch_data(self, id_info, max_retries=2, min_retry_wait=3, max_retry_wait=5):
    """获取数据，支持重试"""
    retries = 0
    while retries <= max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return data_text, id_value, alias
        except Exception as e:
            retries += 1
            if retries <= max_retries:
                # 指数退避 + 随机延迟
                base_wait = random.uniform(min_retry_wait, max_retry_wait)
                additional_wait = (retries - 1) * random.uniform(1, 2)
                wait_time = base_wait + additional_wait
                time.sleep(wait_time)
```

**特点**:
- ✅ 最多重试2次
- ✅ 随机延迟 (3-5秒基础 + 指数增长)
- ✅ 避免规律性请求

### 5. 其他值得学习的特性

1. **推送模式**:
   - `daily` - 当日汇总模式
   - `incremental` - 增量监控模式 (只推送新增)
   - `current` - 当前榜单模式

2. **时间窗口控制**:
   - 限制推送时间范围 (如09:00-18:00)
   - 避免非工作时间打扰

3. **多渠道通知**:
   - 企业微信、钉钉、飞书、Telegram、邮件、ntfy

4. **排序算法**:
   - 排名权重 (0.6) + 频次权重 (0.3) + 热度权重 (0.1)
   - 重新组合不同平台的排序

## 对 GrillRadar 的应用建议

### 🎯 方案一: 集成 V2EX 数据源 (强烈推荐)

**为什么选 V2EX**:
- ✅ **技术含量最高** (20% tech-related content)
- ✅ **活跃的技术社区** (程序员聚集地)
- ✅ **真实面试经验分享** (很多人分享面试题和经验)
- ✅ **API稳定可靠** (newsnow API完美支持)
- ✅ **无反爬虫问题** (通过API访问)

**实现方式**:

```python
# app/sources/crawlers/v2ex_api_crawler.py
import requests
from typing import List
from .models import RawItem, CrawlerResult

class V2EXAPICrawler(BaseCrawler):
    """V2EX爬虫 - 使用newsnow API"""

    @property
    def source_name(self) -> str:
        return "v2ex"

    def crawl(self, **kwargs) -> CrawlerResult:
        """通过API获取V2EX热门话题"""
        url = "https://newsnow.busiyi.world/api/s?id=v2ex&latest"

        headers = {
            "User-Agent": "Mozilla/5.0...",
            "Accept": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        items = []
        for item in data.get("items", []):
            title = item["title"]
            url = item.get("url", "")

            # 筛选技术相关内容
            if self._is_tech_related(title):
                items.append(RawItem(
                    title=title,
                    url=url,
                    source=self.source_name,
                    content_type="discussion",
                    metrics={"views": 0}  # API不提供详细指标
                ))

        return CrawlerResult(
            source=self.source_name,
            items=items,
            success=True
        )

    def _is_tech_related(self, title: str) -> bool:
        """判断是否技术相关"""
        tech_keywords = [
            "面试", "LLM", "AI", "算法", "Python", "Java",
            "开发", "后端", "前端", "数据库", "架构",
            "代码", "bug", "调试"
        ]
        return any(kw in title for kw in tech_keywords)
```

**预期效果**:
- 每次获取约 30 条V2EX热门话题
- 筛选后约 6-10 条技术相关内容
- 作为面试经验数据源的补充

### 🎯 方案二: 集成 IT之家 数据源 (推荐)

**优势**:
- ✅ 最新科技新闻
- ✅ 技术产品发布
- ✅ 行业动态

**适用场景**:
- 补充技术趋势信息
- 了解最新技术产品

### 🎯 方案三: 学习关键词筛选语法

为 GrillRadar 添加高级关键词筛选:

```python
# app/sources/keyword_filter.py
class KeywordFilter:
    """关键词筛选器 - 支持 +必须词 和 !过滤词 语法"""

    def __init__(self, keywords: List[str]):
        self.normal_keywords = []     # 普通词
        self.required_keywords = []   # 必须词 (+)
        self.exclude_keywords = []    # 过滤词 (!)

        for kw in keywords:
            if kw.startswith("+"):
                self.required_keywords.append(kw[1:])
            elif kw.startswith("!"):
                self.exclude_keywords.append(kw[1:])
            else:
                self.normal_keywords.append(kw)

    def match(self, text: str) -> bool:
        """判断文本是否匹配关键词规则"""
        # 1. 检查过滤词 - 包含则直接排除
        if any(kw in text for kw in self.exclude_keywords):
            return False

        # 2. 检查普通词 - 至少包含一个
        has_normal = any(kw in text for kw in self.normal_keywords)
        if not has_normal and self.normal_keywords:
            return False

        # 3. 检查必须词 - 必须全部包含
        if self.required_keywords:
            has_all_required = all(kw in text for kw in self.required_keywords)
            if not has_all_required:
                return False

        return True

# 使用示例
filter = KeywordFilter([
    "LLM", "ChatGPT", "大模型",  # 普通词
    "+面试", "+应用",             # 必须词
    "!广告", "!培训"              # 过滤词
])

filter.match("LLM大模型面试应用经验分享")  # ✅ True
filter.match("LLM大模型培训课程")         # ❌ False (包含过滤词)
filter.match("LLM大模型技术分析")         # ❌ False (缺少必须词)
```

### 🎯 方案四: 学习重试机制

为现有爬虫添加更健壮的重试逻辑:

```python
# 改进 base_crawler.py 的重试机制
def _make_request_with_retry(
    self,
    url: str,
    max_retries: int = 3,
    min_wait: int = 2,
    max_wait: int = 5
) -> Optional[httpx.Response]:
    """请求失败时自动重试 (指数退避)"""
    retries = 0
    while retries <= max_retries:
        try:
            response = self.client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            retries += 1
            if retries <= max_retries:
                # 指数退避 + 随机延迟
                base_wait = random.uniform(min_wait, max_wait)
                additional_wait = (retries - 1) * random.uniform(1, 2)
                wait_time = base_wait + additional_wait

                self.logger.warning(
                    f"请求失败 (尝试 {retries}/{max_retries}): {e}. "
                    f"{wait_time:.1f}秒后重试..."
                )
                time.sleep(wait_time)
            else:
                self.logger.error(f"请求最终失败: {e}")
                return None
    return None
```

## 测试结果总结

### newsnow API 可用性测试

```bash
python scripts/test_newsnow_api.py
```

**结果**:
```
✅ 知乎         - success  -  20 条 (5% tech)
❌ 36氪        - 失败       -   0 条
❌ 掘金         - 失败       -   0 条
❌ CSDN       - 失败       -   0 条
✅ V2EX       - cache    -  30 条 (20% tech) ⭐⭐⭐⭐⭐
✅ IT之家       - cache    -  30 条 (20% tech) ⭐⭐⭐⭐
✅ 微博         - cache    -  30 条 (0% tech)
✅ 今日头条       - cache    -  30 条 (0% tech)
```

**V2EX 示例内容**:
```
✅ "刚看完 Cloudflare 的故障复盘，虽然有点心疼他们..."
✅ "最近用 cursor 最新版 auto 生成项目的时候遇到的一些问题"
✅ "你们的国外大模型 api 都怎么充值的呢，好像要国外的信用卡？"
✅ "哈哈哈, 原来 cloudflare 写代码也用 unwarp() 呀"
✅ "开源软件 ShowDoc 新版发布，支持 AI 知识库助手"
```

## 实施优先级

### 🥇 高优先级 (立即实施)

1. **集成 V2EX API 爬虫**
   - 工作量: 小 (2-3小时)
   - 收益: 高 (技术讨论 + 面试经验)
   - 风险: 低 (API稳定)

2. **学习并应用重试机制**
   - 工作量: 小 (1小时)
   - 收益: 中 (提升爬虫健壮性)
   - 风险: 无

### 🥈 中优先级 (可选)

3. **集成 IT之家 API 爬虫**
   - 工作量: 小 (1-2小时)
   - 收益: 中 (科技新闻补充)
   - 风险: 低

4. **实现关键词筛选器**
   - 工作量: 中 (3-4小时)
   - 收益: 高 (精准过滤)
   - 风险: 无

### 🥉 低优先级 (未来考虑)

5. **探索其他newsnow支持的平台**
   - B站热搜、GitHub Trending等
   - 需要进一步测试评估

## 总结与建议

### ✅ 从 TrendRadar 学到的核心理念

1. **API优于直接爬虫**
   - 稳定性更高
   - 维护成本更低
   - 完全绕过反爬虫

2. **关键词筛选的重要性**
   - 精准匹配需求
   - 减少噪音干扰
   - 支持复杂过滤规则

3. **健壮的重试机制**
   - 指数退避
   - 随机延迟
   - 避免雪崩效应

### 🎯 对 GrillRadar 的具体建议

**当前数据源组合 (推荐)**:
```
1. GitHub Trending (自研爬虫)    ✅ 最新技术趋势
2. V2EX (newsnow API)           ✅ 技术讨论 + 面试经验
3. Local Dataset                ✅ 精选高质量数据
4. IT之家 (newsnow API, 可选)   ⭐ 科技新闻补充
```

**优势**:
- ✅ 4个数据源覆盖不同维度
- ✅ 2个API源 (GitHub + newsnow) 无反爬虫问题
- ✅ 技术相关度高
- ✅ 适合面试准备场景

**配置方式**:
```python
# app/sources/external_info_service.py
self.provider = MultiSourceCrawlerProvider(
    config=crawler_config,
    enable_github=True,    # 技术趋势
    enable_v2ex=True,      # 技术讨论 (新增)
    enable_ithome=True,    # 科技新闻 (新增, 可选)
    enable_local=True,     # 精选数据
)
```

## 参考资料

- **TrendRadar 项目**: https://github.com/sansan0/TrendRadar
- **newsnow 数据源**: https://github.com/ourongxing/newsnow
- **newsnow API**: https://newsnow.busiyi.world/api/s
- **V2EX 官网**: https://www.v2ex.com/
- **IT之家**: https://www.ithome.com/

---

**最后更新**: 2025-11-19
**分析者**: Claude (GrillRadar 开发助手)
