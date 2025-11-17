# GrillRadar

> **AI-powered interview preparation platform for Chinese programmers and graduate school applicants**

GrillRadar generates comprehensive "deep grilling + guidance reports" through a virtual interview/advisor committee, helping you identify risks in your resume and providing targeted preparation advice.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen.svg)]()

## ✨ Core Features

- **🎯 Precision Customization** - Generate 10-20 highly relevant questions based on your resume and target position
- **🔍 Deep Grilling** - Each question includes rationale, baseline answer, and reference materials
- **💡 Reusable Prompts** - Practice prompts for each question, ready to use with AI for deep practice
- **🎭 Multi-role Perspectives** - Comprehensive evaluation from 6 roles: tech interviewers, HR, mentors/PIs, etc.
- **📊 Three Modes** - Support for job hunting (job), academic applications (grad), dual perspective (mixed)
- **🌐 External Information Sources** - Integrate real JD and interview experience data for more realistic questions
- **📄 Multi-format Resume Support** - **NEW!** Upload PDF, Word, TXT, or Markdown resumes
- **🔧 Multi-API Compatibility** - **NEW!** Support for Anthropic, OpenAI, and third-party compatible endpoints
- **⚙️ Flexible Configuration** - **NEW!** 5 configuration methods from interactive wizard to manual editing

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Resume Format Support](#-resume-format-support)
- [Configuration Methods](#-configuration-methods)
- [API Compatibility](#-api-compatibility)
- [Usage Examples](#-usage-examples)
- [Supported Domains](#-supported-domains)
- [Project Structure](#-project-structure)
- [Development](#️-development)
- [Roadmap](#-roadmap)

---

## 🚀 Quick Start

### 1. Environment Preparation

**System Requirements:**
- Python 3.8+
- pip

**Clone the project:**
```bash
git clone https://github.com/lllllllama/GrillRadar.git
cd GrillRadar
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

**Option 1: Interactive Configuration Wizard (Recommended for beginners)**

```bash
# Python wizard with colored output and step-by-step guidance
python setup_config.py

# Bash script for Linux/macOS
bash setup_config.sh
```

**Option 2: Manual Configuration**

Copy the environment template and configure your API key:

```bash
cp .env.example .env
```

Edit `.env` and fill in at least one API key:

```bash
# Use Claude (Recommended for GrillRadar)
ANTHROPIC_API_KEY=sk-ant-...

# Or use OpenAI
OPENAI_API_KEY=sk-...

# Or use third-party Anthropic-compatible service (e.g., BigModel in China)
ANTHROPIC_AUTH_TOKEN=your_token_here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
```

**For detailed configuration instructions**, see [CONFIGURATION.md](./CONFIGURATION.md)

### 4. Prepare Configuration File

Create `config.json`:

```json
{
  "mode": "job",
  "target_desc": "ByteDance - Backend Engineer (Campus Recruitment)",
  "domain": "backend",
  "level": "junior"
}
```

**Field Descriptions:**
- `mode`: Mode - `job` (job hunting), `grad` (academic), `mixed` (dual perspective)
- `target_desc`: Detailed description of target position or direction
- `domain`: Domain (optional), e.g., `backend`, `llm_application`, `cv_segmentation`
- `level`: Candidate level (optional), e.g., `intern`, `junior`, `senior`, `master`, `phd`
- `enable_external_info`: Enable external information sources (optional, default false)
- `target_company`: Target company name (optional, for external info retrieval)

### 5. Prepare Your Resume

**Supported formats:** `.pdf`, `.docx`, `.txt`, `.md`

Create `resume.txt` (or use your existing resume file):

```
Name: Zhang San
Education: XX University - Computer Science - Bachelor's Degree

Project Experience:
1. Distributed Web Crawler System
   - Developed in Python, based on Redis and RabbitMQ
   - Implemented deduplication and fault tolerance
   - Daily crawl volume: 1 million records

2. Microservice Backend System
   - Developed RESTful API in Go
   - Integrated with MySQL and Redis
   ...
```

### 6. Generate Report

```bash
# Using text resume
python cli.py --config config.json --resume resume.txt --output report.md

# Using PDF resume
python cli.py --config config.json --resume resume.pdf --output report.md

# Using Word resume
python cli.py --config config.json --resume resume.docx --output report.md
```

The report will be saved as `report.md` and can be opened directly in any Markdown editor.

---

## 📄 Resume Format Support

GrillRadar supports multiple resume formats for maximum flexibility:

| Format | Extension | Description | Features |
|--------|-----------|-------------|----------|
| **PDF** | `.pdf` | Portable Document Format | ✅ Preserves formatting<br>✅ Multi-page support<br>✅ Table extraction |
| **Word** | `.docx` | Microsoft Word Document | ✅ Paragraphs and tables<br>✅ Rich text support |
| **Text** | `.txt` | Plain Text | ✅ Simple and reliable<br>✅ Multiple encodings (UTF-8, GBK, etc.) |
| **Markdown** | `.md` | Markdown Format | ✅ Structured content<br>✅ Easy to edit |

### Using Different Formats

**CLI:**
```bash
# PDF
python cli.py --config config.json --resume resume.pdf --output report.md

# Word
python cli.py --config config.json --resume resume.docx --output report.md

# Text (supports UTF-8, GBK, GB2312, etc.)
python cli.py --config config.json --resume resume.txt --output report.md

# Markdown
python cli.py --config config.json --resume resume.md --output report.md
```

**Web API:**
```bash
# Upload file endpoint
curl -X POST "http://localhost:8000/api/generate-report-upload" \
  -F "mode=job" \
  -F "target_desc=Backend Engineer" \
  -F "domain=backend" \
  -F "resume_file=@resume.pdf"
```

### Encoding Support

For text files, GrillRadar automatically detects encoding:
- UTF-8 (default and recommended)
- GBK, GB2312 (common in China)
- ISO-8859-1, and other encodings

**Best Practice:** Use UTF-8 encoding for best compatibility.

---

## ⚙️ Configuration Methods

GrillRadar provides **5 flexible configuration methods** to suit different user needs:

### 1. 🎨 Interactive Configuration Wizard (Easiest)

```bash
# Python wizard - Recommended for all users
python setup_config.py

# Features:
# ✅ Colored terminal output with emojis
# ✅ Step-by-step guidance
# ✅ Auto-validation of API keys
# ✅ Support for official and third-party services
# ✅ Built-in testing: python setup_config.py --test
```

### 2. 📝 Bash Configuration Script (Linux/macOS)

```bash
bash setup_config.sh

# Features:
# ✅ Menu-driven interface
# ✅ Quick template selection
# ✅ Editor integration
```

### 3. 📋 Template Files

```bash
# Basic template
cp .env.example .env

# Detailed template with annotations
cp .env.example.detailed .env
```

### 4. 🔧 Environment Variables (Production)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export DEFAULT_LLM_PROVIDER="anthropic"
python cli.py ...
```

### 5. ✏️ Direct Editing

Edit `.env` file directly with comprehensive documentation:

```bash
# See CONFIGURATION.md for detailed explanations
# See .env.example.detailed for annotated template
```

**For complete configuration guide**, see [CONFIGURATION.md](./CONFIGURATION.md)

**For quick 5-minute setup**, see [docs/QUICK_START.md](./docs/QUICK_START.md)

---

## 🔧 API Compatibility

GrillRadar supports multiple LLM providers with seamless switching:

### Supported Providers

| Provider | Type | Context Window | Best For | Cost |
|----------|------|----------------|----------|------|
| **Anthropic Claude** (Official) | Direct | 200K tokens | Complex analysis, long resumes | $ |
| **OpenAI GPT** | Direct | 128K tokens | Standard text generation | $-$$ |
| **BigModel** (智谱AI) | Third-party | 200K tokens | Users in China | $ |
| **Custom Endpoint** | Third-party | Varies | Enterprise deployments | Varies |

### Provider Configuration

**Anthropic (Official) - Recommended:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-sonnet-4
```

**OpenAI:**
```bash
OPENAI_API_KEY=sk-your-key-here
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
```

**BigModel (Third-party Anthropic-compatible):**
```bash
ANTHROPIC_AUTH_TOKEN=your-token-here
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
DEFAULT_LLM_PROVIDER=anthropic
```

**Custom Endpoint:**
```bash
ANTHROPIC_API_KEY=your-key
ANTHROPIC_BASE_URL=https://your-custom-endpoint.com
```

### API Health Monitoring

**Check API status:**
```bash
curl http://localhost:8000/api/api-health
```

**Validate configuration:**
```bash
curl http://localhost:8000/api/api-validate
```

**Compare providers:**
```bash
curl http://localhost:8000/api/api-compare
```

**For detailed API compatibility guide**, see [CONFIGURATION.md#api-providers](./CONFIGURATION.md#api-providers)

---

## 📖 Usage Examples

### CLI Examples

**Job Hunting Scenario:**
```bash
python cli.py \
  --config examples/job_backend.json \
  --resume examples/resume_backend.pdf \
  --output reports/backend_report.md
```

**Academic Application Scenario:**
```bash
python cli.py \
  --config examples/grad_cv.json \
  --resume examples/resume_cv.docx \
  --output reports/grad_report.md
```

**Dual Perspective Scenario:**
```bash
python cli.py \
  --config examples/mixed.json \
  --resume examples/resume_full.txt \
  --output reports/mixed_report.md \
  --format markdown
```

**With External Information (Company-specific):**
```bash
# config.json with external info enabled
{
  "mode": "job",
  "target_desc": "ByteDance Backend Engineer",
  "domain": "backend",
  "enable_external_info": true,
  "target_company": "ByteDance"
}

python cli.py --config config.json --resume resume.pdf --output report.md
```

### CLI Parameters

```bash
python cli.py [options]

Required:
  --config CONFIG    Configuration file path (JSON format)
  --resume RESUME    Resume file path (supports: .pdf, .docx, .txt, .md)

Optional:
  --output OUTPUT    Output file path (default: report.md)
  --format FORMAT    Output format: markdown | json (default: markdown)
  --provider PROVIDER  LLM provider: anthropic | openai
  --model MODEL      LLM model name
```

### Web Interface

Start the web server:

```bash
# Method 1: Using Python module
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Method 2: Using uvicorn command
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to use the web interface.

**Web Features:**
- ✅ Simple and friendly form interface
- ✅ Real-time report generation
- ✅ Report download (Markdown and HTML formats)
- ✅ File upload support (PDF, Word, TXT, MD)
- ✅ Loading animations during generation
- ✅ Responsive design for mobile access

### API Endpoints

**Generate Report (JSON):**
```bash
curl -X POST "http://localhost:8000/api/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "job",
    "target_desc": "Backend Engineer",
    "domain": "backend",
    "resume_text": "Your resume content here..."
  }'
```

**Generate Report (File Upload):**
```bash
curl -X POST "http://localhost:8000/api/generate-report-upload" \
  -F "mode=job" \
  -F "target_desc=Backend Engineer" \
  -F "domain=backend" \
  -F "resume_file=@resume.pdf"
```

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**List Domains:**
```bash
curl http://localhost:8000/api/domains
```

---

## 🎯 Supported Domains

> **Milestone 3 Enhancement**: Each domain now includes detailed keywords, tech stacks, classic papers, and recommended readings!

### Engineering Domains (7)

| Domain | Description | Key Technologies |
|--------|-------------|------------------|
| `backend` | Backend Development | Distributed systems, microservices, database optimization |
| `frontend` | Frontend Development | React/Vue, TypeScript, frontend engineering |
| `llm_application` | LLM Application Development | RAG, Prompt engineering, Agent development |
| `algorithm` | Algorithm Engineering | Recommendation systems, search ranking, ML |
| `data_engineering` | Data Engineering | Data warehousing, ETL, big data processing |
| `mobile` | Mobile Development | iOS/Android, cross-platform development |
| `cloud_native` | Cloud Native | Kubernetes, DevOps, microservices |

### Research Domains (6)

| Domain | Description | Focus Areas |
|--------|-------------|-------------|
| `cv_segmentation` | Computer Vision - Image Segmentation | Semantic segmentation, instance segmentation |
| `nlp` | Natural Language Processing | Language models, text analysis |
| `multimodal` | Multimodal Learning | Vision-language models, cross-modal learning |
| `cv_detection` | Computer Vision - Object Detection | Detection algorithms, real-time systems |
| `general_ml` | Machine Learning (General) | ML theory, optimization |
| `reinforcement_learning` | Reinforcement Learning | RL algorithms, decision making |

**For detailed domain information**, see [DOMAINS.md](./DOMAINS.md)

**Configuration file:** `app/config/domains.yaml`

### Domain Benefits

When you specify a domain, GrillRadar will:
- ✅ **Inject domain knowledge** - Add domain keywords, tech stacks, classic papers to prompts
- ✅ **Focus question scope** - Generate questions focused on core competencies
- ✅ **Provide professional references** - Include recommended readings in support_notes
- ✅ **Match typical positions** - Adjust question difficulty based on typical job requirements

---

## 📁 Project Structure

```
GrillRadar/
├── app/
│   ├── models/              # Pydantic data models
│   │   ├── user_config.py        # User configuration
│   │   ├── question_item.py      # Question model
│   │   ├── report.py             # Report model
│   │   └── external_info.py      # External info model
│   ├── core/                # Core business logic
│   │   ├── prompt_builder.py     # Prompt construction
│   │   ├── llm_client.py         # LLM client
│   │   └── report_generator.py   # Report generation
│   ├── sources/             # External information sources
│   │   ├── mock_provider.py      # Mock data provider
│   │   └── external_info_service.py  # External info service
│   ├── retrieval/           # Information retrieval
│   │   └── info_aggregator.py    # Info aggregator
│   ├── api/                 # FastAPI routes
│   │   └── report.py             # Report generation API
│   ├── config/              # Configuration files
│   │   ├── domains.yaml          # Domain knowledge (13 domains)
│   │   ├── modes.yaml            # Mode configuration
│   │   └── settings.py           # Settings
│   ├── utils/               # Utility functions
│   │   ├── markdown.py           # Markdown utilities
│   │   ├── domain_helper.py      # Domain management
│   │   ├── document_parser.py    # **NEW** Multi-format parser
│   │   └── api_compatibility.py  # **NEW** Multi-API support
│   └── main.py              # FastAPI app entry
├── frontend/                # Web frontend
│   ├── templates/           # Jinja2 templates
│   │   └── index.html
│   └── static/              # Static assets
│       ├── css/
│       └── js/
├── tests/                   # Tests (238 tests, 94% coverage)
├── examples/                # Example files
├── docs/                    # Documentation
│   ├── QUICK_START.md       # Quick start guide
│   └── ...
├── setup_config.py          # **NEW** Interactive config wizard
├── setup_config.sh          # **NEW** Bash config script
├── cli.py                   # CLI entry point
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .env.example.detailed    # **NEW** Detailed template
├── CONFIGURATION.md         # **NEW** Configuration guide
├── DOMAINS.md               # Domain configuration guide
├── EXTERNAL_INFO.md         # External info guide
└── README.md                # This file
```

---

## 📊 Report Example

Generated reports include the following sections:

1. **Overall Assessment** - Strengths, risks, preparation advice
2. **Candidate Highlights** - Inferred advantages from resume
3. **Key Risk Points** - Weaknesses exposed in resume
4. **Question List** (10-20 questions) - Each question includes:
   - Question content
   - Rationale for asking
   - How to answer (baseline answer structure)
   - Reference materials
   - Practice prompt

---

## 🔧 Configuration Reference

### Environment Variables (.env)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | - | sk-ant-... |
| `ANTHROPIC_AUTH_TOKEN` | Third-party auth token | - | your_token |
| `ANTHROPIC_BASE_URL` | Custom/third-party base URL | - | https://... |
| `OPENAI_API_KEY` | OpenAI API key | - | sk-... |
| `DEFAULT_LLM_PROVIDER` | Default LLM provider | anthropic | anthropic/openai |
| `DEFAULT_MODEL` | Default model | claude-sonnet-4 | claude-sonnet-4 |
| `LLM_TEMPERATURE` | Temperature parameter | 0.7 | 0.0-1.0 |
| `LLM_MAX_TOKENS` | Max token count | 16000 | 1000-200000 |

### Mode Descriptions

#### job Mode (Job Hunting)
- **Suitable for:** Campus recruitment, job hunting, internship interview preparation
- **Focus:** Engineering skills, project depth, position matching, soft skills
- **Role weights:** Tech interviewer 40%, Hiring manager 30%, HR 20%

#### grad Mode (Academic Application)
- **Suitable for:** Master's recommendation, postgraduate interview, PhD application, research positions
- **Focus:** Research literacy, paper reading, experimental design, academic standards
- **Role weights:** Advisor/PI 40%, Academic reviewer 30%, Tech interviewer 15%

#### mixed Mode (Dual Perspective)
- **Suitable for:** Preparing for both job and graduate school, industry research positions
- **Features:** Each question tagged with [Engineering] or [Academic] perspective
- **Report includes:** Dual-track evaluation

---

## 🛠️ Development

### Install Development Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_document_parser.py -v
```

### Code Formatting

```bash
black app/ tests/ cli.py
```

### Current Test Coverage

- **238 tests** passing
- **94% overall coverage**
- Key modules at 95%+ coverage

---

## 📝 Roadmap

- [x] **Milestone 1**: CLI prototype ✅
- [x] **Milestone 2**: Web version (FastAPI + frontend) ✅
- [x] **Milestone 3**: Configuration-driven domain management ✅
  - 13 domains (7 engineering + 6 research)
  - Detailed domain configuration (keywords, tech stacks, papers, readings)
  - Enhanced prompt injection
  - Domain management API and tools
- [x] **Milestone 4**: External information source integration (JD, interviews) ✅
  - Mock data provider (demo mode)
  - JD and interview experience data models
  - Info aggregation and keyword extraction
  - Automatic prompt injection of external info
  - External info query API
- [x] **Milestone 4.5**: Multi-format resume support ✅
  - PDF, Word, Text, Markdown parsers
  - Encoding detection and handling
  - File upload API endpoint
  - Comprehensive testing
- [x] **Milestone 4.6**: Multi-API compatibility ✅
  - Support for Anthropic, OpenAI, third-party services
  - Auto-detection and validation
  - Health checking and monitoring
  - Interactive configuration wizard
- [ ] **Milestone 5**: Multi-agent architecture evolution (BettaFish-style)
- [ ] **Milestone 6**: Multi-round training system

See `Claude.md` for detailed development roadmap.

---

## 🤝 Contributing

Contributions are welcome! Please submit Issues and Pull Requests.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

This project draws inspiration from:
- [TrendRadar](https://github.com/sansan0/TrendRadar) - Configuration-driven information aggregation
- [BettaFish](https://github.com/666ghj/BettaFish) - Multi-agent collaborative architecture

---

## 📮 Contact

- **Project:** https://github.com/lllllllama/GrillRadar
- **Issues:** https://github.com/lllllllama/GrillRadar/issues
- **Discussions:** https://github.com/lllllllama/GrillRadar/discussions

---

## 🌟 Star History

If GrillRadar helps you prepare for interviews, please give us a ⭐ star!

---

**Last Updated:** 2025-11-17 | **Version:** 0.5.0 | **Test Coverage:** 94%
