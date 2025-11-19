# 爬虫系统状态说明

## 概述

GrillRadar 支持三种外部信息提供者：
1. **Mock Provider** (默认) - 快速模拟数据
2. **Local Dataset Provider** (推荐稳定性) - 真实的本地JSON数据集
3. **Multi-Source Crawler Provider** (推荐实时性) - GitHub + Juejin + Zhihu 实时爬虫

## 当前状态 (2025-11-19 更新 - 反爬虫改进测试)

### ✅ 正常工作
- **Mock Provider**: 完全正常，快速生成模拟数据

- **Local Dataset Provider**: 完全正常，使用真实的JD和面经数据
  - 数据位置: `app/sources/data/jd_database.json` 和 `interview_database.json`
  - 包含8个真实JD，10个真实面经
  - 支持关键词趋势和主题趋势分析
  - 覆盖领域: backend, frontend, ml, nlp, cv_segmentation

- **Multi-Source Crawler Provider**: ✅ 部分工作
  - **GitHub爬虫**: ✅ 完全正常 (10个trending项目 in ~4秒)
  - **Juejin爬虫**: ⚠️ 突破403但需JavaScript渲染 (详见下文)
  - **Zhihu爬虫**: ❌ 仍遇到403 (需要更强的反检测)
  - **CSDN爬虫**: 已禁用 (SSL握手问题)

### 🚀 最新改进 (v2.0)

#### 新增爬虫
1. **掘金(Juejin)爬虫** - `app/sources/crawlers/juejin_crawler.py`
   - 专注技术文章和面试经验
   - 11+技术领域关键词映射
   - 智能数字解析 (支持k/w/万/千单位)
   - 状态: 已实现，遇到403需改进

2. **知乎(Zhihu)爬虫** - `app/sources/crawlers/zhihu_crawler.py`
   - 专注技术问答和经验分享
   - 面试导向的关键词优化
   - 区分问题和文章类型
   - 投票数提取和互动指标
   - 状态: 已实现，遇到403需改进

#### 基础设施改进
- **SSL错误处理**: base_crawler添加`verify=False`
- **多源编排**: 支持4个爬虫并行运行
- **智能重试**: 指数退避策略

### 🛡️ 反爬虫检测改进 (v2.1 - 最新)

#### 实现的反检测技术
创建了 `app/sources/crawlers/anti_detection.py` - **AntiDetectionHelper**:

1. **User-Agent池轮换**
   - 8个真实浏览器User-Agent (Chrome, Edge, Firefox, Safari)
   - 随机选择，模拟真实用户

2. **完整的浏览器请求头**
   - `Sec-Fetch-*` headers (现代浏览器特征)
   - `DNT: 1` (Do Not Track)
   - `Accept-Language`: zh-CN优先
   - `Referer`: 模拟站内跳转
   - `Cache-Control`, `Connection` 等标准头

3. **随机延迟**
   - 可配置的min/max延迟范围
   - 默认0.5-1.5秒，避免规律性请求

#### 测试结果 (2025-11-19)

**测试命令**: `python scripts/test_multi_source_v2.py`

| 爬虫 | 状态 | HTTP响应 | 获取项数 | 耗时 | 详细说明 |
|------|------|---------|---------|------|---------|
| **GitHub** | ✅ 成功 | 200 OK | 10项 | 3.8秒 | 完全正常，trending数据 |
| **Juejin** | ⚠️ 部分成功 | 200 OK | 0项 | 8.6秒 | 突破403，但内容需JS渲染 |
| **Zhihu** | ❌ 失败 | 403 Forbidden | 0项 | 19.2秒 | 反检测不足，需更强措施 |

**关键发现**:

1. **Juejin突破403**
   - ✅ 反检测headers成功绕过基础拦截
   - ❌ 搜索页面使用React/Vue前端渲染 (SPA)
   - 💡 返回的HTML仅1230字节，内容在JavaScript中
   - **需要**: Playwright浏览器自动化执行JS

2. **Zhihu仍被拦截**
   - ❌ 所有请求均返回403 (3次重试全失败)
   - 💡 反爬虫机制更强，可能检测:
     - Cookie/Session验证
     - TLS指纹识别
     - 请求频率分析
   - **需要**: Cookie池、Session管理或Playwright

## 测试结果

### Local Dataset Provider 测试 (✅ 成功)
```bash
python scripts/test_local_dataset.py
```

