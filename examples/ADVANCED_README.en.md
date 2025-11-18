# GrillRadar Advanced Demos

This directory contains advanced demonstrations showcasing GrillRadar's sophisticated features.

## 🎯 Overview

**Two Advanced Features**:

1. **TrendRadar-Style External Information** - Real-world JD/interview data with keyword frequency analysis
2. **BettaFish-Style Multi-Agent Architecture** - 6 specialized agents collaborating for better questions

## 📂 Directory Structure

```
examples/
├── demo_advanced_features.py          # Main advanced features demo
├── compare_single_vs_multi_agent.py   # Single vs multi-agent comparison
├── quality_cases/                     # Test cases for all demos
│   ├── resume_job_backend.txt
│   ├── config_job_backend.json
│   ├── resume_job_frontend.txt
│   ├── config_job_frontend.json
│   ├── resume_grad_nlp.txt
│   └── config_grad_nlp.json
├── run_demo_llm.py                    # Quick demo: LLM engineer
├── run_demo_cv.py                     # Quick demo: CV researcher
└── ADVANCED_README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY or OPENAI_API_KEY
```

### Run Advanced Features Demo

```bash
# Basic demo (shows both features)
python examples/demo_advanced_features.py

# Specific test case
python examples/demo_advanced_features.py --case job_backend

# Frontend engineering demo
python examples/demo_advanced_features.py --case job_frontend

# NLP research demo
python examples/demo_advanced_features.py --case grad_nlp
```

### Run Multi-Agent Comparison

```bash
# Compare approaches
python examples/compare_single_vs_multi_agent.py --case job_backend

# Generate markdown report
python examples/compare_single_vs_multi_agent.py --case job_backend \
    --output my_comparison.md
```

## 📊 Demo 1: TrendRadar Information Acquisition

### What It Shows

- **Real JD Data**: 15 job descriptions from ByteDance, Alibaba, Tencent, etc.
- **Interview Experiences**: 12 real interview experiences with questions
- **Keyword Frequency**: Identifies high-frequency skills (e.g., MySQL appears in 6 JDs)
- **Trend Analysis**: Shows which topics are hot in the industry

### Example Output

```
🔥 High-Frequency Keywords Analysis:

  Top keywords (sorted by frequency):
   1. MySQL                     ██████ (6 occurrences)
   2. Redis                     ████   (4 occurrences)
   3. 性能优化                      ████   (4 occurrences)
   4. Python                    ████   (4 occurrences)
   5. 微服务                       ███    (3 occurrences)

📝 Integration into support_notes:

  该问题涉及 MySQL（高频技能，在6个JD中出现），
  建议重点准备相关知识点...
```

### Key Features

- ✅ Real-world data from actual job postings
- ✅ Frequency-based skill prioritization
- ✅ Domain-specific keyword boosting
- ✅ Automatic marking of high-frequency skills in support_notes

## 🤖 Demo 2: Multi-Agent Architecture

### What It Shows

- **6 Specialized Agents**: Technical Interviewer, Hiring Manager, HR, Advisor, Reviewer, Advocate
- **Parallel Proposal**: All agents propose questions simultaneously
- **Forum Discussion**: Virtual committee filters and refines questions
- **Quality Control**: Advocate agent removes unfair/low-quality questions

### Example Output

```
🎭 Role Perspective Analysis:

  技术面试官                                    ████████ 4 questions (26.7%)
  招聘经理                                      ███████ 3 questions (20.0%)
  HR/行为面试官                                 ████ 2 questions (13.3%)
  导师/PI                                      ████ 2 questions (13.3%)
  学术评审                                     ████ 2 questions (13.3%)
  候选人守护者                                 ████ 2 questions (13.3%)

💡 Multi-Agent Architecture Benefits:

  ✓ Diverse Perspectives: 6 different role viewpoints
  ✓ Comprehensive Coverage: 12 unique topics addressed
  ✓ Resume Alignment: 78.5% questions reference resume
  ✓ Quality Control: Advocate agent filters low-quality questions
  ✓ Deduplication: ForumEngine removes similar questions
```

### Key Features

