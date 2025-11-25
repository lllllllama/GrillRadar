<div align="center">

# GrillRadar | 烤网雷达

**[中文](#chinese) | [English](./README.en.md) | [切换语言](./switch_language.py)**

> **AI驱动的程序员与研究生面试准备平台**
>
> *通过6个专业智能体生成深度面试拷问报告*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-91%25+-brightgreen.svg)]()

</div>

---

<a name="chinese"></a>

## 🎯 核心特性

### 为什么选择 GrillRadar？

<table>
<tr>
<td width="50%">

**🤖 多智能体协作**
- 6个专业角色深度评估
- 技术面试官、HR、导师等
- 智能去重和质量过滤

**📊 三种面试模式**
- 求职模式 (job): **30-50题**
- 学术申请模式 (grad): **20-35题**
- 混合模式 (mixed): **25-40题**

</td>
<td width="50%">

**🎯 精准定制**
- **更多更详细的问题** (相比旧版2-3倍)
- 基于简历和目标岗位
- 23个专业领域支持

**💡 实战练习**
- 每个问题含练习提示词
- 提问理由+基准答案
- 参考资料推荐

</td>
</tr>
</table>

---

## 📋 环境要求

| 依赖 | 版本要求 |
|------|----------|
| **Python** | 3.8+ (推荐 3.10+) |
| **pip** | 21.0+ |
| **操作系统** | Windows 10+, Ubuntu 18.04+, macOS 10.15+ |

> ⚠️ **注意**: 部分 OCR 功能需要安装额外依赖，详见 `requirements-ocr.txt`

---

## ⚡ 5分钟快速开始

### 1️⃣ 安装

```bash
# 检查 Python 版本 (需要 3.8+)
python --version

# 克隆项目
git clone https://github.com/lllllllama/GrillRadar.git
cd GrillRadar

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置API（3种方式任选）

<details open>
<summary><b>方式A：交互式向导（推荐）</b></summary>

```bash
python setup_config.py
```
向导会自动引导你完成所有配置 ✨

</details>

<details>
<summary><b>方式B：快速配置</b></summary>

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件，填入API密钥
nano .env
```

</details>

<details>
<summary><b>方式C：查看详细配置文档</b></summary>

查看 [CONFIGURATION.md](./CONFIGURATION.md) 了解：
- 多API提供商支持（Anthropic、OpenAI、Kimi等）
- 高级配置选项
- 故障排除指南

</details>

### 3️⃣ 运行演示

**无需准备简历，一键体验：**

```bash
# 演示1: LLM应用工程师岗位
python examples/run_demo_llm.py

# 演示2: 计算机视觉PhD申请
python examples/run_demo_cv.py
```

### 4️⃣ 使用你的简历

```bash
# 创建配置文件 config.json
cat > config.json << EOF
{
  "target_desc": "字节跳动后端开发工程师",
  "mode": "job",
  "domain": "backend",
  "level": "mid"
}
EOF

# 生成报告（支持PDF、Word、TXT、Markdown）
python cli.py --config config.json --resume 你的简历.pdf
```

✅ **完成！** 报告生成在 `report.md`

---

## 🎬 示例场景演示

GrillRadar 提供了 **3 个真实示例**,展示不同场景下的面试准备:

### 📱 示例 1: LLM 应用工程师求职

**场景**: 阿里巴巴 LLM 应用工程师,目标字节跳动/阿里巴巴

**技术特点**: RAG系统、Prompt工程、Agent框架、开源项目

```bash
python cli.py \
  --config examples/job_llm_app/config.json \
  --resume examples/job_llm_app/resume.md \
  --output llm_report.md
```

**报告亮点**:
- ✅ **40个全面工程面试问题** (深度评估)
- ✅ 涵盖RAG检索、Prompt优化、向量数据库、幻觉检测
- ✅ 考察系统设计、性能优化、大模型基础理论
- ✅ 每个问题附带练习提示词,可复制到ChatGPT/Claude深度练习
- ✅ 融合GitHub/V2EX最新技术趋势

📂 [查看完整示例](./examples/job_llm_app/)

---

### 🎓 示例 2: 计算机视觉 PhD 申请

**场景**: 上海交大本科生,申请美国/香港 CV 方向 PhD

**学术特点**: MICCAI论文投稿、竞赛获奖、开源项目 (350+ stars)

