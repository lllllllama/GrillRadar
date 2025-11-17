# Claude.md - GrillRadar 项目规格说明书

## I. 项目概述

### 1. 愿景与核心定位

**GrillRadar** 是一个面向中国程序员和研究生申请者（硕士/博士/科研方向）的**一次性深度面试模拟与指导报告生成工具**。

**核心价值主张：**

用户提供简历和目标求职/学术方向后，系统将调用一个"虚拟面试/导师委员会"，生成一份高质量的**"深度拷问 + 辅导报告"**，包含：

- **必问的硬核问题** - 根据简历和目标精准定制，覆盖技术深度、项目真实性、研究能力等维度
- **清晰的提问理由** - 每个问题都明确说明为什么必须问、考察什么能力
- **基准答案结构** - 提供严谨的回答框架和关键要点，但不编造用户个人经历
- **参考方向** - 推荐相关技术、论文、会议、关键词等支撑材料
- **可复用的练习提示词** - 用户可以将这些提示词直接喂给任何AI进行迭代练习

**MVP定位：**

- **一次性报告生成** - 无用户记忆，无多轮对话，每次请求独立
- **单次深度诊断** - 类似体检报告，一次性暴露所有关键风险点和准备方向
- **架构前瞻性** - 虽然MVP简单，但架构设计借鉴TrendRadar和BettaFish，预留扩展能力

**设计哲学：**

- **TrendRadar式** - 对抗信息过载，只呈现真正重要的问题；配置驱动的信息源和关键词管理
- **BettaFish式** - 清晰的多智能体职责分离和协作流程；ForumEngine式多轮内部讨论→结构化报告

### 2. 目标用户与使用场景

#### 核心用户群体

**A. 程序员求职者**
- 校招应届生（本科/硕士）准备互联网大厂技术面试
- 社招工程师准备跳槽面试（特别是AI/后端/算法岗位）
- 实习生准备暑期/日常实习面试

**B. 研究生申请者**
- 准备硕士推免/考研复试面试
- 准备博士申请面试（套瓷PI、院系面试）
- 准备科研岗位/实验室面试
- 准备国外研究生项目面试（需要展示研究能力）

#### 典型使用场景

**场景1：工程岗求职**
> "我有一份简历，目标是字节跳动的LLM应用工程师岗位。他们会从哪些角度拷问我？我的简历有哪些风险点？"

**场景2：学术申请**
> "我在申请某视觉实验室做图像分割方向的硕士，导师和面试委员会会问我什么？我需要准备哪些研究方法论的问题？"

**场景3：双线准备**
> "我既在找工作也在准备保研，希望同一份简历从工程和科研两个视角被审视，看看哪些地方需要针对性调整。"

**场景4：快速诊断**
> "面试前48小时，我需要快速了解自己简历的所有漏洞和可能被问到的刁钻问题，集中突击准备。"

#### 当前版本限制与未来愿景

**当前版本（MVP）：**
- 一次性"诊断体检"，不保存用户数据
- 不支持多轮对话或长期训练
- 报告生成后，用户自行使用提示词练习

**未来版本愿景：**
- 支持多轮迭代训练（记录用户答题历史，追踪进步）
- 集成外部知识源（JD、面经、论文、博客）实现TrendRadar式信息雷达
- 真正的多智能体系统（BettaFish式agent拆分和协作）
- 个性化学习路径推荐

### 3. 模式设计（Mode: job / grad / mixed）

系统支持三种模式，每种模式调整虚拟委员会的角色权重和问题类型分布。

#### Mode: `job` (工程求职导向)

**目标场景：** 互联网公司技术岗位面试（校招/社招/实习）

**关注维度：**
- **工程技能** - 编程能力、系统设计、算法与数据结构
- **项目真实性与深度** - 项目是否真实参与、贡献度、技术难点
- **岗位匹配度** - 技术栈匹配、业务理解、角色适配性
- **职场软技能** - 沟通协作、主人翁意识、学习能力、抗压能力

**虚拟委员会角色权重：**
- **技术面试官（Technical Interviewer）** - 主导，占比40%
- **招聘经理（Hiring Manager）** - 占比30%
- **HR/行为面试官** - 占比20%
- **学术评审/导师** - 占比5%（仅用于检查基础CS素养）
- **候选人守护者（Advocate）** - 占比5%（过滤无意义问题）

**问题类型示例：**
- "你的简历上写了'优化了推荐系统召回率'，请详细描述你具体做了什么，用了什么算法，为什么选这个算法？"
- "你提到用Redis做缓存，请问你是如何设计缓存失效策略的？遇到缓存雪崩怎么办？"
- "你说你负责后端开发，但简历上没有写数据库设计经验，这是为什么？"

#### Mode: `grad` (学术/读研导向)

**目标场景：** 硕士推免/考研复试、博士申请、科研岗位面试

**关注维度：**
- **CS核心基础** - 操作系统、网络、算法、数据结构等（研究的基础）
- **研究素养** - 问题定义、文献阅读、实验设计、科学思维
- **目标领域理解** - 对申请方向的认知深度（如图像分割、多模态、LLM+X）
- **研究兴趣与规划** - 长期研究兴趣、为什么选这个方向、未来计划

**虚拟委员会角色权重：**
- **导师/PI（Advisor）** - 主导，占比40%
- **学术评审（Academic Reviewer）** - 占比30%
- **技术面试官** - 占比15%（检查工程实现能力）
- **HR/行为面试官** - 占比10%（检查科研态度、合作意愿）
- **候选人守护者（Advocate）** - 占比5%

**问题类型示例：**
- "你说你对图像分割感兴趣，请问你读过哪些经典论文？能说说Mask R-CNN和Semantic Segmentation的区别吗？"
- "你的本科毕设做了一个推荐系统，如果要把它写成一篇学术论文，你觉得研究问题（Research Question）应该怎么定义？"
- "你为什么想读研？你希望在研究生阶段解决什么问题？"
- "你提到想做多模态方向，请问你了解CLIP、BLIP这些工作吗？你觉得这个领域的核心挑战是什么？"

#### Mode: `mixed` (工程+学术双视角)

**目标场景：** 同时准备求职和读研、或者申请工业界研究岗位

**关注维度：**
- 综合`job`和`grad`的所有维度
- 每个问题必须标注视角标签：`[工程视角]` / `[学术视角]`

**虚拟委员会角色权重：**
- 所有角色均参与，权重相对均衡
- 技术面试官 + 导师/PI 各占30%
- 其他角色分配剩余40%

**报告特殊要求：**
- **双线总结** - 报告的summary部分必须包含两条评估：
  - "作为工程候选人的评估"
  - "作为科研/读研候选人的评估"
- **问题标签化** - 每个问题明确标注`[工程视角]`或`[学术视角]`，便于用户针对性准备

**问题类型示例：**
- `[工程视角]` "你的分布式爬虫项目，如果要部署到生产环境，你会如何设计监控和容错？"
- `[学术视角]` "同样是这个爬虫项目，如果要写成一篇会议论文，你觉得技术贡献点（Technical Contribution）在哪里？"

---

## II. 对标与借鉴：TrendRadar 和 BettaFish

本章节详细说明GrillRadar如何从两个优秀开源项目中借鉴设计思想和架构模式。

### 1. TrendRadar - 配置驱动的信息聚合与过滤

#### TrendRadar 核心特性

