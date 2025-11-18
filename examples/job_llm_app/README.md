# 示例1: LLM应用工程师求职场景

## 场景描述

**候选人背景**: 王思远,浙江大学软件工程本科毕业,在阿里巴巴担任LLM应用研发工程师1年半,有丰富的大模型应用开发经验

**目标岗位**: 字节跳动/阿里巴巴 LLM应用工程师

**技术特点**:
- RAG系统设计与优化
- 智能Agent框架开发
- Prompt工程实践
- 开源项目作者(AgentHub, 580 stars)

---

## 如何运行

### 方式1: 使用命令行

```bash
# 从项目根目录运行
python cli.py \
  --config examples/job_llm_app/config.json \
  --resume examples/job_llm_app/resume.md \
  --output my_report.md
```

### 方式2: 查看示例报告

直接查看 `sample_report.md` 了解报告输出格式和问题类型。

---

## 文件说明

- `resume.md` - 候选人简历(中文,Markdown格式)
- `config.json` - GrillRadar配置文件
- `sample_report.md` - 生成的示例报告
- `README.md` - 本说明文档

---

## 报告亮点

本报告包含**15个核心拷问问题**,覆盖:

1. **RAG技术** (双路召回、文档分块、幻觉检测)
2. **Prompt工程** (优化方法论、评估体系)
3. **Agent系统** (ReAct框架、对话状态管理)
4. **系统设计** (高并发、成本优化、监控)
5. **工程实践** (向量检索优化、开源项目运营)
6. **理论基础** (Transformer原理、预训练vs微调)

每个问题都包含:
- 提问理由
- 基准答案框架
- 支撑材料和学习资源
- **可复用的练习提示词**(复制后喂给ChatGPT/Claude进行深度练习)

---

## 适用人群

- LLM应用工程师求职者
- AI应用研发工程师
- Prompt工程师
- 有1-3年大模型应用开发经验的工程师

---

[返回examples目录](../)
