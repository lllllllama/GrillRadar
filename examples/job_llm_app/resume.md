# 王思远 | LLM应用工程师

**联系方式**: wangsiyuan@email.com | **GitHub**: github.com/wangsiyuan-llm | **手机**: 135-2468-1357

---

## 教育背景

**浙江大学** | 软件工程 | 本科 | 2019.09 - 2023.06
- GPA: 3.7/4.0，专业排名前15%
- 核心课程: 自然语言处理(92)、深度学习(95)、软件工程(90)、数据库系统(88)
- 毕业设计: 基于GPT的智能代码审查系统（优秀毕业设计，导师: 陈教授）

---

## 工作经历

### 阿里巴巴 | LLM应用研发工程师 | 2023.07 - 至今 (1年5个月)

#### 1. 通义千问企业知识库问答系统 (2024.03 - 至今)
- **项目描述**: 为企业客户构建基于通义千问的私有知识库问答平台，支持多种文档格式接入
- **核心技术**:
  * 设计并实现RAG检索增强生成架构，集成Elasticsearch + 向量检索双路召回
  * 使用LangChain框架，实现文档分块、向量化、检索、重排序完整pipeline
  * 优化Prompt工程，设计Few-shot模板，问答准确率从72%提升至89%
  * 实现向量数据库Milvus索引优化，检索延迟降低60% (500ms → 200ms)
  * 开发答案可信度评估模块，基于多维度特征（相似度、置信度、幻觉检测）
- **技术栈**: Python, LangChain, 通义千问API, Milvus, Elasticsearch, FastAPI, Redis
- **业务成果**: 服务企业客户15家，日均处理查询8000+次，知识库规模10万+文档

#### 2. 智能客服Agent系统 (2023.09 - 2024.02)
- **项目描述**: 开发多轮对话的智能客服系统，集成意图识别、槽位填充、任务编排
- **核心工作**:
  * 基于通义千问设计ReAct Agent框架，实现工具调用和决策链路
  * 开发Function Calling机制，接入10+业务API（订单查询、退款、物流等）
  * 实现对话状态管理和上下文追踪，支持多轮交互
  * 设计Prompt模板系统，支持角色设定、任务描述、输出格式约束
  * 构建评估体系：任务完成率、对话轮次、用户满意度
- **技术要点**:
  * Agent框架设计（ReAct, Self-Ask）
  * Function Calling与工具编排
  * 对话流管理和异常处理
- **业务成果**: 客服自动化率提升至65%，平均对话轮次4.2轮，用户满意度4.3/5

#### 3. LLM应用监控平台 (2023.07 - 2023.08)
- **项目描述**: 内部工具，用于监控LLM应用的调用情况、性能指标、成本分析
- **实现功能**:
  * 实时监控API调用量、Token消耗、响应时间、错误率
  * 可视化Dashboard展示趋势分析、成本预测
  * 告警系统：异常检测（错误率突增、延迟过高）
  * Prompt版本管理和A/B测试支持
- **技术栈**: Python, Grafana, Prometheus, PostgreSQL, Celery

---

## 实习经历

### 字节跳动 | 推荐算法实习生 | 2022.06 - 2022.12 (6个月)
- 参与抖音推荐系统召回层优化，负责用户兴趣向量表示学习
- 使用TensorFlow实现双塔模型，CTR提升2.1%
- 处理海量数据：Spark离线特征工程 + Flink实时特征
- 学习了推荐系统架构、A/B测试方法论、工业界模型训练流程

---

## 项目经历

### 开源项目: AgentHub - 多Agent协作框架 (2024.01 - 2024.06)
- **GitHub**: github.com/wangsiyuan-llm/AgentHub (Star: 580)
- **项目介绍**: 轻量级多Agent协作框架，支持Agent通信、任务分解、协同决策
- **核心特性**:
  * 实现多种Agent角色：规划Agent、执行Agent、评审Agent
  * 支持Agent间消息传递和状态共享
  * 可视化Agent决策过程（思维链、工具调用）
  * 提供CLI和Web界面
