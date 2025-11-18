# GrillRadar 快速上手指南

> 🎯 **5分钟快速体验 AI 面试准备工具**
>
> 专为中国程序员和研究生申请者打造的面试拷问报告生成器

---

## 什么是 GrillRadar?

GrillRadar 是一个 **AI 驱动的面试准备工具**,通过分析你的简历和目标岗位,生成 **10-20 个深度拷问问题**,帮助你提前准备面试。

### 核心特色

✅ **三种模式**:
- **job** (工程求职): 技术面试官视角,考察工程能力
- **grad** (学术申请): 导师/PI视角,考察科研潜力
- **mixed** (双重视角): 同时准备工程面试和PhD申请

✅ **每个问题包含**:
- 问题正文 (针对你的简历定制)
- 提问理由 (为什么问这个问题)
- 基准答案 (回答框架和要点)
- 支撑材料 (相关技术、推荐阅读)
- **练习提示词** (复制后喂给ChatGPT/Claude,深度练习)

---

## 快速开始

### 步骤 1: 安装依赖

```bash
# 克隆项目
git clone https://github.com/lllllllama/GrillRadar.git
cd GrillRadar

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 配置 API 密钥

GrillRadar 需要调用大模型 API (支持 Claude、GPT、Kimi 等)。

#### 方式 A: 交互式配置 (推荐)

```bash
python setup_config.py
```

按照向导提示,选择 API 提供商并填入密钥即可。

#### 方式 B: 手动配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件,填入你的 API 密钥
nano .env
```

**示例配置** (使用 Claude API):
```bash
# .env 文件
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxx你的密钥xxx
ANTHROPIC_MODEL=claude-sonnet-4
```

**支持的 API 提供商**:
- **Claude** (Anthropic): 推荐,效果最好,200K上下文
- **GPT** (OpenAI): gpt-4, gpt-3.5-turbo
- **Kimi** (Moonshot): 国内友好
- 其他兼容 OpenAI 格式的 API

