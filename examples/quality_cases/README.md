# GrillRadar 质量测试用例

> [English Version](./README.en.md)

本目录包含用于评估生成问题质量的测试用例。

## 📁 测试用例

### 1. 求职 - 后端工程师 (`job_backend`)
- **简历**：`resume_job_backend.txt`
- **配置**：`config_job_backend.json`
- **场景**：后端工程师（Go/Python）应聘阿里云
- **关键点**：微服务、分布式系统、API 网关

### 2. 求职 - 前端工程师 (`job_frontend`)
- **简历**：`resume_job_frontend.txt`
- **配置**：`config_job_frontend.json`
- **场景**：前端工程师（React）应聘字节跳动
- **关键点**：React、TypeScript、性能优化、协作工具

### 3. 读研 - NLP 博士 (`grad_nlp`)
- **简历**：`resume_grad_nlp.txt`
- **配置**：`config_grad_nlp.json`
- **场景**：NLP 研究员申请 Stanford/CMU 博士项目
- **关键点**：大语言模型、少样本学习、可控生成

## 🔧 使用方法

### 对所有用例运行质量评估：
```bash
python scripts/evaluate_question_quality.py
```

### 对特定用例运行质量评估：
```bash
python scripts/evaluate_question_quality.py --case job_backend
python scripts/evaluate_question_quality.py --case grad_nlp
```

### 使用详细输出运行：
```bash
python scripts/evaluate_question_quality.py --verbose
```

## 📊 质量检查

评估脚本检查以下质量维度：

### 问题质量
- ✓ 长度（最少 10 字，建议 20+ 字）
- ✓ 清晰度（不太笼统，有具体情境）

### 提问理由质量
- ✓ 长度（最少 30 字，建议 50+ 字）
- ✓ 情境相关性（提及简历/目标/领域）

### 基线答案质量
- ✓ 结构（有段落、要点或章节）
- ✓ 深度（最少 50 字，建议 200+ 字）

### 支撑材料质量
- ✓ 具体性（包含知识点、资源）
- ✓ 长度（最少 20 字，建议 100+ 字）

### 练习提示词质量
- ✓ 有练习占位符（例如 {your_experience}）
- ✓ 比问题本身更详细

## 📈 质量评分

- **A 级（90%+）**：优秀 - 可用于生产
- **B 级（80-89%）**：良好 - 建议小幅改进
- **C 级（70-79%）**：可接受 - 需要一些改进
- **D 级（<70%）**：需要改进 - 存在重大问题

## 🎯 添加新测试用例

要添加新测试用例：

1. 创建简历文件：`resume_{your_case}.txt`
2. 创建配置文件：`config_{your_case}.json`
3. 将用例名称添加到 `evaluate_question_quality.py` 中的 `available_cases`
4. 运行评估：`python scripts/evaluate_question_quality.py --case {your_case}`

## 💡 质量改进建议

如果你发现质量问题：

1. **问题太笼统**：添加具体技术情境或领域术语
2. **理由缺乏情境**：引用具体简历项目或目标要求
3. **答案缺乏结构**：使用段落、要点或编号列表
4. **支撑材料不具体**：包含具体论文、工具或概念
5. **练习提示词缺少占位符**：添加 {your_experience}、{your_project} 等
