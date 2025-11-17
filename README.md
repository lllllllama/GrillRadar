<div align="center">

# GrillRadar | 烤网雷达

**[中文](#chinese) | [English](./README.en.md)**

> **AI驱动的程序员与研究生面试准备平台**
> *AI-powered interview preparation platform for programmers and graduate applicants*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-91%25+-brightgreen.svg)]()

</div>

---

<a name="chinese"></a>

## 📖 关于项目

GrillRadar通过虚拟面试/导师委员会生成全面的"深度拷问+辅导报告"，帮助您识别简历中的风险点并提供针对性的准备建议。

## ✨ 核心功能

- **🎯 精准定制** - 基于简历和目标岗位生成10-20个高度相关的问题
- **🔍 深度拷问** - 每个问题包含提问理由、基准答案和参考资料
- **💡 可复用提示词** - 每个问题附带练习提示词，随时与AI深度练习
- **🎭 多角色视角** - 6个专业角色全方位评估：技术面试官、HR、导师/PI等
- **📊 三种模式** - 支持求职(job)、学术申请(grad)、双视角(mixed)
- **🌐 外部信息源** - 集成真实JD和面经数据，生成更贴近实际的问题
- **📄 多格式简历支持** - 支持上传PDF、Word、TXT或Markdown格式简历
- **🔧 多API兼容** - 支持Anthropic、OpenAI、Kimi及第三方兼容端点
- **⚙️ 灵活配置** - 5种配置方式，从交互式向导到手动编辑
- **🤖 多智能体决策** - **NEW!** 6个专业智能体协作生成高质量问题

---

## 🧪 快速演示

**3步体验完整报告生成流程：**

我们提供了两个开箱即用的演示案例，无需准备简历即可体验完整功能：

### 演示1：LLM应用工程师岗位

```bash
# 1. 配置API密钥（首次使用）
cp .env.example .env
# 编辑 .env 文件，填入 ANTHROPIC_API_KEY 或 OPENAI_API_KEY

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行演示
python examples/run_demo_llm.py
```

**输出文件：** `examples/demo_report_llm.md`
**演示简历：** 2年经验的字节跳动LLM工程师，包含RAG系统、文档处理、提示词工程经验

### 演示2：计算机视觉PhD申请

```bash
# 运行演示
python examples/run_demo_cv.py
```

**输出文件：** `examples/demo_report_cv.md`
**演示简历：** 清华大学本科生，医疗影像分割方向，MICCAI竞赛第3名，申请Stanford/MIT PhD

### 演示特点

✅ **真实案例** - 基于实际求职/申请场景构建的虚拟简历
✅ **完整流程** - 自动加载简历→调用AI→生成Markdown报告
✅ **即开即用** - 一行命令体验多智能体协作生成高质量问题

---

## 📋 目录

