# GrillRadar 高级演示

> [English Version](./ADVANCED_README.en.md)

本目录包含展示 GrillRadar 高级功能的演示。

## 🎯 概述

**两大高级特性**：

1. **TrendRadar 风格外部信息** - 真实 JD/面经数据及关键词频率分析
2. **BettaFish 风格多智能体架构** - 6 个专业智能体协作生成更好的问题

## 📂 目录结构

```
examples/
├── demo_advanced_features.py          # 主高级功能演示
├── compare_single_vs_multi_agent.py   # 单智能体 vs 多智能体对比
├── quality_cases/                     # 所有演示的测试用例
│   ├── resume_job_backend.txt
│   ├── config_job_backend.json
│   ├── resume_job_frontend.txt
│   ├── config_job_frontend.json
│   ├── resume_grad_nlp.txt
│   └── config_grad_nlp.json
├── run_demo_llm.py                    # 快速演示：LLM 工程师
├── run_demo_cv.py                     # 快速演示：CV 研究员
└── ADVANCED_README.md                 # 本文件
```

## 🚀 快速开始

### 前置要求

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API 密钥
cp .env.example .env
# 编辑 .env 并添加 ANTHROPIC_API_KEY 或 OPENAI_API_KEY
```

### 运行高级功能演示

```bash
# 基础演示（展示两个功能）
python examples/demo_advanced_features.py

# 特定测试用例
python examples/demo_advanced_features.py --case job_backend

# 前端工程演示
python examples/demo_advanced_features.py --case job_frontend

# NLP 研究演示
python examples/demo_advanced_features.py --case grad_nlp
```

### 运行多智能体对比

```bash
# 对比方法
python examples/compare_single_vs_multi_agent.py --case job_backend

# 生成 markdown 报告
python examples/compare_single_vs_multi_agent.py --case job_backend \
    --output my_comparison.md
```

## 📊 演示 1：TrendRadar 信息获取

### 展示内容

- **真实 JD 数据**：来自字节跳动、阿里巴巴、腾讯等 15 个职位描述
- **面经数据**：12 份包含真实问题的面试经验
- **关键词频率**：识别高频技能（例如 MySQL 在 6 个 JD 中出现）
- **趋势分析**：显示行业热门话题

### 示例输出

```
🔥 高频关键词分析:

  热门关键词（按频率排序）:
   1. MySQL                     ██████ (6 次出现)
   2. Redis                     ████   (4 次出现)
   3. 性能优化                      ████   (4 次出现)
   4. Python                    ████   (4 次出现)
   5. 微服务                       ███    (3 次出现)

📝 集成到 support_notes:

  该问题涉及 MySQL（高频技能，在6个JD中出现），
  建议重点准备相关知识点...
```

### 核心功能

- ✅ 来自真实职位发布的数据
- ✅ 基于频率的技能优先级排序
- ✅ 领域特定关键词加权
- ✅ 在 support_notes 中自动标记高频技能

## 🤖 演示 2：多智能体架构

### 展示内容

- **6 个专业智能体**：技术面试官、招聘经理、HR、导师、评审、守护者
- **并行提议**：所有智能体同时提出问题
- **论坛讨论**：虚拟委员会过滤和完善问题
- **质量控制**：守护者智能体移除不公平/低质量问题

### 示例输出

```
🎭 角色视角分析:

  技术面试官                                    ████████ 4 个问题 (26.7%)
  招聘经理                                      ███████ 3 个问题 (20.0%)
  HR/行为面试官                                 ████ 2 个问题 (13.3%)
  导师/PI                                      ████ 2 个问题 (13.3%)
  学术评审                                     ████ 2 个问题 (13.3%)
  候选人守护者                                 ████ 2 个问题 (13.3%)

💡 多智能体架构的优势:

  ✓ 多元视角: 6 个不同角色的观点
  ✓ 全面覆盖: 12 个独特话题
  ✓ 简历对齐: 78.5% 的问题引用简历
  ✓ 质量控制: 守护者智能体过滤低质量问题
  ✓ 去重: ForumEngine 移除相似问题
