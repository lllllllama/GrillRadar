# 爬虫系统状态说明

## 概述

GrillRadar 支持三种外部信息提供者：
1. **Mock Provider** (默认) - 快速模拟数据
2. **Local Dataset Provider** (推荐稳定性) - 真实的本地JSON数据集
3. **Multi-Source Crawler Provider** (推荐实时性) - GitHub + Juejin + Zhihu 实时爬虫

## 当前状态 (2025-11-19 更新)

### ✅ 正常工作
- **Mock Provider**: 完全正常，快速生成模拟数据

- **Local Dataset Provider**: 完全正常，使用真实的JD和面经数据
  - 数据位置: `app/sources/data/jd_database.json` 和 `interview_database.json`
  - 包含8个真实JD，10个真实面经
  - 支持关键词趋势和主题趋势分析
  - 覆盖领域: backend, frontend, ml, nlp, cv_segmentation

- **Multi-Source Crawler Provider**: ✅ 部分工作
  - **GitHub爬虫**: ✅ 完全正常 (10个trending项目 in ~4秒)
  - **Juejin爬虫**: 已实现但遇到403 (反爬虫机制)
  - **Zhihu爬虫**: 已实现但遇到403 (反爬虫机制)
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

## 改进建议 (Juejin/Zhihu 403问题)

### 短期解决方案
1. **继续使用GitHub作为主要数据源** - 已经工作良好
2. **补充本地数据集** - 手动添加Juejin/Zhihu的优质文章
3. **定期更新local_dataset** - 保持数据新鲜度

### 长期解决方案 (未来改进)
1. **Playwright浏览器自动化**
   - 参考MediaCrawler的实现
   - 可绕过基本的反爬虫检测
   - 缺点: 资源消耗大，部署复杂

2. **官方API集成**
   - Juejin: 寻找官方API或RSS feed
   - Zhihu: 可能需要申请开发者权限

3. **高级反检测技术**
   - 轮换User-Agent
   - Cookie池管理
   - 请求间隔随机化
   - IP代理池

4. **RSS/Atom订阅**
   - 部分网站提供RSS feed
   - 更稳定，不易被封

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

## 总结

**当前推荐使用 Local Dataset Provider**，因为：
1. ✅ 数据真实可靠
2. ✅ 性能稳定快速
3. ✅ 无需网络请求
4. ✅ 趋势分析完整
5. ✅ 易于维护和扩展

Multi-Source Crawler 需要更新HTML解析器后才能正常使用。