结果:
- ✅ 成功加载8个JD
- ✅ 成功加载10个面经
- ✅ 关键词趋势分析正常
- ✅ 主题趋势分析正常
- ✅ 高频问题提取正常

### Multi-Source Crawler V2 测试 (✅ 部分成功)
```bash
python scripts/test_multi_source_v2.py
```

结果:
- ✅ **GitHub**: 10项目 in 4秒 (trending repositories)
- ⚠️ **Juejin**: 0项目 (HTTP 403 Forbidden)
- ⚠️ **Zhihu**: 0项目 (HTTP 403 Forbidden)
- ✅ **数据聚合**: 5个JD from GitHub
- ✅ **关键词提取**: 8个核心技术栈
- ✅ **Prompt生成**: 正常

## 推荐方案

### 方案1: Multi-Source Crawler (推荐用于获取最新趋势)
使用 **Multi-Source Crawler Provider** with GitHub:

```bash
# 在 .env 中设置
EXTERNAL_INFO_PROVIDER=multi_source_crawler
```

**优势:**
- ✅ GitHub trending实时数据 (最新技术趋势)
- ✅ 10个项目 in ~4秒 (性能优秀)
- ✅ 自动数据聚合和关键词提取
- ⚠️ Juejin/Zhihu暂时无法使用 (403)

### 方案2: Local Dataset (推荐用于稳定性)
使用 **Local Dataset Provider**:

```bash
# 在 .env 中设置
EXTERNAL_INFO_PROVIDER=local_dataset
```

**优势:**
- ✅ 稳定可靠 (无网络依赖)
- ✅ 真实JD和面经数据
- ✅ 包含字节跳动、阿里巴巴、腾讯等
- ✅ 关键词和主题趋势分析
- ❌ 数据需手动更新

### 方案3: Mock (开发测试用)
```bash
EXTERNAL_INFO_PROVIDER=mock
```

## 改进建议与下一步行动

### ✅ 已完成的改进
1. ✅ **反检测基础设施** (v2.1)
   - User-Agent池轮换 (8个浏览器)
   - 完整的浏览器请求头 (Sec-Fetch-*, DNT, etc.)
   - 随机延迟机制
   - 成功突破Juejin的403防护

2. ✅ **AntiDetectionHelper工具类**
   - 位置: `app/sources/crawlers/anti_detection.py`
   - 已集成到Juejin和Zhihu爬虫
   - 可复用的反检测组件

### 📋 短期解决方案 (推荐)
1. **继续使用GitHub作为主要实时数据源** ⭐
   - ✅ 稳定可靠，性能优秀 (10项/3.8秒)
   - ✅ 无需JavaScript渲染
   - ✅ 覆盖最新技术趋势

2. **补充Local Dataset数据集**
   - 手动精选Juejin/Zhihu优质文章
   - 定期更新 (每月/每季度)
   - 保持数据质量和相关性

3. **组合策略** (最佳实践)
   - GitHub实时爬虫: 获取最新技术趋势
   - Local Dataset: 补充高质量面试经验
   - Mock Provider: 开发测试使用

### 🚀 长期解决方案 (可选，复杂度较高)

#### 方案A: Playwright浏览器自动化 (推荐度: ⭐⭐⭐)
**优点**:
- ✅ 可执行JavaScript，解决SPA问题
- ✅ 完全模拟真实浏览器行为
- ✅ MediaCrawler项目已验证可行

**缺点**:
- ❌ 资源消耗大 (每个浏览器实例~100MB内存)
- ❌ 速度慢 (需要完整页面加载)
- ❌ 部署复杂 (需要安装浏览器依赖)

**实现参考**:
```python
# 参考 MediaCrawler 的实现
from playwright.async_api import async_playwright
# 创建浏览器上下文，模拟真实用户行为
```

#### 方案B: API逆向工程 (推荐度: ⭐⭐⭐⭐)
**优点**:
- ✅ 性能最优，直接获取JSON数据
- ✅ 无需浏览器，资源消耗小
- ✅ 数据结构化，易于解析

**缺点**:
- ❌ 需要逆向分析网站API
- ❌ API可能变更，需要维护
- ❌ 可能需要加密/签名处理

**下一步**:
- 使用浏览器DevTools分析Juejin/Zhihu的API请求
- 提取API endpoint和参数规则
- 实现API调用 (可能需要签名)