```

### 核心功能

- ✅ 对同一份简历的多个专家视角
- ✅ 协作过滤提高质量
- ✅ 更好地覆盖不同技能维度
- ✅ 通过多元观点减少偏见

## 📖 测试用例

### job_backend

**简历**：来自小米的 2 年后端工程师（Go/Python）
**项目**：API 网关、任务调度系统
**目标**：阿里云后端工程师
**领域**：backend

**运行**：`python examples/demo_advanced_features.py --case job_backend`

### job_frontend

**简历**：来自字节跳动/腾讯的 3 年前端工程师（React）
**项目**：低代码平台、实时协作编辑器
**目标**：字节跳动前端工程师
**领域**：frontend

**运行**：`python examples/demo_advanced_features.py --case job_frontend`

### grad_nlp

**简历**：北京大学本科生，NLP 研究，CoNLL 2023 论文
**项目**：少样本学习、意图分类
**目标**：Stanford/CMU NLP 方向博士
**领域**：nlp

**运行**：`python examples/demo_advanced_features.py --case grad_nlp`

## 📈 性能

### TrendRadar 数据加载

- **15 个 JD + 12 份面经**：<50ms 加载时间
- **关键词分析**：<10ms
- **内存使用**：<5MB

### 多智能体生成

- **单智能体**：8-12 秒
- **多智能体（6 个智能体）**：20-35 秒
- **质量提升**：基于自动评估提升 +20%

## 💡 集成到你的工作流

### 使用 TrendRadar 数据

```python
from app.sources.json_data_provider import json_data_provider

# 获取领域的 JD
jds = json_data_provider.get_jds(domain='backend')

# 分析高频关键词
keywords = json_data_provider.get_high_frequency_keywords(
    jds, domain='backend', top_k=10
)

# 结果: [('MySQL', 6), ('Redis', 4), ...]
```

### 启用多智能体模式

```python
from app.core.agent_orchestrator import AgentOrchestrator
from app.models.user_config import UserConfig

orchestrator = AgentOrchestrator(llm_client)
report = await orchestrator.generate_report(
    user_config,
    enable_multi_agent=True  # 启用多智能体
)
```

## 🔧 自定义

### 添加你自己的 JD 数据

1. 编辑 `app/sources/data/jd_database.json`
2. 遵循架构：
```json
{
  "id": "jd_custom_001",
  "company": "你的公司",
  "position": "你的职位",
  "keywords": ["Python", "Go", "MySQL"],
  "requirements": [...],
  ...
}
```

3. 测试：`python examples/demo_advanced_features.py`

### 调整智能体权重

编辑 `app/config/modes.yaml`：

```yaml
job:
  roles:
    technical_interviewer: 0.40  # 增加技术关注
    hiring_manager: 0.25
    hr: 0.20
    advocate: 0.15
```

## 📚 文档

- **质量控制**：[quality_cases/README.md](./quality_cases/README.md)
- **主 README**：[README.md](../README.md)
- **Web 界面**：[WEB_INTERFACE.md](../WEB_INTERFACE.md)

## 🐛 故障排除

### "No JDs found for domain"

**解决方案**：检查领域名称是否匹配以下之一：`backend`、`frontend`、`ml`、`nlp`、`cv_segmentation`

### "AttributeError: 'Anthropic' object has no attribute 'messages'"

**解决方案**：更新 Anthropic SDK：`pip install --upgrade anthropic`

### "Test case files not found"

**解决方案**：确保从项目根目录运行：
```bash
cd /path/to/GrillRadar
python examples/demo_advanced_features.py
```

## 🤝 贡献

想要添加更多功能或数据？

1. **更多 JD 数据**：添加到 `app/sources/data/jd_database.json`
2. **新智能体**：在 `app/agents/your_agent.py` 中创建
3. **更好的算法**：改进 `json_data_provider.py` 中的关键词频率

查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 获取指南。

---

**需要帮助？** 查看主 [README.md](../README.md) 获取详细的技术文档。