```bash
python cli.py \
  --config examples/grad_cv_segmentation/config.json \
  --resume examples/grad_cv_segmentation/resume.md \
  --output cv_grad_report.md
```

**报告亮点**:
- ✅ **28个深度PhD面试问题** (全方位评估)
- ✅ 涵盖研究创新性、实验严谨性、理论基础、文献综述
- ✅ 考察失败经历、学术诚信、Research Proposal、英语能力
- ✅ 导师视角深度拷问,暴露简历薄弱点
- ✅ 结合最新学术趋势和研究方向

📂 [查看完整示例](./examples/grad_cv_segmentation/)

---

### 🔀 示例 3: 混合模式 - 工程 + PhD 双重准备

**场景**: 字节跳动后端工程师,同时准备分布式系统 PhD 申请

**特点**: 工程经验 + 科研背景 (SOSP投稿、Raft开源项目)

```bash
python cli.py \
  --config examples/mixed_backend_grad/config.json \
  --resume examples/mixed_backend_grad/resume.md \
  --output mixed_report.md
```

**报告亮点**:
- ✅ **32个双视角问题** (16个工程 + 16个学术)
- ✅ 工程侧: 性能优化、系统设计、Raft工程实践
- ✅ 学术侧: 研究创新性、理论基础、PhD规划
- ✅ 交叉问题: 工程vs学术的平衡与价值
- ✅ 同时融合行业和学术最新动态

📂 [查看完整示例](./examples/mixed_backend_grad/)

---

### 💡 如何选择模式?

| 场景 | 模式 | 适用人群 |
|------|------|----------|
| 工程求职 | `mode: job` | 程序员、算法工程师、LLM应用开发者 |
| 学术申请 | `mode: grad` | 研究生、PhD申请者、科研人员 |
| 双重准备 | `mode: mixed` | 工作同时准备读博、纠结工程vs学术 |

👉 **更多详情**: [QUICK_START_ZH.md](./QUICK_START_ZH.md) - 5分钟快速上手指南

---

## 📚 文档导航