> 💡 **提示**: 如果没有 API 密钥,可以先查看 [示例报告](#步骤-4-查看示例报告) 了解效果。

### 步骤 3: 准备简历和配置

#### 3.1 准备简历文件

GrillRadar 支持多种格式:
- `.pdf` (PDF 文档,支持 OCR 扫描件)
- `.docx` (Word 文档)
- `.txt` (纯文本)
- `.md` (Markdown)

**示例**: 将你的简历保存为 `my_resume.pdf`

#### 3.2 创建配置文件

创建一个 `config.json` 文件,描述你的目标岗位:

```json
{
  "mode": "job",
  "target_desc": "字节跳动后端开发工程师",
  "domain": "backend",
  "level": "junior",
  "language": "zh"
}
```

**配置参数说明**:

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `mode` | 面试模式 | `job` (工程求职) / `grad` (学术申请) / `mixed` (双重视角) |
| `target_desc` | 目标岗位/学校 | 自由描述,如 "字节跳动后端工程师" / "Stanford CV PhD" |
| `domain` | 技术领域 | `backend`, `llm_application`, `cv_segmentation`, `nlp` 等 ([查看完整列表](./DOMAINS.md)) |
| `level` | 候选人级别 | `intern`, `junior`, `senior`, `master`, `phd` |
| `language` | 输出语言 | `zh` (简体中文) / `en` (英文) |

### 步骤 4: 生成面试报告

运行以下命令生成报告:

```bash
python cli.py \
  --config config.json \
  --resume my_resume.pdf \
  --output report.md
```

**等待 1-2 分钟**,报告将生成在 `report.md` 文件中。

---

## 示例场景演示

GrillRadar 提供了 **3 个真实示例**,涵盖不同场景:

### 示例 1: LLM 应用工程师求职

**场景**: 阿里巴巴 LLM 工程师,想跳槽到字节跳动

```bash
python cli.py \
  --config examples/job_llm_app/config.json \
  --resume examples/job_llm_app/resume.md \
  --output my_llm_report.md
```

**报告内容**: 15个问题,涵盖 RAG、Prompt工程、Agent系统、性能优化、大模型基础理论

### 示例 2: 计算机视觉 PhD 申请

**场景**: 上海交大本科生,申请美国/香港 CV 方向 PhD

```bash
python cli.py \
  --config examples/grad_cv_segmentation/config.json \
  --resume examples/grad_cv_segmentation/resume.md \
  --output my_grad_report.md
```

**报告内容**: 12个问题,涵盖研究创新性、实验严谨性、理论基础、PhD规划、学术诚信

### 示例 3: 混合模式 - 工程 + PhD

**场景**: 字节跳动后端工程师,同时准备分布式系统 PhD 申请

```bash
python cli.py \
  --config examples/mixed_backend_grad/config.json \
  --resume examples/mixed_backend_grad/resume.md \
  --output my_mixed_report.md
```

**报告内容**: 10个问题,双视角 (5个工程问题 + 5个学术问题)

---

## 如何使用生成的报告?

报告生成后,你会得到类似这样的内容:

```markdown
# GrillRadar 面试准备报告

## 问题 1
**角色**: 技术面试官
**标签**: 分布式系统

**问题**: 你的简历中提到"设计分布式爬虫系统",请详细描述你如何解决任务分发与调度问题?

**提问理由**: 这个问题考察候选人对分布式系统核心问题的理解深度...

**基准答案**: 一个好的回答应包含:
1. 任务分发架构 (Master-Worker)
2. 使用的消息队列 (RabbitMQ/Kafka)
3. 去重策略 (布隆过滤器)
4. 容错机制 (任务重试)
...

**支撑材料**:
- 关键技术: 消息队列、布隆过滤器、幂等性
- 推荐阅读: 《设计数据密集型应用》第11章
- 搜索关键词: "distributed task queue"

**练习提示词**:
我在简历中写了"分布式爬虫系统",面试官问我如何解决任务分发问题。我的实际情况是: {你的具体实现}。请帮我组织一个有技术深度的回答。
```

### 使用方法:

#### 1️⃣ 阅读理解

- 仔细阅读每个问题的 **提问理由**,理解面试官的考察点
- 对照 **基准答案**,检查自己是否能回答到位
- 阅读 **支撑材料**,补充知识盲点

#### 2️⃣ 使用练习提示词 (重点!)

每个问题都有一个 **练习提示词**,这是 GrillRadar 的核心功能!

**操作步骤**:
1. 复制问题底部的 `练习提示词`
2. 将 `{你的具体实现}` 替换为你的真实经历
3. 粘贴到 **ChatGPT** / **Claude** / **Kimi** 等对话框
4. AI 会帮你生成一个结构化、有深度的回答
5. 反复练习,直到你能流畅表达

**示例**:

原始提示词:
```
我在简历中写了"分布式爬虫系统",面试官问我如何解决任务分发问题。我的实际情况是: {你的具体实现}。请帮我组织一个有技术深度的回答。
```

填入真实经历后:
```
我在简历中写了"分布式爬虫系统",面试官问我如何解决任务分发问题。我的实际情况是: 我使用了RabbitMQ作为消息队列,采用Master-Worker架构,Master负责URL调度,Worker从队列拉取任务。去重使用了Redis的Set数据结构,任务失败会自动重试3次。请帮我组织一个有技术深度的回答。
```

粘贴到 ChatGPT,得到:
```
面试官,关于分布式爬虫的任务分发问题,我的设计是这样的:

首先,架构上我采用了Master-Worker模式。Master节点负责URL调度和任务分发,多个Worker节点并行执行爬取任务。

在任务分发方面,我使用了RabbitMQ消息队列。具体来说:
1. Master将待爬取的URL封装为任务消息,发送到RabbitMQ
2. Worker通过订阅队列,拉取任务并执行爬取
3. 这样做的好处是解耦了生产者和消费者,支持动态扩展Worker数量

关于去重策略,我使用了Redis的Set数据结构存储已爬取的URL。在Master发布任务前,先检查Redis,避免重复爬取。之所以选择Redis而非布隆过滤器,是因为我们的URL总量在千万级别,Redis的内存开销可接受,且能保证100%准确。

在容错方面,我实现了任务重试机制。Worker爬取失败时,会将任务重新放回队列,最多重试3次。如果3次都失败,则记录到死信队列,人工介入处理。

这个设计在实际运行中,支撑了每天200万URL的爬取量,系统稳定性达到99.5%。

(停顿,观察面试官反应)

如果您对某个细节感兴趣,我可以进一步展开说明。
```

**这就是练习提示词的威力!** 🚀

#### 3️⃣ 反复练习

- 对每个问题都使用练习提示词,生成个性化回答
- 大声朗读或录音,模拟真实面试场景
- 请朋友或mentor进行mock interview

#### 4️⃣ 补充学习

- 根据 **支撑材料** 推荐的资源,深入学习薄弱环节
- 使用 **搜索关键词** 查找更多资料
- 准备1-2个真实项目的详细技术细节

---

## 常见问题 (FAQ)

### Q1: 我没有 API 密钥怎么办?

**A**: 你可以:
1. 先查看 `examples/` 目录下的示例报告,了解效果
2. 申请免费 API 密钥:
   - **Kimi**: https://platform.moonshot.cn/ (国内友好,有免费额度)
   - **Claude**: https://console.anthropic.com/ (需要国外信用卡)
   - **OpenAI**: https://platform.openai.com/ (需要国外信用卡)

### Q2: 生成一次报告需要多少钱?

**A**: 成本很低,取决于简历长度和选择的模型:
- **Claude Sonnet 4**: 约 ¥1-3 元/次
- **GPT-4**: 约 ¥2-5 元/次
- **Kimi**: 更便宜,约 ¥0.5-1 元/次

### Q3: 支持哪些技术领域?

**A**: GrillRadar 支持 **23 个专业领域**,包括:

**工程领域** (12个):
- 后端开发 (backend)
- 前端开发 (frontend)
- **LLM 应用开发** (llm_application) ⭐
- 算法工程 (algorithm)
- 数据工程 (data_engineering)
- 移动开发 (mobile)
- 云原生 (cloud_native)
- 嵌入式 (embedded)
- 游戏开发 (game_dev)
- 区块链 (blockchain)
- 网络安全 (security)
- 测试/QA (test_qa)

**研究领域** (11个):
- **计算机视觉 - 图像分割** (cv_segmentation) ⭐
- 计算机视觉 - 目标检测 (cv_detection)
- 自然语言处理 (nlp)
- 多模态学习 (multimodal)
- 机器学习 (general_ml)
- 强化学习 (reinforcement_learning)
- 机器人学 (robotics)
- 图学习 (graph_learning)
- 时间序列 (time_series)
- 联邦学习 (federated_learning)
- AI 安全 (ai_safety)

完整列表见 [DOMAINS.md](./DOMAINS.md)

### Q4: 报告生成需要多长时间?

**A**: 通常 **1-3 分钟**,取决于:
- 简历长度 (越长越慢)
- API 响应速度
- 是否启用多智能体模式 (更慢但质量更高)

### Q5: 可以修改问题数量吗?

**A**: 默认生成 **10-20 个问题**。问题数量由 AI 根据简历内容自动决定,暂不支持手动设置。

### Q6: 报告是中文还是英文?

**A**: 由 `config.json` 中的 `language` 参数控制:
- `"language": "zh"` → 中文报告
- `"language": "en"` → 英文报告

### Q7: 我的简历会被保存吗?

**A**: **不会**。GrillRadar 在本地运行,你的简历只会:
1. 被发送到你配置的 LLM API (如 Claude/GPT)
2. 用于生成报告
3. **不会被保存到任何服务器**

### Q8: 生成的问题太难/太简单怎么办?

**A**: 调整 `config.json` 中的 `level` 参数:
- `"level": "intern"` → 简单问题 (实习生水平)
- `"level": "junior"` → 中等问题 (初级工程师)
- `"level": "senior"` → 困难问题 (高级工程师/专家)
- `"level": "master"` → 研究生水平
- `"level": "phd"` → 博士水平

---

## 进阶使用

### 启用多智能体模式

GrillRadar 支持 **多智能体协作** 模式,由 6 个专业 AI 角色协作生成报告,质量更高:

```bash
python cli.py \
  --config config.json \
  --resume my_resume.pdf \
  --output report.md \
  --multi-agent  # 启用多智能体模式
```

**优势**:
- 问题更全面 (不同角色的视角)
- 自动去重和质量过滤
- 智能难度平衡

**劣势**:
- 生成时间更长 (3-5 分钟)
- API 调用成本略高

### 集成外部信息源

启用后,GrillRadar 会从 JD 数据库和面经库检索相关信息:

```json
{
  "mode": "job",
  "target_desc": "字节跳动后端工程师",
  "domain": "backend",
  "enable_external_info": true,
  "target_company": "字节跳动"
}
```

### 使用 Web 界面

如果你不喜欢命令行,可以使用 Web 界面:

```bash
# 启动 Web 服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 浏览器访问
open http://localhost:8000
```

详见 [WEB_INTERFACE.md](./WEB_INTERFACE.md)

---

## 最佳实践

### ✅ 面试准备流程

1. **生成报告** (1-3 分钟)
2. **快速浏览** (10 分钟): 看问题和提问理由,了解考察点
3. **深度准备** (2-3 小时):
   - 对每个问题使用练习提示词,生成回答
   - 大声朗读,模拟面试场景
   - 标记不熟悉的技术点
4. **补充学习** (1-2 天):
   - 根据支撑材料,学习薄弱环节
   - 准备项目细节和代码实现
5. **模拟面试** (1 小时):
   - 请朋友或用 AI 进行 mock interview
   - 录音回放,改进表达

### ✅ 简历撰写建议

为了让 GrillRadar 生成更好的报告,简历应该:

- **具体**: 不要只写 "参与XX项目",而要写 "负责XX模块,使用YY技术,实现ZZ功能"
- **量化**: 提供数据支撑,如 "性能提升30%", "QPS从1000提升至5000"
- **技术细节**: 写清楚技术栈、架构设计、遇到的挑战
- **避免空话**: 少用 "熟悉"、"了解",多用 "实现"、"优化"、"设计"

### ✅ 使用练习提示词的技巧

- **真实**: 填入你的真实经历,不要编造
- **具体**: 越详细越好,AI 才能生成有深度的回答
- **迭代**: 如果第一次生成的回答不满意,可以补充信息重新生成
- **多模型**: 尝试用不同的 AI (ChatGPT, Claude, Kimi) 生成,对比效果

---

## 获取帮助

- **文档**: [README.md](./README.md) | [配置指南](./CONFIGURATION.md) | [领域列表](./DOMAINS.md)
- **示例**: `examples/` 目录下有 3 个完整示例
- **问题反馈**: [GitHub Issues](https://github.com/lllllllama/GrillRadar/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/lllllllama/GrillRadar/discussions)

---

## 下一步

- 🚀 [立即生成你的第一份报告](#步骤-1-安装依赖)
- 📚 [查看完整文档](./README.md)
- 💡 [了解支持的领域](./DOMAINS.md)
- 🌐 [尝试 Web 界面](./WEB_INTERFACE.md)

---

<div align="center">

**🔥 Happy Grilling! 🔥**

*为中国程序员和研究者精心打造*

[返回首页](./README.md)

</div>
