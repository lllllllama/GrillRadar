# 爬虫系统状态说明

## 概述

GrillRadar 支持三种外部信息提供者：
1. **Mock Provider** (默认) - 快速模拟数据
2. **Local Dataset Provider** (推荐) - 真实的本地JSON数据集
3. **Multi-Source Crawler Provider** (需要更新) - GitHub + CSDN 实时爬虫

## 当前状态

### ✅ 正常工作
- **Mock Provider**: 完全正常，快速生成模拟数据
- **Local Dataset Provider**: 完全正常，使用真实的JD和面经数据
  - 数据位置: `app/sources/data/jd_database.json` 和 `interview_database.json`
  - 包含8个真实JD，10个真实面经
  - 支持关键词趋势和主题趋势分析
  - 覆盖领域: backend, frontend, ml, nlp, cv_segmentation

### ⚠️ 需要更新
- **Multi-Source Crawler Provider**: HTML解析器需要更新
  - GitHub和CSDN的网页结构已经改变
  - 当前解析器返回0条结果
  - HTTP请求成功，但CSS选择器已过时

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

### Multi-Source Crawler 测试 (⚠️ 需要更新)
```bash
python scripts/test_multi_source_crawler.py
```

结果:
- ✅ HTTP请求成功 (GitHub trending: 200 OK)
- ✅ HTTP请求成功 (CSDN search: 200 OK)
- ❌ 解析结果: 0 items (HTML结构变更)

## 解决方案

### 短期方案 (推荐)
使用 **Local Dataset Provider**:

```bash
# 在 .env 中设置
EXTERNAL_INFO_PROVIDER=local_dataset
```

这将使用真实的本地数据集，包含：
- 字节跳动、阿里巴巴、腾讯等公司的JD
- NLP、LLM、后端、前端等领域的面经
- 关键词和主题趋势分析

### 长期方案
更新爬虫的HTML解析器:

1. **GitHub Crawler** (`app/sources/crawlers/github_crawler.py`)
   - 需要更新CSS选择器
   - GitHub trending页面结构已改变
   - 原选择器: `article.Box-row`, `h2.h3`
   - 需要检查新的HTML结构

2. **CSDN Crawler** (`app/sources/crawlers/csdn_crawler.py`)
   - 需要更新CSS选择器
   - CSDN搜索页面结构已改变
   - 可能需要处理反爬虫机制

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