- [快速演示](#-快速演示)
- [快速开始](#-快速开始)
- [简历格式支持](#-简历格式支持)
- [配置方法](#-配置方法)
- [API兼容性](#-api兼容性)
- [使用示例](#-使用示例)
- [支持的领域](#-支持的领域)
- [项目结构](#-项目结构)
- [开发指南](#️-开发指南)
- [路线图](#-路线图)

---

## 🚀 快速开始

### 1. 环境准备

**系统要求：**
- Python 3.8+
- pip

**克隆项目：**
```bash
git clone https://github.com/lllllllama/GrillRadar.git
cd GrillRadar
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

**选项1：交互式配置向导（推荐新手）**

```bash
# Python向导，带彩色输出和逐步引导
python setup_config.py

# Bash脚本（Linux/macOS）
bash setup_config.sh
```

**选项2：手动配置**

复制环境模板并配置API密钥：

```bash
cp .env.example .env
```

编辑`.env`并填入至少一个API密钥：

```bash
# 使用Claude（推荐）
ANTHROPIC_API_KEY=sk-ant-...

# 或使用OpenAI
OPENAI_API_KEY=sk-...

# 或使用Kimi（Moonshot AI，适合国内用户）
OPENAI_API_KEY=sk-...  # Kimi使用OpenAI兼容API
OPENAI_BASE_URL=https://api.moonshot.cn/v1

# 或使用第三方Anthropic兼容服务（如国内的BigModel）
ANTHROPIC_AUTH_TOKEN=your_token_here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
```

**详细配置说明**请参阅 [CONFIGURATION.md](./CONFIGURATION.md)

### 4. 准备配置文件

创建`config.json`：

```json
{
  "target_desc": "字节跳动后端开发工程师",
  "mode": "job",
  "domain": "backend",
  "level": "mid",
  "enable_external_info": false
}
```

**字段说明：**
- `target_desc`: 目标岗位/方向描述（必填）
- `mode`: 模式选择（必填）
  - `job` - 求职模式
  - `grad` - 研究生申请模式
  - `mixed` - 混合模式（同时准备工程岗位和学术申请）
- `domain`: 领域选择（可选，见下方支持的领域）
- `level`: 候选人级别（可选）
  - `junior` - 初级/本科生
  - `mid` - 中级/硕士
  - `senior` - 高级/博士
- `enable_external_info`: 是否启用外部信息源（可选，默认false）

### 5. 运行生成报告

```bash
# 使用文本简历
python main.py --config config.json --resume resume.txt

# 使用PDF简历
python main.py --config config.json --resume resume.pdf

# 使用Word简历
python main.py --config config.json --resume resume.docx
```

生成的报告将保存为`report.json`。

---

## 📄 简历格式支持

GrillRadar支持多种简历格式，自动检测编码并提取内容：

| 格式 | 扩展名 | 特性 |
|------|--------|------|
| **纯文本** | `.txt` | 自动编码检测（UTF-8/GBK/GB2312） |
| **Markdown** | `.md` | 保留格式结构 |
| **PDF** | `.pdf` | 提取文本和表格内容 |
| **Word** | `.docx`, `.doc` | 提取文本、表格和格式 |

**使用示例：**

```bash
# PDF简历
python main.py --config config.json --resume my_resume.pdf

# Word简历
python main.py --config config.json --resume my_resume.docx

# 纯文本简历
python main.py --config config.json --resume my_resume.txt
```

---

## ⚙️ 配置方法

GrillRadar提供5种灵活的配置方法，满足不同用户需求：

### 方法1：交互式向导（最简单）

```bash
python setup_config.py
```

向导将引导您：
1. 选择API提供商（Anthropic/OpenAI/Kimi/第三方）
2. 输入API密钥
3. 配置基础URL（可选）
4. 验证配置
5. 自动生成`.env`文件

### 方法2：命令行参数

```bash
python main.py \
  --resume resume.txt \
  --target "字节跳动后端工程师" \
  --mode job \
  --domain backend \
  --level mid
```

### 方法3：JSON配置文件

创建`config.json`（见快速开始第4步）

### 方法4：环境变量

```bash
export GRILLRADAR_TARGET_DESC="字节跳动后端工程师"
export GRILLRADAR_MODE="job"
export GRILLRADAR_DOMAIN="backend"
python main.py --resume resume.txt
```

### 方法5：Web API（开发中）

```bash
# 启动FastAPI服务器
uvicorn app.api.main:app --reload --port 8000

# 使用API
curl -X POST "http://localhost:8000/api/report/generate" \
  -H "Content-Type: multipart/form-data" \
  -F "resume=@resume.pdf" \
  -F "target_desc=字节跳动后端工程师" \
  -F "mode=job"
```

详细配置说明请参阅 [CONFIGURATION.md](./CONFIGURATION.md)

---

## 🔧 API兼容性

GrillRadar支持多个LLM API提供商，并提供自动检测和健康检查：

### 支持的提供商

| 提供商 | 模型示例 | 适用场景 |
|--------|----------|----------|
| **Anthropic Claude** | claude-sonnet-4, claude-opus-4 | 推荐，最佳效果 |
| **OpenAI** | gpt-4, gpt-4-turbo | 通用选择 |
| **Kimi (Moonshot)** | moonshot-v1-8k/32k/128k | 国内用户友好 |
| **第三方兼容** | 任何Anthropic兼容端点 | 灵活部署 |

### 自动检测

系统会自动检测您的配置并选择合适的API提供商：

```bash
# 检查当前配置
python -m app.utils.api_compatibility check

# 比较不同提供商
python -m app.utils.api_compatibility compare
```

### 健康检查

```bash
# 验证API连接
python -m app.utils.api_compatibility health

# 输出示例
✓ Provider: Anthropic
✓ Model: claude-sonnet-4
✓ API Key: Valid
✓ Connection: Healthy
```

详细API配置请参阅 [CONFIGURATION.md](./CONFIGURATION.md#api-compatibility)

---

## 📚 使用示例

### 示例1：求职模式 - 后端工程师

```bash
python main.py \
  --resume backend_resume.pdf \
  --target "字节跳动后端开发工程师" \
  --mode job \
  --domain backend \
  --level mid
```

**生成报告包含：**
- 10-20个针对性面试问题
- 技术深度、系统设计、项目经验评估
- 软技能和文化契合度分析
- 每个问题的提问理由和准备建议

### 示例2：研究生申请 - 计算机视觉

```bash
python main.py \
  --resume cv_resume.pdf \
  --target "Stanford PhD in Computer Vision" \
  --mode grad \
  --domain cv_segmentation \
  --level mid
```

**生成报告包含：**
- 研究方法论和论文阅读能力评估
- 学术潜力和科研经历分析
- 导师契合度评估
- 推荐阅读论文和学习资源

### 示例3：混合模式 - 工程+学术

```bash
python main.py \
  --resume mixed_resume.pdf \
  --target "AI Research Engineer at OpenAI" \
  --mode mixed \
  --domain llm_application \
  --level senior
```

**生成报告包含：**
- 双视角评估（工程能力+研究潜力）
- 平衡的问题分布（工程实践+学术深度）
- 综合建议

---

## 🗂️ 支持的领域

GrillRadar现支持**23个专业领域**（工程12个 + 研究11个）：

### 工程领域（12个）

| 领域ID | 领域名称 | 关键词示例 |
|--------|----------|------------|
| `backend` | 后端开发 | 分布式系统、微服务、数据库优化 |
| `frontend` | 前端开发 | React/Vue、前端工程化、性能优化 |
| `llm_application` | 大模型应用开发 | RAG、Prompt工程、Agent |
| `algorithm` | 算法工程 | 推荐系统、搜索排序、机器学习 |
| `data_engineering` | 数据工程 | 数据仓库、ETL、大数据处理 |
| `mobile` | 移动开发 | iOS/Android、跨平台开发 |
| `cloud_native` | 云原生 | Kubernetes、Docker、DevOps |
| `embedded` | 嵌入式开发 | 物联网、RTOS、驱动开发 |
| `game_dev` | 游戏开发 | 游戏引擎、图形渲染、物理引擎 |
| `blockchain` | 区块链/Web3 | 智能合约、DeFi、NFT |
| `security` | 网络安全 | 渗透测试、安全架构、漏洞挖掘 |
| `test_qa` | 测试/质量保障 | 自动化测试、性能测试 |

### 研究领域（11个）

| 领域ID | 领域名称 | 关键领域 |
|--------|----------|----------|
| `cv_segmentation` | 计算机视觉-图像分割 | 语义分割、实例分割、医疗影像 |
| `cv_detection` | 计算机视觉-目标检测 | 实时检测、小目标检测、3D检测 |
| `nlp` | 自然语言处理 | 大语言模型、文本生成、信息抽取 |
| `multimodal` | 多模态学习 | 视觉-语言、跨模态检索 |
| `general_ml` | 机器学习（通用） | 优化理论、模型压缩、迁移学习 |
| `reinforcement_learning` | 强化学习 | RLHF、Multi-agent、决策智能 |
| `robotics` | 机器人学 | SLAM、运动规划、机器人控制 |
| `graph_learning` | 图学习 | 图神经网络、知识图谱 |
| `time_series` | 时间序列分析 | 时序预测、异常检测、因果推断 |
| `federated_learning` | 联邦学习/隐私计算 | 差分隐私、安全多方计算 |
| `ai_safety` | AI安全与对齐 | RLHF、模型可解释性、对抗样本 |

**使用示例：**
```bash
# 工程领域
python main.py --domain backend ...
python main.py --domain blockchain ...

# 研究领域
python main.py --domain cv_segmentation ...
python main.py --domain robotics ...
```

---

## 🏗️ 项目结构

```
GrillRadar/
├── app/
│   ├── agents/                # 多智能体系统（Milestone 5）
│   │   ├── base_agent.py      # 智能体基类
│   │   ├── models.py          # 智能体数据模型
│   │   ├── technical_interviewer.py   # 技术面试官
│   │   ├── hiring_manager.py          # 招聘经理
│   │   ├── hr_agent.py                # HR专员
│   │   ├── advisor_agent.py           # 学术导师
│   │   ├── reviewer_agent.py          # 学术评审
│   │   └── advocate_agent.py          # 候选人倡导者
│   ├── api/                   # FastAPI接口
│   ├── config/                # 配置管理
│   │   ├── domains.yaml       # 领域知识库（23个领域）
│   │   ├── modes.yaml         # 模式配置
│   │   └── settings.py        # 系统设置
│   ├── core/                  # 核心逻辑
│   │   ├── agent_orchestrator.py  # 智能体编排器
│   │   ├── forum_engine.py        # ForumEngine协调层
│   │   ├── prompt_builder.py      # Prompt构建器
│   │   └── report_generator.py    # 报告生成器
│   ├── models/                # 数据模型
│   ├── parsers/               # 简历解析器（PDF/Word/TXT）
│   ├── sources/               # 外部信息源
│   └── utils/                 # 工具函数
│       ├── api_compatibility.py   # API兼容层
│       └── domain_helper.py       # 领域辅助工具
├── tests/                     # 测试文件
├── main.py                    # CLI入口
├── setup_config.py            # 配置向导
└── requirements.txt           # 依赖列表
```

---

## 🧑‍💻 开发指南

### 安装开发依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_domain_helper.py -v

# 查看测试覆盖率
pytest --cov=app tests/
```

### 质量控制

评估生成问题的质量：

```bash
# 运行质量评估（所有测试用例）
python scripts/evaluate_question_quality.py

# 运行特定场景
python scripts/evaluate_question_quality.py --case job_backend

# 查看详细建议
python scripts/evaluate_question_quality.py --verbose
```

质量检查维度：
- ✓ 问题清晰度和长度
- ✓ 提问理由的上下文相关性
- ✓ 基准答案的结构和深度
- ✓ 支持资料的具体性
- ✓ 练习模板的有效性

详细文档：[docs/QUALITY_CONTROL.md](./docs/QUALITY_CONTROL.md)

### 代码风格

```bash
# 使用black格式化代码
black app/ tests/

# 使用flake8检查
flake8 app/ tests/
```

### 添加新领域

1. 编辑`app/config/domains.yaml`
2. 在`engineering`或`research`部分添加新领域
3. 运行测试验证：`pytest tests/test_domain_helper.py`

### 添加新智能体

1. 在`app/agents/`创建新智能体类（继承`BaseAgent`）
2. 在`app/core/agent_orchestrator.py`中注册
3. 添加测试：`tests/test_agents.py`

---

## 📝 路线图

- [x] **Milestone 1**: CLI原型 ✅
- [x] **Milestone 2**: Web版本（FastAPI + 前端） ✅
- [x] **Milestone 3**: 配置驱动的领域管理 ✅
  - 23个领域（12工程 + 11研究）
  - 详细领域配置（关键词、技术栈、论文、阅读材料）
  - 增强的Prompt注入
  - 领域管理API和工具
- [x] **Milestone 4**: 外部信息源集成（JD、面经） ✅
  - Mock数据提供者（演示模式）
  - JD和面经数据模型
  - 信息聚合和关键词提取
  - 外部信息自动注入Prompt
  - 外部信息查询API
- [x] **Milestone 4.5**: 多格式简历支持 ✅
  - PDF、Word、文本、Markdown解析器
  - 编码检测和处理
  - 文件上传API端点
  - 全面测试
- [x] **Milestone 4.6**: 多API兼容性 ✅
  - 支持Anthropic、OpenAI、Kimi、第三方服务
  - 自动检测和验证
  - 健康检查和监控
  - 交互式配置向导
- [x] **Milestone 5**: 多智能体架构演进（BettaFish风格） ✅
  - 6个专业智能体：技术面试官、招聘经理、HR、导师、评审、倡导者
  - ForumEngine协调和共识机制
  - 并行智能体执行与优雅降级
  - 去重、质量过滤和问题增强
  - 全面测试覆盖（91%+通过率）
- [ ] **Milestone 6**: 多轮训练系统

详细开发路线图请参阅`Claude.md`。

---

## 🤝 贡献

欢迎贡献！请查看[贡献指南](CONTRIBUTING.md)。

主要贡献方向：
- 添加新的专业领域到`domains.yaml`
- 改进多智能体协作策略
- 优化Prompt模板
- 添加新的简历解析器
- 改进测试覆盖率

---

## 📄 许可证

本项目采用[MIT许可证](LICENSE)。

---

## 🙏 致谢

- Claude API提供强大的AI能力
- BettaFish项目启发了多智能体架构设计
- 感谢所有贡献者和用户的反馈

---

## 📮 联系方式

- Issues: [GitHub Issues](https://github.com/lllllllama/GrillRadar/issues)
- Discussions: [GitHub Discussions](https://github.com/lllllllama/GrillRadar/discussions)

---

**Happy Grilling! 🔥**

*Built with ❤️ for Chinese programmers and researchers*
