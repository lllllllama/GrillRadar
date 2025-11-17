# GrillRadar

> 面向中国程序员和研究生申请者的深度面试模拟与指导报告生成工具

GrillRadar 通过"虚拟面试/导师委员会"为你生成一份高质量的"深度拷问+辅导报告"，帮助你发现简历中的风险点，并提供针对性的准备建议。

## ✨ 核心特性

- **🎯 精准定制** - 根据简历和目标岗位生成10-20个高度相关的问题
- **🔍 深度拷问** - 每个问题都包含提问理由、基准答案、参考资料
- **💡 可复用提示词** - 每个问题提供练习提示词，可直接喂给AI进行深度练习
- **🎭 多角色视角** - 模拟技术面试官、HR、导师/PI等6个角色的综合评估
- **📊 三种模式** - 支持工程求职（job）、学术申请（grad）、双视角（mixed）

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

复制环境变量模板并配置你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥（至少配置一个）：

```bash
# 使用Claude
ANTHROPIC_API_KEY=sk-ant-...

# 或使用OpenAI
OPENAI_API_KEY=sk-...
```

### 4. 准备配置文件

创建 `config.json`（配置文件示例）：

```json
{
  "mode": "job",
  "target_desc": "字节跳动 - 抖音推荐后端研发工程师（校招）",
  "domain": "backend",
  "level": "junior"
}
```

**字段说明：**
- `mode`: 模式，可选值：
  - `job` - 工程求职
  - `grad` - 学术/读研
  - `mixed` - 双视角
- `target_desc`: 目标岗位或方向的详细描述
- `domain`: 领域（可选），如 `backend`, `llm_application`, `cv_segmentation`
- `level`: 候选人级别（可选），如 `intern`, `junior`, `senior`, `master`, `phd`

### 5. 准备简历

创建 `resume.txt`（纯文本或Markdown格式）：

```
姓名：张三
教育背景：XX大学 计算机科学与技术 本科

项目经历：
1. 分布式爬虫系统
   - 使用Python开发，基于Redis和RabbitMQ
   - 实现了任务去重和容错机制
   - 日均爬取数据100万条

2. 微服务后端系统
   - 使用Go开发RESTful API
   - 接入MySQL和Redis
   ...
```

### 6. 生成报告

```bash
python cli.py --config config.json --resume resume.txt --output report.md
```

报告将保存为 `report.md`，可以直接在Markdown编辑器中打开查看。

## 📖 使用说明

### CLI参数

```bash
python cli.py [参数]

必需参数:
  --config CONFIG    配置文件路径 (JSON格式)
  --resume RESUME    简历文件路径 (纯文本或Markdown)

可选参数:
  --output OUTPUT    输出文件路径 (默认: report.md)
  --format FORMAT    输出格式: markdown | json (默认: markdown)
  --provider PROVIDER  LLM提供商: anthropic | openai
  --model MODEL      LLM模型名称
```

### 示例

**工程求职场景：**
```bash
python cli.py \
  --config examples/job_backend.json \
  --resume examples/resume_backend.txt \
  --output reports/backend_report.md
```

**学术申请场景：**
```bash
python cli.py \
  --config examples/grad_cv.json \
  --resume examples/resume_cv.txt \
  --output reports/grad_report.md
```

**双视角场景：**
```bash
python cli.py \
  --config examples/mixed.json \
  --resume examples/resume_full.txt \
  --output reports/mixed_report.md \
  --format markdown
```

## 📁 项目结构

```
GrillRadar/
├── app/
│   ├── models/           # Pydantic数据模型
│   │   ├── user_config.py
│   │   ├── question_item.py
│   │   └── report.py
│   ├── core/             # 核心业务逻辑
│   │   ├── prompt_builder.py  # Prompt构建
│   │   ├── llm_client.py      # LLM调用
│   │   └── report_generator.py # 报告生成
│   ├── config/           # 配置文件
│   │   ├── domains.yaml       # 领域知识
│   │   ├── modes.yaml         # 模式配置
│   │   └── settings.py
│   └── utils/            # 工具函数
│       └── markdown.py
├── tests/                # 测试
├── cli.py                # CLI入口
├── requirements.txt      # 依赖
├── .env.example          # 环境变量模板
├── Claude.md             # 项目规格说明
└── README.md             # 本文件
```

## 🎯 支持的领域

### 工程领域
- `backend` - 后端开发
- `frontend` - 前端开发
- `llm_application` - LLM应用开发
- `algorithm` - 算法工程师
- `data_engineering` - 数据工程

### 研究领域
- `cv_segmentation` - 图像分割
- `nlp` - 自然语言处理
- `multimodal` - 多模态学习
- `cv_detection` - 目标检测

更多领域配置见 `app/config/domains.yaml`

## 📊 报告示例

生成的报告包含以下部分：

1. **总体评估** - 优势、风险点、准备建议
2. **候选人亮点** - 从简历推断的优势
3. **关键风险点** - 简历暴露的薄弱环节
4. **问题清单** (10-20个) - 每个问题包含：
   - 问题正文
   - 提问理由
   - 如何回答（基准答案结构）
   - 参考资料
   - 练习提示词

## 🔧 配置说明

### 环境变量（.env）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| ANTHROPIC_API_KEY | Claude API密钥 | - |
| OPENAI_API_KEY | OpenAI API密钥 | - |
| DEFAULT_LLM_PROVIDER | 默认LLM提供商 | anthropic |
| DEFAULT_MODEL | 默认模型 | claude-sonnet-4 |
| LLM_TEMPERATURE | 温度参数 | 0.7 |
| LLM_MAX_TOKENS | 最大token数 | 16000 |

### 模式说明

#### job 模式（工程求职）
- 适合：校招、社招、实习面试准备
- 关注：工程技能、项目深度、岗位匹配、软技能
- 角色权重：技术面试官40%、招聘经理30%、HR20%

#### grad 模式（学术申请）
- 适合：硕士推免、考研复试、博士申请、科研岗位
- 关注：研究素养、论文阅读、实验设计、学术规范
- 角色权重：导师/PI 40%、学术评审30%、技术面试官15%

#### mixed 模式（双视角）
- 适合：同时准备求职和读研、工业界研究岗位
- 特点：每个问题标注[工程视角]或[学术视角]
- 报告包含双线评估

## 🛠️ 开发

### 安装开发依赖

```bash
pip install -r requirements.txt
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black app/ tests/ cli.py
```

## 📝 TODO / 路线图

- [x] Milestone 1: CLI原型
- [ ] Milestone 2: Web版本（FastAPI + 前端）
- [ ] Milestone 3: 扩展领域配置
- [ ] Milestone 4: 外部信息源集成（JD、面经）
- [ ] Milestone 5: 多Agent架构演进
- [ ] Milestone 6: 多轮训练系统

详见 `Claude.md` 中的开发路线图。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本项目设计借鉴了：
- [TrendRadar](https://github.com/sansan0/TrendRadar) - 配置驱动的信息聚合
- [BettaFish](https://github.com/666ghj/BettaFish) - 多智能体协作架构

## 📮 联系方式

- 项目地址：https://github.com/lllllllama/GrillRadar
- 问题反馈：https://github.com/lllllllama/GrillRadar/issues

---

**Last Updated:** 2025-11-17