- **技术亮点**:
  * 抽象Agent基类，支持插件化扩展
  * 异步任务调度，提升并发性能
  * 集成LangSmith进行调试和追踪
  * 完整的单元测试和文档
- **影响力**: 被3个商业项目采用，收到15个PR贡献

### 个人项目: PromptStudio - Prompt管理工具 (2023.10 - 2023.12)
- **功能**: Prompt版本管理、变量模板、Few-shot样例库、效果评测
- **技术**: React + FastAPI + SQLite，支持团队协作
- **使用情况**: 团队内部使用，管理Prompt模板100+个

---

## 技术能力

**编程语言**: Python(精通), JavaScript(熟练), Go(了解)

**LLM相关**:
- **大模型API**: 通义千问、GPT-3.5/4、Claude、文心一言、Kimi、GLM-4
- **框架与工具**: LangChain, LlamaIndex, Semantic Kernel, LangSmith, AutoGen
- **Prompt工程**: Few-shot, Chain-of-Thought, ReAct, Self-Consistency, Tree-of-Thought
- **RAG技术**: 文档解析、分块策略、Embedding、向量检索、重排序、混合检索
- **向量数据库**: Milvus, FAISS, Pinecone, ChromaDB, Weaviate
- **Agent设计**: ReAct框架, Function Calling, 工具编排, 多Agent协作

**后端开发**:
- Web框架: FastAPI, Flask, Django
- 数据库: PostgreSQL, MySQL, MongoDB, Redis
- 消息队列: RabbitMQ, Kafka
- 搜索引擎: Elasticsearch

**工程能力**:
- DevOps: Docker, Kubernetes, CI/CD (GitLab CI)
- 监控运维: Prometheus, Grafana, ELK Stack
- 版本管理: Git, GitHub Actions
- 测试: Pytest, 单元测试, 集成测试

**云服务**: 阿里云(OSS, ECS, ACK), AWS(S3, Lambda)

---

## 英语能力

- CET-6: 580分
- 能够流利阅读英文技术文档、论文、API文档
- 活跃于英文技术社区（GitHub, Stack Overflow）
- 撰写英文技术博客5篇

---

## 其他

**技术博客**:
- 掘金专栏《LLM应用开发实战》，15篇文章，总阅读量12万+
- 主题: RAG系统设计、Prompt工程、Agent框架、LLM应用最佳实践

**开源贡献**:
- LangChain贡献者 (2个PR合并): 修复文档加载器bug、优化向量检索逻辑
- Milvus文档贡献 (中文翻译)

**技术分享**:
- 公司内部分享《RAG系统设计与实践》(2024.05)
- 阿里云开发者大会演讲《通义千问企业应用最佳实践》(2024.08)

---

## 求职意向

**期望岗位**: LLM应用工程师 / AI应用研发工程师 / Prompt工程师
**期望公司**: 字节跳动、阿里巴巴、腾讯、百度、美团（LLM相关团队）
**期望城市**: 北京 / 杭州 / 深圳
**期望薪资**: 35k-50k
**到岗时间**: 1个月内

---

## 自我评价

我是一名专注于LLM应用开发的工程师，拥有1年半的大模型落地经验。在阿里巴巴期间，我参与了多个LLM应用项目，从RAG系统、智能Agent到监控平台，积累了丰富的工程实践经验。我擅长RAG架构设计、Prompt工程优化、Agent系统开发，熟悉多种大模型API和主流框架。

我对LLM技术保持高度热情，活跃于开源社区，开发了AgentHub等开源项目。我追求技术深度和工程质量，注重代码规范、测试覆盖和文档完善。希望加入一家重视AI创新的团队，将LLM能力应用到更多实际业务场景中，创造真正的用户价值。