[TrendRadar](https://github.com/sansan0/TrendRadar) 是一个多平台热点内容聚合工具，其核心特性包括：

**A. 多源聚合**
- 支持从多个平台（微博、知乎、GitHub Trending、Hacker News等）获取热点内容
- 通过配置文件（`config.yaml`）定义监控的平台和数据源

**B. 关键词驱动的过滤**
- 使用`frequency_words.txt`等配置文件定义关键词
- 支持"必须包含"和"排除"规则
- 对抗信息过载：只呈现真正符合用户兴趣的内容

**C. 灵活的推送模式**
- 每日摘要（Daily Digest）
- 当前排行（Current Ranking）
- 增量更新（Incremental Updates）

**D. AI增强分析**
- 通过MCP（Model Context Protocol）集成AI能力
- 对热点内容进行深度分析、总结、趋势预测

#### GrillRadar 借鉴的设计点

**A. 配置驱动的领域管理（类比frequency_words.txt）**

在GrillRadar中，我们将借鉴TrendRadar的配置文件思想，创建：

- `domains.yaml` - 定义常见技术栈和研究领域
  ```yaml
  engineering:
    backend:
      keywords: [分布式系统, 微服务, 数据库优化, 缓存, 消息队列]
      common_stacks: [Java, Go, Python, MySQL, Redis, Kafka]
    llm_application:
      keywords: [prompt工程, RAG, 向量数据库, LLM微调, agent]
      common_stacks: [OpenAI API, LangChain, ChromaDB, FAISS]

  research:
    cv_segmentation:
      keywords: [语义分割, 实例分割, 全景分割, Transformer, 注意力机制]
      canonical_papers: [Mask R-CNN, SegFormer, Swin Transformer]
      conferences: [CVPR, ICCV, ECCV]
  ```

- `question_templates.yaml` - 预定义问题模板库（按领域分类）

**B. "对抗信息过载"的问题筛选哲学**

TrendRadar的核心思想是"不是所有热点都值得关注"，GrillRadar将其转化为：

- **不是所有问题都值得问** - 避免泛泛而谈的概念题
- **只问与简历和目标强相关的问题** - 基于简历内容+目标岗位/方向+当前技术趋势，精准筛选
- **问题必须有明确考察目的** - 每个问题都有清晰的`rationale`字段

**C. 外部信息源集成（未来版本）**

TrendRadar从多个平台抓取内容，GrillRadar未来将类似地集成：

- **JD数据源** - 爬取目标公司的真实岗位描述
- **面经数据源** - 牛客网、LeetCode讨论区的真实面试题
- **论文数据源** - arXiv、顶会论文的最新研究热点
- **技术博客** - 各大公司技术博客的实践案例

**D. 配置文件即产品形态**

TrendRadar通过修改配置文件即可适配不同用户需求，GrillRadar也将：

- 提供预设配置模板（如"后端工程师"、"CV研究生"）
- 允许用户自定义关注的技术栈/研究领域
- 配置驱动prompt生成，而非硬编码

#### MVP vs 未来版本

**MVP阶段：**
- 实现`domains.yaml`配置文件
- 用户选择领域标签（如"backend", "llm_application", "cv_segmentation"）
- Prompt中引用对应领域的关键词和常见技术栈

**未来版本：**
- 实现真正的外部信息源爬取（JD、面经、论文）
- 建立"面试信息雷达"，定期更新热门问题库
- 类似TrendRadar的推送机制：用户订阅后，定期收到最新面试趋势报告

### 2. BettaFish - 多智能体协作与ForumEngine

#### BettaFish 核心特性

[BettaFish](https://github.com/666ghj/BettaFish) 是一个多智能体意见分析系统，其核心特性包括：

**A. 清晰的智能体角色分工**

- **Query Agent** - 负责广泛的信息检索
- **Media Agent** - 负责多模态内容分析（图片、视频等）
- **Insight Agent** - 负责深度洞察，利用私有数据
- **Report Agent** - 负责最终报告生成

每个Agent有明确的职责边界和专业领域。

**B. ForumEngine式多轮协作**

- Agents之间不是简单的串行调用，而是类似论坛讨论的多轮交互
- 每轮讨论中：
  - 各Agent提出观点和证据
  - 相互反思、质疑、补充
  - 逐步收敛到一致结论
- 最终形成结构化报告

**C. 模块化代码架构**

BettaFish的代码结构清晰：
```
bettafish/
  agents/        # 每个agent一个模块
  tools/         # 工具层（检索、API调用等）
  llm/           # LLM接口封装
  orchestrator/  # 协调器，管理agent调度
```

#### GrillRadar 借鉴的设计点

**A. 虚拟委员会的角色设计（类比BettaFish的Agents）**

GrillRadar设计了一个"虚拟面试/导师委员会"，包含以下角色：

| 角色 | 职责 | 对应BettaFish角色 |
|------|------|-------------------|
| **技术面试官（Technical Interviewer）** | 考察工程技能、项目深度、算法能力 | Query Agent（检索技术知识） |
| **招聘经理（Hiring Manager）** | 考察岗位匹配、业务理解、主人翁意识 | Insight Agent（深度评估） |
| **HR/行为面试官（HR Interviewer）** | 考察软技能、价值观、团队协作 | Media Agent（多维度观察） |
| **导师/PI（Advisor）** | 考察研究能力、学术素养、长期潜力 | Insight Agent（学术维度） |
| **学术评审（Academic Reviewer）** | 考察论文阅读、实验设计、科研方法论 | Report Agent（严谨评估） |
| **候选人守护者（Advocate）** | 过滤低质量、攻击性、无意义的问题 | 质量控制角色（新增） |

**B. ForumEngine式内部协作流程**

虽然MVP使用单次LLM调用模拟多角色，但Prompt设计将模拟ForumEngine的多轮讨论：

1. **阶段1：各角色提出初步问题清单**
   - 技术面试官列出3-5个技术问题
   - 导师列出3-5个学术问题
   - HR列出2-3个软技能问题
   - 每个问题附简短理由

2. **阶段2：虚拟论坛讨论**
   - 委员会主席（虚拟角色）召集讨论
   - 合并相似问题
   - 去除纯概念题、低信号题
   - 候选人守护者发言：标记过于刁难或无价值的问题

3. **阶段3：筛选并完善最终问题**
   - 选出10-20个核心问题
   - 确保覆盖度：基础、项目、工程/研究、软技能
   - 对`mixed`模式，确保双视角平衡

4. **阶段4：为每个问题生成完整QuestionItem**
   - 填充`view_role`、`tag`、`question`、`rationale`、`baseline_answer`、`support_notes`、`prompt_template`

**C. 架构前瞻性：预留Agent拆分能力**

虽然MVP使用单次LLM调用，但代码架构将预留未来拆分为真实多Agent的能力：

```python
# 当前MVP实现
class VirtualCommittee:
    def generate_report(self, resume, config) -> Report:
        prompt = self.build_multi_role_prompt(resume, config)
        response = llm_client.call(prompt)
        return parse_report(response)

# 未来多Agent实现（预留接口）
class AgentOrchestrator:
    def __init__(self):
        self.technical_interviewer = TechnicalInterviewerAgent()
        self.advisor = AdvisorAgent()
        self.hr = HRAgent()
        # ...

    def generate_report(self, resume, config) -> Report:
        # 1. 各agent并行生成初步问题
        draft_questions = await asyncio.gather(
            self.technical_interviewer.propose_questions(resume, config),
            self.advisor.propose_questions(resume, config),
            # ...
        )
        # 2. Forum协调器合并讨论
        final_questions = self.forum_engine.discuss(draft_questions)
        # 3. Report Agent生成最终报告
        return self.report_agent.generate(final_questions)
```

**D. 模块化代码结构**

借鉴BettaFish的清晰模块划分，GrillRadar将采用：

```
grillradar/
  app/
    agents/              # 未来：每个角色一个模块（预留）
      technical.py
      advisor.py
      hr.py
    core/
      prompt_builder.py  # 当前：构建多角色prompt
      llm_client.py      # LLM调用封装
      report_generator.py # 报告生成协调器
    models/              # 数据模型
    config/              # 配置文件
    api/                 # FastAPI路由
```

#### MVP vs 未来版本

**MVP阶段：**
- 用一个精心设计的System Prompt模拟多角色讨论
- 单次LLM调用输出完整Report JSON
- 在Prompt中明确描述ForumEngine式的内部讨论流程

**未来版本：**
- 拆分为真正的独立Agent模块
- 实现真实的多轮协作（多次LLM调用，agents之间传递信息）
- 引入Forum协调器（类似BettaFish的Orchestrator）
- 支持Agent的自我反思和迭代优化

### 3. 综合借鉴总结

| 维度 | TrendRadar借鉴 | BettaFish借鉴 | GrillRadar融合 |
|------|----------------|---------------|----------------|
| **信息管理** | 配置驱动的多源聚合、关键词过滤 | - | `domains.yaml`配置领域知识；未来集成JD/面经/论文 |
| **质量哲学** | 对抗信息过载，只呈现重要内容 | - | 对抗问题泛滥，只问真正有价值的问题 |
| **角色设计** | - | 清晰的Agent职责分工 | 虚拟委员会6大角色（技术/HR/导师等） |
| **协作机制** | - | ForumEngine多轮讨论 | Prompt模拟论坛式问题筛选和完善 |
| **架构模式** | 配置文件+处理器 | Agents+Tools+Orchestrator | 当前简化，架构预留拆分能力 |
| **AI集成** | MCP深度分析 | 多Agent分工调用LLM | 单次LLM模拟多角色，未来真实多Agent |

**核心设计原则：**

1. **配置驱动** - 从TrendRadar学习，用YAML管理领域知识和问题模板
2. **角色清晰** - 从BettaFish学习，每个虚拟角色有明确职责和考察维度
3. **质量优先** - 综合两者哲学，宁缺毋滥，只生成高价值问题
4. **架构前瞻** - MVP简单实现，但模块划分为未来演进铺路

---

## III. 数据模型设计

本章节定义GrillRadar的核心数据模型，使用自然语言描述 + JSON Schema示例。

### 1. UserConfig（用户配置）

用户输入的配置信息，驱动报告生成的各个环节。

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | string enum | 是 | 模式：`"job"` / `"grad"` / `"mixed"` |
| `target_desc` | string | 是 | 目标描述，例如："字节跳动LLM应用工程师" 或 "清华大学某实验室图像分割方向硕士" |
| `domain` | string | 否 | 领域标签，例如："backend", "llm_application", "cv_segmentation", "nlp", "rs_recommendation"。用于引用`domains.yaml`中的预设知识 |
| `language` | string | 否 | 输出语言，默认`"zh"`（简体中文），未来支持`"en"` |
| `level` | string | 否 | 候选人级别，例如："intern", "junior", "senior", "master", "phd"。影响问题难度和期望深度 |
| `resume_text` | string | 是 | 简历原文（纯文本或Markdown格式） |

#### JSON Schema 示例

```jsonc
{
  "mode": "job",  // "job" | "grad" | "mixed"
  "target_desc": "字节跳动 - 抖音推荐后端研发工程师（校招）",
  "domain": "backend",  // 可选，用于引用domains.yaml中的backend配置
  "language": "zh",
  "level": "junior",  // intern | junior | senior | master | phd
  "resume_text": "姓名：张三\n教育背景：XX大学 计算机科学与技术 本科\n项目经历：\n1. 分布式爬虫系统..."
}
```

#### 字段使用方式

**`mode`的影响：**
- `job` → 虚拟委员会中技术面试官、招聘经理、HR权重高
- `grad` → 导师、学术评审权重高
- `mixed` → 双视角平衡，问题需要标注`[工程视角]` / `[学术视角]`

**`target_desc`的作用：**
- 在Prompt中直接引用："用户的目标是'{target_desc}'，请基于此目标设计问题"
- 用于判断岗位类型（如后端、算法、前端）或研究方向（如CV、NLP）
- 影响问题的具体内容和深度

**`domain`的作用：**
- 加载`domains.yaml`中对应领域的关键词、常见技术栈、经典论文等
- 在Prompt中注入领域知识，使问题更专业、更有针对性
- 例如：`domain="cv_segmentation"` → 问题会涉及Mask R-CNN、语义分割等

**`level`的作用：**
- `intern` / `junior` → 偏基础题，项目深度要求较低
- `senior` → 高级架构设计、技术选型、团队管理
- `master` / `phd` → 研究方法论、论文写作、学术规范

### 2. QuestionItem（问题卡片）

单个问题的完整信息，是报告的核心组成单元。

#### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 问题编号，从1开始 |
| `view_role` | string | 提问角色，例如："技术面试官", "导师/PI", "HR", "[工程视角]", "[学术视角]" |
| `tag` | string | 主题标签，例如："操作系统", "分布式系统", "图像分割", "研究方法论", "项目真实性风险" |
| `question` | string | 问题正文（简体中文），尽量具体、有针对性 |
| `rationale` | string | 提问理由（2-4句话），说明为什么问这个问题、考察什么能力、与简历/目标的关联 |
| `baseline_answer` | string | 基准答案结构：提供回答框架和关键要点，但不编造用户个人经历。帮助用户理解什么是好的回答 |
| `support_notes` | string | 支撑材料：相关概念、经典技术/论文、推荐阅读、搜索关键词等 |
| `prompt_template` | string | 可复用的练习提示词，用户可复制此提示词喂给任意AI进行深度练习。包含占位符（如`{your_experience}`），用户需填充真实经历 |

#### JSON Schema 示例

```jsonc
{
  "id": 1,
  "view_role": "技术面试官",
  "tag": "分布式系统",
  "question": "你的简历中提到'设计并实现了分布式爬虫系统'，请详细描述你如何解决爬虫任务的分发与调度问题？用了什么消息队列？如何保证任务不重复、不丢失？",
  "rationale": "这个问题考察候选人对分布式系统核心问题（任务分发、一致性、容错）的理解深度。简历只写了'分布式爬虫'，但没有具体技术细节，需要验证是否真正参与设计，还是仅仅部署了现成框架。对于后端工程师岗位，分布式系统能力是核心要求。",
  "baseline_answer": "一个好的回答应包含：1) 任务分发架构（如Master-Worker模式）；2) 使用的消息队列（如RabbitMQ/Kafka）及选型理由；3) 去重策略（如布隆过滤器、Redis Set）；4) 容错机制（如任务重试、心跳检测）；5) 遇到的坑和优化点（如队列堆积、消费者性能瓶颈）。",
  "support_notes": "关键概念：消息队列（RabbitMQ, Kafka, Redis Stream）、分布式一致性、幂等性、布隆过滤器。推荐阅读：《设计数据密集型应用》第11章、Scrapy-Redis源码。搜索关键词：'distributed task queue', 'deduplication in crawlers'。",
  "prompt_template": "我在简历中写了'分布式爬虫系统'，面试官问我如何解决任务分发与调度问题。我的实际情况是：{your_experience}。请帮我组织一个结构清晰、有技术深度的回答，重点说明架构设计、技术选型、遇到的难点和解决方案。"
}
```

#### 关键设计点

**1. `view_role` - 角色标签的作用**
- 帮助用户理解问题来源（"哦，这是技术面试官会问的"）
- 在`mixed`模式下，必须用`[工程视角]` / `[学术视角]`区分
- 未来可按角色过滤问题（"只看导师会问的问题"）

**2. `rationale` - 为什么必须写提问理由？**
- **透明性** - 用户理解每个问题的价值，不会觉得是随机生成
- **学习导向** - 用户看到理由后，即使不会答，也知道这个能力为什么重要
- **避免争议** - 如果问题尖锐，理由能说明正当性

**3. `baseline_answer` - 不编造用户经历的基准答案**
- **难点** - 不能说"你应该这样答"（因为不知道用户真实经历）
- **解法** - 提供**回答结构**和**关键要点**，如："一个好的回答应包含：1)... 2)... 3)..."
- **示例** - 可以给通用的技术方案（如"常见做法是用Redis做缓存"），但不能编造用户的具体实现

**4. `support_notes` - 知识支撑**
- 相关技术名词、经典论文、推荐书籍、搜索关键词
- 帮助用户快速补课（"原来这个问题涉及布隆过滤器，我去查一下"）
- 对学术问题，给出经典论文和会议（如"CVPR 2017: Mask R-CNN"）

**5. `prompt_template` - 可复用的练习提示词**
- **核心价值** - 用户可以拿着这个提示词去ChatGPT/Claude进行深度练习
- **设计要点** - 包含占位符（如`{your_experience}`），用户填充真实经历后喂给AI
- **示例**：
  ```
  我在面试中被问到："{question}"
  我的实际情况是：{your_experience}
  请帮我：
  1. 组织一个结构清晰的回答
  2. 指出我可能遗漏的技术点
  3. 提供可能的追问和应对策略
  ```

### 3. Report（完整报告）

最终生成的grilling报告，包含总结 + 问题列表。

#### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `summary` | string | 总体评估：候选人的优势、风险点、准备建议。语气略带grilling但建设性强 |
| `mode` | string | 报告模式：`"job"` / `"grad"` / `"mixed"` |
| `target_desc` | string | 用户的目标岗位/方向（直接复制自UserConfig） |
| `highlights` | string | 候选人亮点：从简历和问题设计中推断出的优势（如"扎实的分布式系统实践经验"） |
| `risks` | string | 关键风险点：简历暴露的薄弱环节（如"缺少数据库优化经验"、"研究方法论不清晰"） |
| `questions` | QuestionItem[] | 问题列表，通常10-20个 |
| `meta` | object | 元数据：生成时间、LLM模型版本、配置参数等 |

#### JSON Schema 示例

```jsonc
{
  "summary": "作为一名后端开发候选人，你的简历展示了较好的工程实践经验，特别是分布式系统和微服务方面。但也存在一些明显的风险点：1) 项目描述过于简略，缺少量化指标和技术难点说明，容易被质疑深度；2) 数据库和缓存相关经验较少，而这是后端核心能力；3) 系统设计能力未得到充分体现。建议重点准备分布式系统、数据库优化、系统设计三大模块，并补充简历中项目的量化数据。",
  "mode": "job",
  "target_desc": "字节跳动 - 抖音推荐后端研发工程师（校招）",
  "highlights": "1. 有分布式爬虫和微服务项目经验，体现了工程实践能力\n2. 技术栈涵盖Python/Go/Redis，与目标岗位匹配\n3. 参与过性能优化工作，有一定的工程sense",
  "risks": "1. 项目描述缺少量化指标（如QPS提升、延迟降低），难以评估贡献度\n2. 数据库经验薄弱，简历中未提及MySQL/PostgreSQL使用经验\n3. 缺少大规模系统设计经验，对推荐系统的业务理解可能不足\n4. 算法题刷题情况未知，LeetCode能力需要验证",
  "questions": [
    {
      "id": 1,
      "view_role": "技术面试官",
      "tag": "分布式系统",
      "question": "...",
      "rationale": "...",
      "baseline_answer": "...",
      "support_notes": "...",
      "prompt_template": "..."
    }
    // ... 更多问题
  ],
  "meta": {
    "generated_at": "2025-11-17T14:30:00Z",
    "model": "claude-sonnet-4",
    "config_version": "v1.0",
    "num_questions": 15
  }
}
```

#### 特殊处理：`mixed`模式的双线总结

对于`mixed`模式，`summary`字段必须包含两条独立的评估：

```
【工程候选人评估】
作为后端工程师候选人，你的项目经验较丰富，但缺少数据库和系统设计深度...

【科研候选人评估】
作为图像分割方向的研究生候选人，你的CV基础较好，但研究方法论和论文阅读经验不足...
```

#### 问题数量设计

**为什么是10-20个问题？**

- **10个以下** - 覆盖度不足，可能遗漏关键风险点
- **20个以上** - 信息过载，用户难以在短时间内全部准备
- **最佳实践** - 根据简历复杂度和目标岗位难度，动态调整：
  - 简历简单、目标岗位初级 → 10-12个问题
  - 简历丰富、目标岗位高级 → 15-20个问题

#### 报告导出格式

报告需支持多种导出格式，便于用户使用：

**1. JSON（原始数据）**
- 供开发者集成、二次处理

**2. Markdown**
- 结构清晰，便于阅读和编辑
- 可直接粘贴到Notion、Obsidian等笔记工具
- 示例结构：
  ```markdown
  # GrillRadar 面试准备报告

  **目标岗位：** 字节跳动 - 抖音推荐后端研发工程师（校招）
  **生成时间：** 2025-11-17 14:30

  ## 总体评估
  [summary内容]

  ## 候选人亮点
  [highlights内容]

  ## 关键风险点
  [risks内容]

  ---

  ## 问题清单

  ### Q1. [分布式系统] 技术面试官

  **问题：**
  你的简历中提到'设计并实现了分布式爬虫系统'...

  **为什么问这个问题：**
  [rationale]

  **如何回答：**
  [baseline_answer]

  **参考资料：**
  [support_notes]

  **练习提示词：**
  ```
  [prompt_template]
  ```
  ```

**3. HTML**
- 美观的网页格式，带样式
- 可直接在浏览器打开，或转为PDF

**4. PDF（未来）**
- 适合打印或分享
- 使用工具（如wkhtmltopdf）从HTML转换

---

## IV. 虚拟委员会与Prompt设计

这是GrillRadar的核心章节，定义如何用**单次LLM调用**模拟一个多角色"虚拟委员会"的内部讨论和问题生成过程。

### 1. 委员会角色定义

虚拟委员会由6个核心角色组成，每个角色有明确的职责和考察维度。

#### 角色1：技术面试官（Technical Interviewer）

**职责：**
- 考察CS基础（算法、数据结构、操作系统、网络、数据库）
- 考察工程技能（编程能力、系统设计、架构能力）
- 验证项目真实性和技术深度
- 评估问题解决能力和技术选型思维

**典型问题：**
- "你用Redis做缓存，请问你是如何设计缓存失效策略的？遇到缓存雪崩怎么办？"
- "你的分布式爬虫用了什么消息队列？为什么选它而不是其他方案？"
- "请手写一个LRU缓存的实现。"

**权重分布：**
- `job`模式：40%
- `grad`模式：15%
- `mixed`模式：30%

#### 角色2：招聘经理（Hiring Manager）

**职责：**
- 考察岗位匹配度（技术栈、业务理解、角色定位）
- 考察主人翁意识和独立性（是否真正负责项目，还是只是参与者）
- 评估业务sense（是否理解技术服务于业务）
- 判断候选人的成长性和潜力

**典型问题：**
- "你的项目最终解决了什么业务问题？带来了什么价值？"
- "在这个项目中，你是核心开发者还是参与者？你独立负责了哪些模块？"
- "如果让你重新设计这个系统，你会做哪些改进？"

**权重分布：**
- `job`模式：30%
- `grad`模式：10%
- `mixed`模式：20%

#### 角色3：HR/行为面试官（HR Interviewer）

**职责：**
- 考察软技能（沟通、协作、冲突解决）
- 考察价值观和职业规划
- 评估学习能力和适应能力
- 判断候选人是否适合公司文化

**典型问题：**
- "请描述一次你和团队成员意见不合的经历，你是如何处理的？"
- "你为什么选择后端开发方向？未来3-5年的职业规划是什么？"
- "你如何保持技术学习？平时关注哪些技术社区或博客？"

**权重分布：**
- `job`模式：20%
- `grad`模式：10%
- `mixed`模式：15%

#### 角色4：导师/PI（Advisor）

**职责：**
- 考察研究兴趣和长期规划
- 评估研究能力和学术潜力
- 判断候选人是否适合科研（好奇心、耐心、自驱力）
- 了解候选人对目标研究方向的认知深度

**典型问题：**
- "你为什么想做图像分割方向的研究？你觉得这个领域的核心挑战是什么？"
- "你读过哪些相关论文？能说说你最感兴趣的一篇吗？"
- "如果让你设计一个研究课题，你会选择什么问题？为什么？"

**权重分布：**
- `job`模式：5%
- `grad`模式：40%
- `mixed`模式：30%

#### 角色5：学术评审（Academic Reviewer）

**职责：**
- 考察科研方法论（问题定义、实验设计、结果分析）
- 评估论文阅读和写作能力
- 考察对学术规范的理解（引用、实验可复现性等）
- 判断候选人的批判性思维

**典型问题：**
- "你的本科毕设如果要写成论文，研究问题（Research Question）应该怎么定义？"
- "你如何评价你的实验设计？有哪些潜在的bias或局限性？"
- "你提到复现了某篇论文，请问你遇到了哪些坑？论文里有哪些细节没写清楚？"

**权重分布：**
- `job`模式：5%
- `grad`模式：30%
- `mixed`模式：25%

#### 角色6：候选人守护者（Candidate Advocate）

**职责：**
- 过滤低质量、无意义的问题（如纯概念题、百度就能查到的）
- 移除过于刁难、攻击性、或对评估无帮助的问题
- 确保问题"grilling but fair"（尖锐但公平）
- 维护问题的多样性和覆盖度

**典型行为：**
- "这个问题太宽泛，建议改为更具体的场景题。"
- "这个问题过于刁钻，对评估候选人能力没有实际帮助，建议删除。"
- "当前问题过于集中在算法，建议增加系统设计和工程实践类问题。"

**权重分布：**
- 所有模式均为5%（质量控制角色）

### 2. 内部委员会协作流程（ForumEngine式）

虽然MVP使用单次LLM调用，但Prompt将明确描述一个多阶段的内部讨论过程，指导LLM模拟这个流程。

#### 阶段1：输入解析与角色激活

**输入：**
- `resume_text` - 简历原文
- `user_config` - 包含`mode`, `target_desc`, `domain`, `level`等

**处理：**
1. **简历解析**
   - 提取教育背景、项目经历、技能栈、实习/工作经历
   - 识别关键词（如"分布式"、"微服务"、"深度学习"）

2. **目标解析**
   - 从`target_desc`推断岗位类型（后端/算法/前端/研究）
   - 从`domain`加载领域知识（如backend → 分布式、数据库、缓存）

3. **角色权重计算**
   - 根据`mode`确定各角色的发言权重
   - 例如：`job`模式 → 技术面试官40%，导师5%

#### 阶段2：各角色提出初步问题

每个角色独立思考，列出3-5个最想问的问题。

**Prompt指导（伪代码）：**
```
现在请各角色依次发言，提出你最想问的3-5个问题（每个问题附简短理由）：

【技术面试官发言】
1. 问题：...
   理由：...
2. ...

【招聘经理发言】
1. 问题：...
   理由：...

【导师/PI发言】
...
```

**质量要求：**
- 问题必须与简历内容强相关
- 避免纯概念题（如"什么是TCP三次握手"），改为场景题（如"你的项目用了TCP长连接，如何处理连接断开重连？"）
- 问题应有明确考察目的

#### 阶段3：虚拟论坛讨论与筛选

引入一个虚拟的"委员会主席"（或由候选人守护者担任），主持论坛讨论。

**讨论流程：**

1. **合并相似问题**
   - 技术面试官和导师都提了"请描述你的XXX项目"，合并为一个更深入的问题

2. **去除低质量问题**
   - 候选人守护者标记：
     - 纯概念题（"什么是Redis？"）
     - 与简历无关的问题
     - 过于宽泛、没有明确答案的问题（"谈谈你对AI的看法"）

3. **去除过度刁难的问题**
   - 候选人守护者标记：
     - 人身攻击或冒犯性问题
     - 对评估能力无帮助的陷阱题
     - 超出候选人级别太多的问题（对实习生问高级架构）

4. **确保覆盖度**
   - 检查是否覆盖：CS基础、项目深度、工程实践、软技能
   - 对`grad`模式，检查是否覆盖：研究方法论、论文阅读、学术规范
   - 对`mixed`模式，检查双视角是否平衡

**Prompt指导（伪代码）：**
```
【虚拟论坛讨论】
委员会主席：现在我们有20个初步问题，需要筛选到10-15个。

候选人守护者：
- 问题3和问题7高度重复，建议合并
- 问题12是纯概念题，建议删除或改为场景题
- 当前缺少系统设计类问题，建议技术面试官补充

技术面试官：同意，我补充一个分布式系统设计题。

导师/PI：当前学术问题只有2个，对于grad模式不够，建议增加论文阅读和实验设计相关问题。

委员会主席：好的，现在调整后有15个问题，覆盖度较好，进入下一阶段。
```

#### 阶段4：选定最终问题并完善

选出10-20个最终问题，对每个问题生成完整的`QuestionItem`。

**完善内容：**
1. **确定`view_role`和`tag`**
   - `view_role` - 哪个角色问的（技术面试官/导师/HR等）
   - `tag` - 主题标签（操作系统/分布式系统/研究方法论等）

2. **撰写`question`正文**
   - 尽量具体，引用简历中的内容
   - 例如："你的简历中提到'优化了推荐系统召回率'，请详细描述..."

3. **撰写`rationale`（提问理由）**
   - 2-4句话，说明：
     - 为什么问这个问题
     - 考察什么能力
     - 与简历/目标的关联

4. **撰写`baseline_answer`（基准答案）**
   - 提供回答结构："一个好的回答应包含：1)... 2)... 3)..."
   - 给出关键要点和技术方案，但不编造用户个人经历

5. **撰写`support_notes`（支撑材料）**
   - 相关技术名词、经典论文、推荐阅读、搜索关键词

6. **撰写`prompt_template`（练习提示词）**
   - 包含占位符（如`{your_experience}`）
   - 用户可复制此提示词到其他AI进行练习

#### 阶段5：生成报告总结

基于最终问题列表，生成报告的`summary`, `highlights`, `risks`字段。

**总结内容：**
- **summary** - 总体评估，指出优势和风险，给出准备建议
- **highlights** - 从简历和问题设计中推断的候选人亮点
- **risks** - 简历暴露的薄弱环节和可能的追问点

**对`mixed`模式：**
- `summary`必须包含两条独立评估：
  - 【工程候选人评估】
  - 【科研候选人评估】

### 3. System Prompt结构设计

以下是一个抽象的System Prompt模板（开发者需在`prompt_builder.py`中具体实现）。

#### Prompt结构

```
# GrillRadar 虚拟面试委员会 System Prompt

## 你的角色
你是一个"虚拟面试/导师委员会"，由6个专业角色组成：
1. 技术面试官 - 考察工程技能和CS基础
2. 招聘经理 - 考察岗位匹配和业务理解
3. HR/行为面试官 - 考察软技能和价值观
4. 导师/PI - 考察研究能力和学术潜力
5. 学术评审 - 考察科研方法论和论文能力
6. 候选人守护者 - 过滤低质量和刁难问题

## 当前任务
用户提供了简历和目标岗位/方向，你需要生成一份"深度拷问+辅导报告"。

### 输入信息
- 模式（mode）：{mode}  // job | grad | mixed
- 目标（target_desc）：{target_desc}
- 领域（domain）：{domain}  // 用于引用领域知识
- 候选人级别（level）：{level}
- 简历原文（resume_text）：
{resume_text}

### 领域知识（从domains.yaml加载）
{domain_knowledge}

## 任务目标
生成一个严格符合以下JSON Schema的Report对象：

{report_schema}

## 工作流程（你需要在内部模拟以下流程）

### 阶段1：解析输入
- 提取简历中的教育背景、项目、技能栈、实习/工作经历
- 理解目标岗位/方向的要求
- 根据mode确定各角色权重

### 阶段2：各角色提出初步问题
每个角色列出3-5个最想问的问题（附简短理由）。
注意：
- 问题必须与简历强相关
- 避免纯概念题，优先场景题
- 问题应有明确考察目的

### 阶段3：虚拟论坛讨论
委员会主席主持讨论：
- 合并相似问题
- 删除低质量问题（纯概念、与简历无关、过于宽泛）
- 删除过度刁难问题（人身攻击、陷阱题）
- 确保覆盖度（基础、项目、工程/研究、软技能）
- 对mixed模式，确保双视角平衡

### 阶段4：生成最终问题
选出10-20个问题，为每个问题生成完整的QuestionItem，包括：
- view_role, tag, question, rationale, baseline_answer, support_notes, prompt_template

### 阶段5：生成报告总结
撰写summary, highlights, risks字段。
对mixed模式，summary需包含双线评估。

## 输出要求

### 语言与风格
- 输出语言：简体中文
- 问题风格：略带grilling和幽默，但不能人身攻击或粗俗
- 学术内容：严谨、结构化，避免编造具体论文名

### 质量标准
- 每个问题都必须有明确的rationale
- baseline_answer不能编造用户个人经历，只能提供回答结构和技术要点
- support_notes要提供真实有用的参考资料
- prompt_template要包含清晰的占位符，便于用户填充

### JSON格式
- 严格遵循Report schema
- 确保所有字符串正确转义
- questions数组包含10-20个QuestionItem对象

## 特殊处理

### 针对job模式
- 技术面试官、招聘经理、HR权重高
- 问题偏重工程实践、项目深度、系统设计

### 针对grad模式
- 导师/PI、学术评审权重高
- 问题偏重研究方法论、论文阅读、学术规范

### 针对mixed模式
- 所有角色均衡参与
- 每个问题必须标注[工程视角]或[学术视角]
- summary包含双线评估

---

现在，请基于上述输入生成Report JSON。
```

#### Prompt中的动态部分

以下内容需要在`prompt_builder.py`中动态注入：

1. **`{mode}`** - 从`user_config.mode`获取
2. **`{target_desc}`** - 从`user_config.target_desc`获取
3. **`{domain}`** - 从`user_config.domain`获取
4. **`{level}`** - 从`user_config.level`获取
5. **`{resume_text}`** - 用户提供的简历原文
6. **`{domain_knowledge}`** - 从`domains.yaml`加载对应领域的知识（关键词、技术栈、论文等）
7. **`{report_schema}`** - Report的JSON Schema定义（供LLM参考）

#### Prompt优化技巧

**1. Few-shot示例（可选）**
- 在Prompt中提供1-2个QuestionItem的示例，帮助LLM理解输出格式

**2. 思维链（Chain of Thought）**
- 明确要求LLM"先思考，再输出"
- 例如："请先内部讨论（不需要输出讨论过程），然后直接输出最终的Report JSON"

**3. 约束强化**
- 重复关键约束，如"不得编造用户个人经历"、"每个问题必须有rationale"

**4. 负面示例（告诉LLM不要做什么）**
- "不要问'什么是TCP三次握手'这种纯概念题"
- "不要问'谈谈你对AI的看法'这种过于宽泛的问题"

### 4. 模式切换的Prompt调整

不同模式下，Prompt需要动态调整角色权重和问题类型指导。

#### job模式Prompt片段

```
当前模式：job（工程求职）
角色权重：
- 技术面试官：40%（主导）
- 招聘经理：30%
- HR：20%
- 导师/PI：5%
- 学术评审：5%

问题类型偏重：
- CS基础（算法、数据结构、操作系统、网络）：30%
- 项目深度与真实性：30%
- 系统设计与工程实践：25%
- 软技能与职业规划：15%

特别注意：
- 技术问题要结合简历中的项目，验证真实性和深度
- 招聘经理应关注业务理解和独立性
- 避免过多理论题，优先实战场景题
```

#### grad模式Prompt片段

```
当前模式：grad（学术/读研）
角色权重：
- 导师/PI：40%（主导）
- 学术评审：30%
- 技术面试官：15%
- HR：10%
- 招聘经理：5%

问题类型偏重：
- 研究兴趣与规划：25%
- 研究方法论（问题定义、实验设计）：25%
- 论文阅读与学术规范：20%
- CS基础（研究的基础）：20%
- 科研态度与合作意愿：10%

特别注意：
- 导师应关注候选人的长期研究兴趣和自驱力
- 学术评审应考察科研方法论和批判性思维
- 可以问论文阅读经验，但不要编造具体论文名，用"你读过XXX领域的经典论文吗"
```

#### mixed模式Prompt片段

```
当前模式：mixed（工程+学术双视角）
角色权重：
- 技术面试官：30%
- 导师/PI：30%
- 学术评审：25%
- 招聘经理：20%
- HR：15%
- 候选人守护者：5%

问题类型要求：
- 每个问题必须标注[工程视角]或[学术视角]
- 确保双视角平衡：工程问题和学术问题各占约50%

summary要求：
必须包含两条独立评估：
【工程候选人评估】
...
【科研候选人评估】
...

特别注意：
- 同一个项目可以从两个视角提问
  - [工程视角] 如果部署到生产环境，如何设计监控和容错？
  - [学术视角] 如果写成论文，技术贡献点在哪里？
```

---

## V. 技术架构与模块拆解

本章节定义GrillRadar的技术栈、模块划分、数据流，以及如何借鉴TrendRadar和BettaFish的架构模式。

### 1. 推荐技术栈

#### 后端

**Python + FastAPI**（推荐）
- **优势：**
  - 异步支持，性能好
  - 自动生成API文档（Swagger UI）
  - Pydantic原生集成，数据验证方便
  - 社区活跃，AI/LLM相关库丰富
- **替代方案：** Flask（更轻量，但需手动处理异步）

**Pydantic**
- 用于定义数据模型（`UserConfig`, `QuestionItem`, `Report`）
- 自动验证、序列化/反序列化

#### LLM调用

**llm_client模块**
- 封装对Claude、OpenAI、国产大模型的调用
- 支持流式输出（未来版本）
- 支持多模型切换（环境变量配置）

**推荐库：**
- `anthropic` - Claude官方SDK
- `openai` - OpenAI官方SDK
- `httpx` - 通用HTTP客户端（支持异步）

#### 配置管理

**PyYAML**
- 加载`domains.yaml`, `modes.yaml`等配置文件

**python-dotenv**
- 管理环境变量（API密钥等）

#### 前端（MVP）

**方案1：FastAPI + Jinja2（推荐MVP）**
- 服务端渲染，简单直接
- 适合快速原型

**方案2：React单页应用（未来版本）**
- 用户体验更好
- 适合后续扩展（如多轮对话、实时流式输出）

#### 数据存储（未来版本）

**MVP：**
- 无数据库，纯无状态服务

**未来版本：**
- SQLite / PostgreSQL - 存储用户历史报告
- Redis - 缓存领域知识、问题模板
- 向量数据库（如ChromaDB） - 存储面经、论文等外部知识

### 2. 模块拆解（BettaFish式清晰结构）

#### 目录结构

```
grillradar/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   └── report.py           # POST /generate-report
│   ├── models/                 # Pydantic数据模型
│   │   ├── __init__.py
│   │   ├── user_config.py      # UserConfig
│   │   ├── question_item.py    # QuestionItem
│   │   └── report.py           # Report
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── prompt_builder.py   # 构建虚拟委员会Prompt
│   │   ├── llm_client.py       # LLM调用封装
│   │   └── report_generator.py # 报告生成协调器
│   ├── config/                 # 配置文件
│   │   ├── domains.yaml        # 领域知识配置
│   │   ├── modes.yaml          # 模式权重配置
│   │   └── settings.py         # 应用配置（从.env加载）
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── parsing.py          # 简历文本清洗/分段
│   │   ├── markdown.py         # Report转Markdown
│   │   └── validation.py       # 数据验证辅助函数
│   └── agents/                 # 未来：多Agent模块（预留）
│       ├── __init__.py
│       ├── technical.py        # 技术面试官Agent
│       ├── advisor.py          # 导师Agent
│       └── orchestrator.py     # Agent协调器
├── tests/                      # 测试
│   ├── test_prompt_builder.py
│   ├── test_report_generator.py
│   └── fixtures/               # 测试用简历样本
├── frontend/                   # 前端（MVP可选）
│   ├── templates/              # Jinja2模板
│   │   ├── index.html
│   │   └── report.html
│   └── static/                 # CSS/JS
│       └── style.css
├── .env.example                # 环境变量模板
├── .gitignore
├── requirements.txt            # Python依赖
├── README.md
├── Claude.md                   # 本文档
└── pyproject.toml              # 可选：Poetry配置
```

#### 模块职责说明

**1. `api/report.py` - API路由**
- 定义`POST /generate-report`接口
- 接收`UserConfig` + `resume_text`
- 调用`report_generator`
- 返回`Report` JSON

**2. `models/` - 数据模型**
- 使用Pydantic定义所有数据结构
- 自动验证字段类型和必填项
- 示例：
  ```python
  # models/user_config.py
  from pydantic import BaseModel
  from typing import Optional

  class UserConfig(BaseModel):
      mode: str  # "job" | "grad" | "mixed"
      target_desc: str
      domain: Optional[str] = None
      language: str = "zh"
      level: Optional[str] = None
  ```

**3. `core/prompt_builder.py` - Prompt构建**
- 输入：`UserConfig` + `resume_text`
- 输出：完整的System Prompt字符串
- 逻辑：
  - 加载`domains.yaml`中的领域知识
  - 加载`modes.yaml`中的角色权重
  - 动态注入到Prompt模板中

**4. `core/llm_client.py` - LLM调用**
- 封装对Claude/OpenAI的调用
- 支持重试、超时、错误处理
- 示例：
  ```python
  class LLMClient:
      def call(self, system_prompt: str, user_message: str) -> str:
          # 调用LLM API
          # 返回JSON字符串
          pass
  ```

**5. `core/report_generator.py` - 报告生成协调器**
- 主入口，协调整个生成流程
- 逻辑：
  ```python
  def generate_report(user_config: UserConfig, resume_text: str) -> Report:
      # 1. 构建Prompt
      prompt = prompt_builder.build(user_config, resume_text)
      # 2. 调用LLM
      response = llm_client.call(prompt)
      # 3. 解析并验证JSON
      report_data = json.loads(response)
      report = Report(**report_data)
      # 4. 返回Report对象
      return report
  ```

**6. `config/domains.yaml` - 领域知识配置（TrendRadar式）**
- 预定义常见技术栈和研究领域
- 示例：
  ```yaml
  engineering:
    backend:
      keywords:
        - 分布式系统
        - 微服务
        - 数据库优化
        - 缓存设计
        - 消息队列
      common_stacks:
        - Java
        - Go
        - Python
        - MySQL
        - Redis
        - Kafka
      common_questions:
        - "如何设计一个高并发的分布式系统？"
        - "缓存一致性问题如何解决？"

  research:
    cv_segmentation:
      keywords:
        - 语义分割
        - 实例分割
        - 全景分割
        - Transformer
        - 注意力机制
      canonical_papers:
        - "Mask R-CNN (ICCV 2017)"
        - "SegFormer (NeurIPS 2021)"
        - "Swin Transformer (ICCV 2021)"
      conferences:
        - CVPR
        - ICCV
        - ECCV
  ```

**7. `config/modes.yaml` - 模式配置**
- 定义各模式下的角色权重和问题分布
- 示例：
  ```yaml
  job:
    roles:
      technical_interviewer: 0.40
      hiring_manager: 0.30
      hr: 0.20
      advisor: 0.05
      reviewer: 0.05
    question_distribution:
      cs_fundamentals: 0.30
      project_depth: 0.30
      system_design: 0.25
      soft_skills: 0.15

  grad:
    roles:
      advisor: 0.40
      reviewer: 0.30
      technical_interviewer: 0.15
      hr: 0.10
      hiring_manager: 0.05
    question_distribution:
      research_interest: 0.25
      research_methodology: 0.25
      paper_reading: 0.20
      cs_fundamentals: 0.20
      attitude: 0.10
  ```

**8. `utils/markdown.py` - Markdown导出**
- 将`Report`对象转换为Markdown格式
- 示例：
  ```python
  def report_to_markdown(report: Report) -> str:
      md = f"# GrillRadar 面试准备报告\n\n"
      md += f"**目标岗位：** {report.target_desc}\n\n"
      md += f"## 总体评估\n\n{report.summary}\n\n"
      # ... 生成完整Markdown
      return md
  ```

**9. `agents/` - 未来多Agent模块（预留）**
- 当前为空目录，仅在代码注释中说明未来用途
- 未来版本将拆分为独立的Agent类

### 3. 数据流设计

#### 一次性报告生成流程（MVP）

```
┌─────────────┐
│   用户输入   │
│ (前端表单)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│ POST /generate-report               │
│ Body: {                             │
│   mode: "job",                      │
│   target_desc: "...",               │
│   domain: "backend",                │
│   resume_text: "..."                │
│ }                                   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ API Handler (api/report.py)        │
│ - 验证UserConfig                    │
│ - 调用report_generator              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ ReportGenerator.generate_report()  │
│ (core/report_generator.py)         │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ PromptBuilder.build()              │
│ (core/prompt_builder.py)           │
│ - 加载domains.yaml                 │
│ - 加载modes.yaml                   │
│ - 注入到Prompt模板                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ LLMClient.call()                   │
│ (core/llm_client.py)               │
│ - 调用Claude/OpenAI API            │
│ - 接收JSON响应                     │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 解析 & 验证JSON                    │
│ - json.loads(response)             │
│ - Report(**data)  # Pydantic验证   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 返回Report对象                     │
│ - JSON格式（API响应）              │
│ - 或Markdown（前端渲染）           │
└─────────────────────────────────────┘
```

#### 未来多Agent流程（预留）

```
┌─────────────────────────────────────┐
│ AgentOrchestrator.generate_report()│
└──────┬──────────────────────────────┘
       │
       ├───────────┬───────────┬──────────┬──────────┐
       ▼           ▼           ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Technical│ │Hiring  │ │  HR    │ │Advisor │ │Reviewer│
   │ Agent  │ │Manager │ │ Agent  │ │ Agent  │ │ Agent  │
   └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
        │          │          │          │          │
        └──────────┴──────────┴──────────┴──────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │  ForumEngine     │
                   │ (讨论 & 筛选)    │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  ReportAgent     │
                   │ (生成最终报告)  │
                   └────────┬─────────┘
                            │
                            ▼
                        Report
```

### 4. 扩展方向（借鉴TrendRadar）

#### 未来版本1：外部信息源集成

**目标：** 类似TrendRadar从多平台抓取热点，GrillRadar从多源获取面试信息。

**信息源：**
1. **JD爬虫**
   - 爬取目标公司的真实岗位描述（拉勾、Boss直聘、牛客网）
   - 提取关键技能要求、任职资格

2. **面经聚合**
   - 牛客网面经、LeetCode讨论区
   - 提取高频面试题和追问点

3. **论文热点**
   - arXiv、顶会论文（CVPR、NeurIPS等）
   - 提取最新研究热点和技术趋势

4. **技术博客**
   - 各大公司技术博客（美团技术团队、字节技术等）
   - 提取真实工程实践案例

**架构：**
```
grillradar/
  sources/                  # 信息源模块
    jd_crawler.py           # JD爬虫
    interview_aggregator.py # 面经聚合
    paper_tracker.py        # 论文追踪
  retrieval/                # 检索模块
    vector_store.py         # 向量数据库（ChromaDB）
    keyword_search.py       # 关键词搜索
```

**使用方式：**
- 用户输入目标公司+岗位 → 自动检索相关JD和面经
- Prompt中注入检索到的真实面试题
- 问题更贴近真实面试场景

#### 未来版本2：个性化问题库

**目标：** 用户可以自定义关注的技术栈和研究方向。

**实现：**
- 提供Web界面，用户创建个人配置文件
- 例如："我关注Go后端 + Kubernetes + 云原生"
- 系统根据配置从`domains.yaml`和外部信息源中筛选内容

#### 未来版本3：多轮训练系统

**目标：** 从一次性报告演进为长期训练工具。

**功能：**
- 用户历史记录（答题记录、进步轨迹）
- AI陪练（多轮对话，模拟真实面试）
- 弱点追踪（识别用户薄弱环节，针对性出题）

---

## VI. 开发路线图与里程碑

本章节规划GrillRadar的分阶段开发计划，从MVP到完整产品。

### 里程碑1：CLI原型（本地命令行版本）

**目标：** 验证核心逻辑，无需前端。

**功能：**
- 用户准备两个文件：
  - `config.json` - 包含`mode`, `target_desc`, `domain`等
  - `resume.txt` - 简历原文
- 运行命令：`python cli.py --config config.json --resume resume.txt --output report.md`
- 输出：`report.md`（Markdown格式报告）

**实现模块：**
- `models/` - 数据模型
- `core/prompt_builder.py` - Prompt构建
- `core/llm_client.py` - LLM调用
- `core/report_generator.py` - 报告生成
- `utils/markdown.py` - Markdown导出

**验收标准：**
- ✅ 能根据简历和配置生成10-15个问题
- ✅ 每个问题包含完整的6个字段（question, rationale, baseline_answer等）
- ✅ 输出的Markdown格式正确，便于阅读
- ✅ 支持`job` / `grad` / `mixed`三种模式

**技术风险：**
- LLM输出的JSON格式可能不稳定 → 需要robust的解析和错误处理
- Prompt过长可能超出token限制 → 需要简历预处理和截断策略

**预计时间：** 1-2周

---

### 里程碑2：Web版本（FastAPI + 简单前端）

**目标：** 提供Web界面，降低使用门槛。

**功能：**
- 用户通过Web表单输入：
  - 模式选择（单选：job / grad / mixed）
  - 目标描述（文本框）
  - 领域选择（下拉：backend / llm_application / cv等，可选）
  - 简历上传（文本框或文件上传）
- 点击"生成报告"按钮
- 前端展示报告（Markdown渲染或HTML格式）
- 支持下载报告（Markdown / HTML）

**实现模块：**
- `api/report.py` - FastAPI路由
- `frontend/templates/` - Jinja2模板（`index.html`, `report.html`）
- `frontend/static/` - CSS样式

**验收标准：**
- ✅ 用户可以通过Web界面生成报告
- ✅ 界面简洁、易用（无需复杂操作）
- ✅ 报告展示美观（Markdown渲染或HTML格式）
- ✅ 支持报告下载

**技术风险：**
- LLM调用可能耗时较长（10-30秒） → 需要加载动画或进度提示
- 用户可能上传超长简历 → 需要字数限制和截断

**预计时间：** 1-2周

---

### 里程碑3：配置驱动的领域管理（TrendRadar式）

**目标：** 实现`domains.yaml`配置文件，预定义常见领域知识。

**功能：**
- 在`config/domains.yaml`中定义：
  - 各领域的关键词、常见技术栈、经典论文、常见问题
- 用户选择领域后，系统自动加载对应知识
- Prompt中注入领域知识，使问题更专业

**示例：**
用户选择`domain="backend"` → 系统加载：
```yaml
backend:
  keywords: [分布式系统, 微服务, 数据库优化, 缓存设计, 消息队列]
  common_stacks: [Java, Go, Python, MySQL, Redis, Kafka]
```
→ Prompt中注入："候选人目标是后端工程师，应重点考察分布式系统、数据库、缓存等能力..."

**实现模块：**
- `config/domains.yaml` - 领域知识配置
- `core/prompt_builder.py` - 加载并注入领域知识

**验收标准：**
- ✅ 至少支持5个工程领域（backend, frontend, algorithm, llm_application, data_engineering）
- ✅ 至少支持3个研究领域（cv_segmentation, nlp, multimodal）
- ✅ 选择领域后，生成的问题明显更专业、更有针对性

**技术风险：**
- 领域知识可能过时 → 需要定期更新配置文件

**预计时间：** 1周

---

### 里程碑4：初步外部信息检索支持（可选）

**目标：** 集成简单的外部信息源，增强问题的真实性。

**功能（MVP版本）：**
- 用户提供目标公司+岗位 → 系统搜索相关JD和面经（使用搜索引擎或爬虫）
- 从JD中提取关键技能要求
- 从面经中提取高频问题
- 在Prompt中注入这些信息

**实现模块：**
- `sources/jd_crawler.py` - 简单的JD爬虫（或调用搜索API）
- `retrieval/keyword_search.py` - 关键词提取

**验收标准：**
- ✅ 能从至少1个JD网站（如拉勾网）爬取岗位描述
- ✅ 提取出关键技能要求（如"熟悉Redis"、"了解分布式系统"）
- ✅ Prompt中注入JD信息，生成的问题与真实岗位需求更贴近

**技术风险：**
- 爬虫可能被反爬 → 需要做好请求限流和User-Agent伪装
- JD信息提取可能不准确 → 需要简单的NLP处理

**预计时间：** 2-3周（可选，根据团队资源决定）

---

### 里程碑5：多Agent架构演进（BettaFish式）

**目标：** 将虚拟委员会拆分为真正的独立Agent模块。

**功能：**
- 拆分6个Agent类：
  - `TechnicalInterviewerAgent`
  - `HiringManagerAgent`
  - `HRAgent`
  - `AdvisorAgent`
  - `ReviewerAgent`
  - `AdvocateAgent`
- 每个Agent独立调用LLM，生成初步问题
- `ForumEngine`协调多个Agent的输出，进行讨论和筛选
- `ReportAgent`生成最终报告

**架构：**
```python
class AgentOrchestrator:
    def __init__(self):
        self.technical = TechnicalInterviewerAgent()
        self.hiring_manager = HiringManagerAgent()
        # ...

    async def generate_report(self, user_config, resume_text):
        # 1. 并行调用各Agent
        draft_questions = await asyncio.gather(
            self.technical.propose_questions(resume_text, user_config),
            self.hiring_manager.propose_questions(resume_text, user_config),
            # ...
        )
        # 2. ForumEngine讨论和筛选
        final_questions = self.forum_engine.discuss(draft_questions)
        # 3. ReportAgent生成最终报告
        return self.report_agent.generate(final_questions, user_config)
```

**验收标准：**
- ✅ 各Agent职责清晰，代码模块化
- ✅ ForumEngine能有效合并和筛选问题
- ✅ 相比MVP单次调用，问题质量和多样性有提升

**技术风险：**
- 多次LLM调用成本较高 → 需要优化调用次数
- Agent之间的协作逻辑复杂 → 需要careful设计

**预计时间：** 3-4周

---

### 里程碑6：多轮训练系统（长期愿景）

**目标：** 从一次性报告演进为长期陪练工具。

**功能：**
- 用户注册/登录，保存历史记录
- AI陪练模式：
  - 用户选择一个问题
  - AI扮演面试官/导师，进行多轮追问
  - 根据用户回答给出实时反馈
- 弱点追踪：
  - 记录用户在各类问题上的表现
  - 智能推荐薄弱环节的练习题

**验收标准：**
- ✅ 支持用户注册和历史记录存储
- ✅ 多轮对话体验流畅，追问合理
- ✅ 能识别用户弱点并推荐练习

**技术风险：**
- 需要引入数据库和用户系统 → 架构复杂度大幅提升
- 多轮对话的上下文管理 → 需要careful设计

**预计时间：** 1-2个月（需要较大投入）

---

## VII. 附录

### 1. 名词解释

| 名词 | 解释 |
|------|------|
| **Grilling** | "拷问式提问"，指尖锐、直击要害但不失公平的问题风格 |
| **ForumEngine** | BettaFish中的多Agent协作机制，类似论坛讨论的多轮互动 |
| **Frequency Words** | TrendRadar中的关键词配置文件，用于过滤信息 |
| **MCP** | Model Context Protocol，AI模型上下文协议 |
| **Agent** | 智能体，具有特定职责和能力的独立模块 |
| **Baseline Answer** | 基准答案，提供回答结构和要点，但不编造用户个人经历 |
| **Prompt Template** | 提示词模板，用户可复制到其他AI进行练习 |

### 2. 常见问题（FAQ）

**Q1: 为什么不直接用ChatGPT生成面试题？**

A: ChatGPT生成的问题往往泛泛而谈，缺少与简历和目标岗位的强关联。GrillRadar通过：
- 虚拟委员会多角色视角
- 配置驱动的领域知识
- 明确的rationale和support_notes

确保每个问题都有明确的考察目的和实用价值。

**Q2: MVP为什么不直接做多Agent？**

A: 多Agent架构复杂度高，成本也高（多次LLM调用）。MVP先用单次调用验证产品价值，后续根据用户反馈决定是否演进。

**Q3: 如何防止LLM编造用户经历？**

A: 在Prompt中明确约束："baseline_answer不能编造用户个人经历，只能提供回答结构和技术要点"。同时，在数据验证阶段检查答案是否包含虚假的个人信息。

**Q4: 为什么问题数量限制在10-20个？**

A: 过少覆盖度不足，过多信息过载。10-20个是经过权衡的最佳实践。

**Q5: 未来会支持英文吗？**

A: 会。在`UserConfig`中增加`language`字段，Prompt和输出语言可切换。

### 3. 参考资源

**开源项目：**
- [TrendRadar](https://github.com/sansan0/TrendRadar) - 多平台热点聚合与AI分析
- [BettaFish](https://github.com/666ghj/BettaFish) - 多Agent意见分析系统

**技术文档：**
- FastAPI官方文档：https://fastapi.tiangolo.com/
- Pydantic官方文档：https://docs.pydantic.dev/
- Claude API文档：https://docs.anthropic.com/
- OpenAI API文档：https://platform.openai.com/docs/

**推荐阅读：**
- 《设计数据密集型应用》（Designing Data-Intensive Applications）
- 《系统设计面试》（System Design Interview）
- 《深度学习论文阅读指南》

---

## 更新日志

### 2025-11-17
- 完整重写Claude.md，基于详细的项目需求
- 定义虚拟委员会6大角色和协作流程
- 设计数据模型（UserConfig, QuestionItem, Report）
- 规划技术架构和模块拆解
- 制定6个里程碑的开发路线图

---

**Last Updated:** 2025-11-17
**Document Version:** 2.0
**Maintained By:** GrillRadar Project Team
**Target Audience:** Claude Code, 开发者, 产品经理