### 🔰 新手入门
| 文档 | 说明 |
|------|------|
| [快速开始](#-5分钟快速开始) | 5分钟上手指南 |
| [详细使用指南](./QUICK_START_ZH.md) | 完整的中文使用教程 |
| [示例场景](#-示例场景演示) | 3个真实示例演示 |
| [配置指南](./CONFIGURATION.md) | 详细配置说明 |
| [Web界面](./WEB_INTERFACE.md) | 使用Web版本 |

### 📖 进阶使用
| 文档 | 说明 |
|------|------|
| [支持的领域](./DOMAINS.md) | 23个专业领域详情 |
| [外部信息源](./EXTERNAL_INFO.md) | JD和面经集成 |
| [开发文档](./docs/) | 开发和贡献指南 |

### 🛠️ 工具和脚本
| 工具 | 说明 |
|------|------|
| `switch_language.py` | 一键切换文档语言 |
| `setup_config.py` | 交互式配置向导 |
| `cli.py` | 命令行工具 |

---

## 🚀 最新升级 (2025-01)

### 📡 多源爬虫系统 - 实时技术趋势集成

GrillRadar 现已集成**多源爬虫系统**，自动获取最新技术趋势和面试热点！

<table>
<tr>
<td width="50%">

**🌐 三大数据源**
- ✅ **GitHub Trending** - 开源项目和技术趋势
- ✅ **V2EX社区** - 技术讨论和面试经验
- ✅ **IT之家** - 科技新闻和产品发布

**⚡ 性能优化**
- 持久化缓存机制
- **965倍加速** (5.21s → 0.01s)
- 并行爬取，秒级响应

</td>
<td width="50%">

**🎯 智能特性**
- TrendRadar风格关键词过滤
- 智能去重 (URL + 标题相似度)
- 质量评分系统
- 数据源权重配置

**📊 覆盖领域**
- LLM应用、后端、算法工程
- 22+ 技术领域
- 50+ 技术关键词库

</td>
</tr>
</table>

**启用方式**:
```json
{
  "enable_external_info": true,
  "target_company": "字节跳动"
}
```

**技术架构**: newsnow API + 文件缓存 + 多线程并行

📂 **详细文档**: [EXTERNAL_INFO.md](./EXTERNAL_INFO.md)

---

## 🎨 主要功能

### 📄 多格式简历支持

| 格式 | 扩展名 | 支持 |
|------|--------|------|
| PDF | `.pdf` | ✅ **支持OCR** |
| Word | `.docx`, `.doc` | ✅ |
| 文本 | `.txt` | ✅ 自动编码检测 |
| Markdown | `.md` | ✅ |

**🔍 智能OCR支持（扫描PDF/图片PDF）**

自动识别扫描简历和图片PDF，无缝切换到OCR模式：
- 支持中英文混合识别
- 自动检测文本可选性，智能回退
- 可配置OCR引擎（PaddleOCR/Tesseract）

<details>
<summary><b>启用OCR功能（可选）</b></summary>

1. 安装OCR依赖：
```bash
pip install -r requirements-ocr.txt
```

2. 配置OCR（`.env`文件）：
```bash
# 启用OCR
PDF_OCR_ENABLED=true

# 可选配置
PDF_OCR_ENGINE=paddleocr  # 或 tesseract
PDF_OCR_LANG=ch          # ch/en/ch_en
PDF_OCR_MIN_TEXT=200     # 触发OCR的最小文本长度
```

**工作原理：**
1. 首先尝试标准文本提取（快速）
2. 如果文本不足200字符，自动切换到OCR
3. OCR失败时智能回退到文本提取

**不安装OCR？** 没问题！系统仍能处理普通PDF，只是不支持扫描版。

</details>

### 🔧 多API兼容

| 提供商 | 推荐场景 | 支持 |
|--------|----------|------|
| **Anthropic Claude** | 最佳效果，200K上下文 | ✅ |
| **OpenAI GPT** | 通用选择 | ✅ |
| **Kimi/Moonshot** | 国内用户友好 | ✅ |
| **BigModel（智谱）** | 第三方兼容 | ✅ |
| 自定义端点 | 企业部署 | ✅ |

### 🎯 支持的领域

<details>
<summary><b>工程领域（12个）</b></summary>

- 后端开发 (backend)
- 前端开发 (frontend)
- 大模型应用开发 (llm_application)
- 算法工程 (algorithm)
- 数据工程 (data_engineering)
- 移动开发 (mobile)
- 云原生 (cloud_native)
- 嵌入式开发 (embedded)
- 游戏开发 (game_dev)
- 区块链/Web3 (blockchain)
- 网络安全 (security)
- 测试/质量保障 (test_qa)

</details>

<details>
<summary><b>研究领域（11个）</b></summary>

- 计算机视觉-图像分割 (cv_segmentation)
- 计算机视觉-目标检测 (cv_detection)
- 自然语言处理 (nlp)
- 多模态学习 (multimodal)
- 机器学习（通用）(general_ml)
- 强化学习 (reinforcement_learning)
- 机器人学 (robotics)
- 图学习 (graph_learning)
- 时间序列分析 (time_series)
- 联邦学习/隐私计算 (federated_learning)
- AI安全与对齐 (ai_safety)

</details>

👉 **查看详情**: [DOMAINS.md](./DOMAINS.md)

---

## 🌐 Web界面

启动Web服务器，使用图形界面：

```bash
# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 或使用快捷脚本
bash run_web.sh
```

访问 `http://localhost:8000` 使用Web界面 🚀

**Web界面特性：**
- ✅ 简洁友好的表单界面
- ✅ 文件上传支持
- ✅ 实时报告生成
- ✅ Markdown和HTML双格式下载
- ✅ 响应式设计，支持移动端

👉 **查看详情**: [WEB_INTERFACE.md](./WEB_INTERFACE.md)

---

## 📖 使用示例

### CLI示例

```bash
# 求职场景
python cli.py \
  --config examples/job_backend.json \
  --resume examples/resume_backend.pdf \
  --output report.md

# 学术申请场景
python cli.py \
  --config examples/grad_cv.json \
  --resume examples/resume_cv.docx \
  --output grad_report.md

# 混合模式（工程+学术）
python cli.py \
  --config examples/mixed.json \
  --resume resume.txt \
  --output mixed_report.md
```

### API示例

```bash
# 生成报告（文件上传）
curl -X POST "http://localhost:8000/api/generate-report-upload" \
  -F "mode=job" \
  -F "target_desc=后端开发工程师" \
  -F "domain=backend" \
  -F "resume_file=@resume.pdf"

# 健康检查
curl http://localhost:8000/api/health

# 查看支持的领域
curl http://localhost:8000/api/domains
```

---

## 🏗️ 项目结构

```
GrillRadar/
├── 📱 app/                    # 应用核心
│   ├── agents/                # 6个专业智能体
│   ├── api/                   # FastAPI接口
│   ├── config/                # 配置管理（domains.yaml、modes.yaml）
│   ├── core/                  # 核心逻辑（编排器、ForumEngine）
│   ├── models/                # 数据模型
│   ├── sources/               # 多源爬虫系统 🆕
│   │   └── crawlers/          # GitHub、V2EX、IT之家爬虫
│   │       ├── github_crawler.py
│   │       ├── v2ex_api_crawler.py
│   │       ├── ithome_api_crawler.py
│   │       ├── keyword_filter.py      # TrendRadar风格过滤
│   │       ├── cache_manager.py       # 缓存管理（965倍加速）
│   │       └── trend_aggregator.py    # 智能聚合器
│   └── utils/                 # 工具函数
├── 🌐 frontend/               # Web界面
│   ├── static/                # 静态资源
│   └── templates/             # HTML模板
├── 📝 examples/               # 示例和演示
├── 🧪 tests/                  # 测试文件（91%+覆盖率）
├── 📝 scripts/                # 测试和工具脚本 🆕
│   ├── test_integration_all.py    # 综合集成测试
│   ├── test_keyword_filter.py     # 关键词过滤测试
│   └── test_cache.py              # 缓存机制测试
├── 📚 docs/                   # 文档
│   └── archive/               # 开发文档归档
├── 🔧 cli.py                  # CLI入口
├── 🌍 switch_language.py      # 语言切换工具
└── ⚙️ setup_config.py         # 配置向导
```

---

## 🧑‍💻 开发和贡献

### 运行测试

```bash
# 运行所有测试
pytest

# 查看覆盖率
pytest --cov=app tests/

# 运行特定测试
pytest tests/test_agents.py -v
```

### 代码质量

```bash
# 代码格式化
black app/ tests/ cli.py

# 代码检查
flake8 app/ tests/

# 问题质量评估
python scripts/evaluate_question_quality.py
```

### 添加新领域

1. 编辑 `app/config/domains.yaml`
2. 添加领域配置（关键词、技术栈等）
3. 运行测试验证

### 添加新智能体

1. 在 `app/agents/` 创建新智能体类
2. 继承 `BaseAgent`
3. 在 `agent_orchestrator.py` 中注册
4. 添加测试

---

## 📝 开发路线图

- [x] **Milestone 1**: CLI原型 ✅
- [x] **Milestone 2**: Web版本 ✅
- [x] **Milestone 3**: 配置驱动的领域管理（23个领域）✅
- [x] **Milestone 4**: 外部信息源集成 ✅
- [x] **Milestone 4.5**: 多格式简历支持 ✅
- [x] **Milestone 4.6**: 多API兼容性 ✅
- [x] **Milestone 5**: 多智能体架构（BettaFish风格）✅
- [x] **Milestone 5.5**: 多源爬虫系统升级 ✅
  - 三大数据源（GitHub + V2EX + IT之家）
  - TrendRadar风格关键词过滤
  - 965倍缓存加速
  - 智能去重和质量评分
- [x] **Milestone 5.6**: 问题数量与深度优化 ✅
  - 求职模式: 30-50题（原15-25题）
  - 学术模式: 20-35题（原10-16题）
  - 混合模式: 25-40题（原14-20题）
- [ ] **Milestone 6**: 多轮训练系统 🔄

---

## 🙏 致谢

- **Claude API** - 提供强大的AI能力
- **[BettaFish](https://github.com/666ghj/BettaFish)** - 启发了多智能体架构设计
- **[TrendRadar](https://github.com/sansan0/TrendRadar)** - 启发了多源爬虫系统架构
  - newsnow API集成方案
  - 关键词过滤语法设计
  - 配置驱动的数据聚合思想
- 所有贡献者和用户的反馈 ❤️

---

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)。

---

## 📮 联系方式

- **项目主页**: https://github.com/lllllllama/GrillRadar
- **问题反馈**: [GitHub Issues](https://github.com/lllllllama/GrillRadar/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/lllllllama/GrillRadar/discussions)

---

<div align="center">

**🔥 Happy Grilling! 🔥**

*为中国程序员和研究者精心打造*

[⬆️ 返回顶部](#grillradar--烤网雷达)

</div>