#### 方案C: RSS/Atom订阅 (推荐度: ⭐⭐⭐⭐⭐)
**优点**:
- ✅ 最稳定，官方提供
- ✅ 不易被封禁
- ✅ 实现简单

**缺点**:
- ❌ 部分网站不提供RSS
- ❌ 内容可能不如搜索全面

**检查**:
- Juejin: 检查是否有标签/话题RSS
- Zhihu: 检查专栏/话题RSS

#### 方案D: 高级反检测技术 (推荐度: ⭐⭐)
- Cookie池管理 (模拟登录态)
- TLS指纹伪造 (curl_cffi库)
- IP代理池轮换
- 请求时序分析规避

**复杂度**: 很高，维护成本大

## 配置说明

在 `.env` 文件中设置外部信息提供者:

```bash
# 选项1: Mock数据 (默认，最快)
EXTERNAL_INFO_PROVIDER=mock

# 选项2: 本地数据集 (推荐，真实数据)
EXTERNAL_INFO_PROVIDER=local_dataset

# 选项3: 实时爬虫 (需要更新)
EXTERNAL_INFO_PROVIDER=multi_source_crawler
```

## 数据集维护

本地数据集位置:
- JD数据: `app/sources/data/jd_database.json`
- 面经数据: `app/sources/data/interview_database.json`

要添加新数据:
1. 编辑JSON文件
2. 遵循现有数据格式
3. 更新metadata中的`total_entries`和`last_updated`

## 演示脚本

### 使用Local Dataset Provider生成报告
```bash
# 设置环境变量
export EXTERNAL_INFO_PROVIDER=local_dataset

# 运行hardcore演示
python examples/run_demo_hardcore_with_external.py
```

输出:
- 25个高质量问题
- 集成真实JD和面经趋势
- Senior级别深度技术问题

## 总结与推荐

### 当前最佳方案 (2025-11-19)

**推荐使用组合策略**:

1. **实时趋势**: Multi-Source Crawler (仅GitHub) ⭐⭐⭐⭐⭐
   - ✅ GitHub爬虫工作完美 (10项/3.8秒)
   - ✅ 获取最新技术趋势和热门项目
   - ✅ 无需额外配置
   - 配置: `EXTERNAL_INFO_PROVIDER=multi_source_crawler`

2. **稳定数据**: Local Dataset Provider ⭐⭐⭐⭐⭐
   - ✅ 真实JD和面经数据
   - ✅ 性能稳定，无网络依赖
   - ✅ 包含字节、阿里、腾讯等大厂数据
   - 配置: `EXTERNAL_INFO_PROVIDER=local_dataset`

3. **开发测试**: Mock Provider ⭐⭐⭐
   - ✅ 快速生成模拟数据
   - ✅ 无需等待，适合开发调试
   - 配置: `EXTERNAL_INFO_PROVIDER=mock`

### 技术现状

| 组件 | 状态 | 备注 |
|------|------|------|
| GitHub爬虫 | ✅ 生产可用 | HTTP请求，无需JS渲染 |
| Juejin爬虫 | ⚠️ 部分完成 | 突破403但需Playwright执行JS |
| Zhihu爬虫 | ❌ 暂不可用 | 需要更强的反检测或API逆向 |
| Local Dataset | ✅ 生产可用 | 8个JD + 10个面经 |
| Mock Provider | ✅ 生产可用 | 开发测试专用 |

### 反爬虫改进成果

v2.1版本实现的反检测技术:
- ✅ User-Agent池 (8个浏览器)
- ✅ 完整浏览器headers (Sec-Fetch-*)
- ✅ 随机延迟机制
- ✅ Referer模拟
- ✅ 成功突破Juejin基础防护 (403→200)

### 下一步建议

**短期 (1-2周)**:
1. 继续使用GitHub + Local Dataset组合
2. 手动补充Juejin/Zhihu精选内容到Local Dataset
3. 优化现有GitHub爬虫性能

**中期 (1-2月)**:
1. 研究Juejin/Zhihu API逆向工程
2. 尝试RSS订阅方案
3. 评估Playwright方案的成本和收益

**长期 (未来)**:
1. 根据实际需求决定是否实现Playwright
2. 考虑官方API合作
3. 探索更多数据源 (V2EX, SegmentFault等)