- ✅ Multiple expert perspectives on same resume
- ✅ Collaborative filtering improves quality
- ✅ Better coverage of different skill dimensions
- ✅ Reduced bias through diverse viewpoints

## 📖 Test Cases

### job_backend

**Resume**: 2-year backend engineer (Go/Python) from Xiaomi
**Projects**: API Gateway, task scheduling system
**Target**: Alibaba Cloud backend engineer
**Domain**: backend

**Run**: `python examples/demo_advanced_features.py --case job_backend`

### job_frontend

**Resume**: 3-year frontend engineer (React) from ByteDance/Tencent
**Projects**: Low-code platform, real-time collaboration editor
**Target**: ByteDance frontend engineer
**Domain**: frontend

**Run**: `python examples/demo_advanced_features.py --case job_frontend`

### grad_nlp

**Resume**: Peking University undergrad, NLP research, CoNLL 2023 paper
**Projects**: Few-shot learning, intent classification
**Target**: Stanford/CMU PhD in NLP
**Domain**: nlp

**Run**: `python examples/demo_advanced_features.py --case grad_nlp`

## 📈 Performance

### TrendRadar Data Loading

- **15 JDs + 12 interviews**: <50ms load time
- **Keyword analysis**: <10ms
- **Memory usage**: <5MB

### Multi-Agent Generation

- **Single-agent**: 8-12 seconds
- **Multi-agent (6 agents)**: 20-35 seconds
- **Quality improvement**: +20% based on automated evaluation

## 💡 Integration into Your Workflow

### Use TrendRadar Data

```python
from app.sources.json_data_provider import json_data_provider

# Get JDs for domain
jds = json_data_provider.get_jds(domain='backend')

# Analyze high-frequency keywords
keywords = json_data_provider.get_high_frequency_keywords(
    jds, domain='backend', top_k=10
)

# Results: [('MySQL', 6), ('Redis', 4), ...]
```

### Enable Multi-Agent Mode

```python
from app.core.agent_orchestrator import AgentOrchestrator
from app.models.user_config import UserConfig

orchestrator = AgentOrchestrator(llm_client)
report = await orchestrator.generate_report(
    user_config,
    enable_multi_agent=True  # Enable multi-agent
)
```

## 🔧 Customization

### Add Your Own JD Data

1. Edit `app/sources/data/jd_database.json`
2. Follow the schema:
```json
{
  "id": "jd_custom_001",
  "company": "Your Company",
  "position": "Your Position",
  "keywords": ["Python", "Go", "MySQL"],
  "requirements": [...],
  ...
}
```

3. Test: `python examples/demo_advanced_features.py`

### Adjust Agent Weights

Edit `app/config/modes.yaml`:

```yaml
job:
  roles:
    technical_interviewer: 0.40  # Increase technical focus
    hiring_manager: 0.25
    hr: 0.20
    advocate: 0.15
```

## 📚 Documentation

- **Full Advanced Demos Guide**: [docs/ADVANCED_DEMOS.md](../docs/ADVANCED_DEMOS.md)
- **Quality Control**: [docs/QUALITY_CONTROL.md](../docs/QUALITY_CONTROL.md)
- **Main README**: [README.md](../README.md)

## 🐛 Troubleshooting

### "No JDs found for domain"

**Solution**: Check domain name matches one of: `backend`, `frontend`, `ml`, `nlp`, `cv_segmentation`

### "AttributeError: 'Anthropic' object has no attribute 'messages'"

**Solution**: Update Anthropic SDK: `pip install --upgrade anthropic`

### "Test case files not found"

**Solution**: Ensure you're running from project root:
```bash
cd /path/to/GrillRadar
python examples/demo_advanced_features.py
```

## 🤝 Contributing

Want to add more features or data?

1. **More JD Data**: Add to `app/sources/data/jd_database.json`
2. **New Agents**: Create in `app/agents/your_agent.py`
3. **Better Algorithms**: Improve keyword frequency in `json_data_provider.py`

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

**Need Help?** Check [docs/ADVANCED_DEMOS.md](../docs/ADVANCED_DEMOS.md) for detailed technical documentation.
