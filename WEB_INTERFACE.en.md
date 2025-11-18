# GrillRadar Web Interface

## 🌐 Overview

GrillRadar now includes a **polished web interface** that showcases the multi-agent intelligence and TrendRadar-style external data integration in action.

### Key Features

✅ **Beautiful UI**: Modern, responsive design with smooth animations
✅ **Real-Time Generation**: Watch the AI committee discuss and generate questions
✅ **External Data Integration**: Automatically pulls from real JD/interview database
✅ **Multi-Agent Intelligence**: 6 specialized agents collaborate on every report
✅ **Export Options**: Download reports as Markdown or HTML
✅ **Personality & Judgment**: See the "personality" through diverse role perspectives

---

## 🚀 Quick Start

### 1. Start the Web Server

```bash
# Option 1: Use the convenience script
./run_web.sh

# Option 2: Manual start
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open in Browser

```
http://localhost:8000
```

### 3. Generate Your First Report

1. **Select Mode**: Choose job/grad/mixed
2. **Enter Target**: E.g., "字节跳动后端开发工程师"
3. **Choose Domain** (optional): E.g., "backend"
4. **Paste Resume**: Your resume text (50+ characters)
5. **Click "🔥 生成报告"**

---

## 🎯 What You'll See

### Stage 1: Loading (15-30 seconds)

```
AI虚拟委员会正在讨论中...
预计需要 15-30 秒
```

Behind the scenes:
- 6 agents proposing questions in parallel
- TrendRadar analyzing 15 JDs + 12 interview experiences
- Keyword frequency analysis (e.g., MySQL appears 6 times)
- ForumEngine deduplicating and filtering
- Quality control by Advocate agent

### Stage 2: Report Display

Beautiful, interactive report with:

**📊 Meta Information**
- Mode, target, question count, generation time

**📊 Overall Assessment**
- AI committee's comprehensive evaluation
- Shows multi-agent collaboration results

**✨ Candidate Highlights**
- Strengths identified from resume

**⚠️  Key Risks**
- Potential weaknesses and preparation suggestions

**🔥 Question List** (10-20 questions)

Each question card shows:
- **Question Number**: Visual identifier
- **Role Tags**: Which agent asked (技术面试官, HR, 导师/PI, etc.)
- **Topic Tag**: Subject area
- **Question Text**: The actual question
- **💡 Rationale**: Why this question matters (shows "personality")
- **📝 Answer Structure**: How to structure your response
- **📚 Support Notes**: Learning resources (**with high-frequency skill markers**)
- **🎯 Practice Prompt**: Ready-to-use prompt for AI practice

### Stage 3: Export

Click to download:
- **Markdown**: For version control, sharing
- **HTML**: Self-contained, styled report

---

## 🔍 TrendRadar Integration in Action

When you generate a report, you'll see **real-world intelligence** integrated:

### Example: Backend Engineer Report

**External Data Retrieved:**
- 8 JDs from 字节跳动, 阿里巴巴, 腾讯, etc.
- 10 interview experiences with real questions

**Keyword Frequency Analysis:**
```
MySQL ██████ (6 occurrences)
Redis ████   (4 occurrences)
性能优化  ████   (4 occurrences)
```

**In support_notes, you'll see:**
```
📚 支撑材料:
该问题涉及 MySQL（高频技能，在6个JD中出现），建议重点准备：
1. MySQL索引原理（B+树）
2. 事务隔离级别
3. 主从复制和读写分离
参考: 《高性能MySQL》第三版
```

**This is TrendRadar-style intelligence!** The system knows MySQL is hot in the market and prioritizes it.

---

## 🤖 Multi-Agent Intelligence

### The 6 Agents

When you view a report, notice the **role tags** on questions:

| Agent | Role Tag | Focus |
|-------|----------|-------|
| **Technical Interviewer** | 技术面试官 | CS fundamentals, coding |
| **Hiring Manager** | 招聘经理 | Project depth, role fit |
| **HR Agent** | HR/行为面试官 | Soft skills, culture |
| **Advisor/PI** | 导师/PI | Research potential (grad mode) |
| **Academic Reviewer** | 学术评审 | Methodology (grad mode) |
| **Advocate** | 候选人守护者 | Quality control |

### Personality & Judgment

You'll see **personality** in:

1. **Diverse Perspectives**: Questions from 6 different viewpoints
2. **Contextual Rationales**: Each explains WHY it matters
3. **Balanced Coverage**: Not just technical, but soft skills too
4. **Resume-Specific**: References your actual experience
5. **Quality Filtering**: No generic or unfair questions

### Example: Multi-Agent Collaboration

**Question 1** (技术面试官):
> 你在简历中提到使用Go开发API网关，请详细讲一下你是如何实现限流、熔断和负载均衡的？

**Rationale**:
> 技术面试官关注系统设计能力。简历中提到的API网关是核心项目，需要深入考察候选人对分布式系统关键技术的理解...

**Question 2** (HR/行为面试官):
> 在小米实习期间，你如何与团队协作完成用户认证服务的重构？遇到过什么挑战？

**Rationale**:
> HR关注团队协作和沟通能力。从简历看候选人有实习经验，需要了解其在真实团队环境中的表现...

This shows **judgment**: different agents care about different things, giving you comprehensive preparation.

---

## 📊 Technical Architecture

### Frontend Stack

- **HTML5**: Semantic, accessible markup
- **CSS3**: Modern gradients, animations, responsive grid
- **Vanilla JS**: No frameworks, fast and lightweight
- **Fetch API**: Async communication with backend

### Backend Stack

- **FastAPI**: High-performance async Python framework
- **Pydantic**: Data validation and serialization
- **JSON Data Provider**: Real JD/interview database
- **Enhanced Info Service**: Keyword frequency analysis

### Data Flow

```
User Input (Resume)
      ↓
FastAPI Endpoint
      ↓
Enhanced Info Service → JSON Database (15 JDs, 12 interviews)
      ↓                         ↓
Keyword Frequency Analysis → High-freq keywords identified
      ↓
Prompt Builder → Injects external data + keyword intelligence
      ↓
LLM (Claude/OpenAI) → Generates questions
      ↓
Multi-Agent Simulation → 6 agents propose & discuss
      ↓
ForumEngine → Deduplicates & filters
      ↓
Report Assembly → Marks high-freq skills in support_notes
      ↓
Frontend Display → Beautiful, exportable report
```

---

## 🎨 Customization

### Change Port

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### Modify Domains

Edit `app/config/domains.yaml` to add/remove domains. Changes auto-reload with `--reload` flag.

### Add More External Data

Edit `app/sources/data/jd_database.json` or `interview_database.json`:

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

Server will automatically load new data on restart.

### Customize Styling

Edit `frontend/static/css/main.css`. All CSS variables are in `:root`:

```css
:root {
    --primary-color: #ff6b6b;  /* Change to your brand color */
    --secondary-color: #4ecdc4;
    ...
}
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Then restart
./run_web.sh
```

### API Key Not Set

```
Error: "API key not found"
```

**Solution**: Edit `.env` and add:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
# or
OPENAI_API_KEY=sk-your-key-here
```

### Slow Generation

If generation takes >60 seconds:
- Check API quota/rate limits
- Check network connection
- Try a different LLM provider

### No Questions Generated

```
Error: "问题数量不足：只有0个"
```

**Causes**:
- Resume too short (<50 chars)
- LLM API error
- Invalid configuration

**Solution**:
- Check resume length
- Check API logs in terminal
- Verify `.env` configuration

---

## 📝 Export Formats

### Markdown Export

Click "下载 Markdown" to get:

```markdown
# GrillRadar 面试准备报告

## 📊 报告信息
- **模式**: 求职模式
- **目标**: 字节跳动后端开发工程师
- **生成时间**: 2025-11-17 18:00:00

## 总体评估
候选人具有扎实的后端开发基础...

## 问题 1
**角色**: 技术面试官
**标签**: 系统设计

### 问题
你在简历中提到...

### 提问理由
...
```

### HTML Export

Click "下载 HTML" to get self-contained file with embedded styles. Can be:
- Opened directly in browser
- Shared via email
- Printed as PDF (browser print dialog)

---

## 🔒 Security & Privacy

### Data Handling

- **Resume data**: Sent to LLM API, not stored on server
- **Generated reports**: Only in browser memory, cleared on refresh
- **No tracking**: No analytics, no cookies
- **Local first**: All data processing happens on your server

### API Keys

- Stored in `.env` (git-ignored)
- Never sent to browser
- Only used for server-side LLM calls

### Production Deployment

For production use:
1. Enable HTTPS
2. Add authentication
3. Rate limiting
4. Input sanitization (already basic validation)

---

## 🚀 Performance

### Typical Metrics

| Metric | Value |
|--------|-------|
| **Page Load** | <1s |
| **Report Generation** | 15-30s (depends on LLM) |
| **Report Display** | <500ms |
| **Export** | <100ms |

### Optimization Tips

1. **Use Haiku model** for faster generation (at cost of some quality)
2. **Enable caching** in LLM client
3. **Reduce question count** (10 instead of 20)

---

## 📚 API Endpoints

For developers who want to integrate programmatically:

### POST /api/generate-report

```bash
curl -X POST http://localhost:8000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "job",
    "target_desc": "字节跳动后端开发工程师",
    "domain": "backend",
    "resume_text": "your resume here..."
  }'
```

**Response**:
```json
{
  "success": true,
  "report": { /* Report object */ },
  "markdown": "# GrillRadar Report\n\n..."
}
```

### GET /api/domains

```bash
curl http://localhost:8000/api/domains
```

**Response**: List of available domains (engineering + research)

### GET /health

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "ok",
  "app": "GrillRadar",
  "version": "1.0.0"
}
```

---

## 🎓 Learning Resources

To understand how it works:

1. **Architecture**: Read [docs/ADVANCED_DEMOS.md](./docs/ADVANCED_DEMOS.md)
2. **Quality Control**: Read [docs/QUALITY_CONTROL.md](./docs/QUALITY_CONTROL.md)
3. **Source Code**:
   - Frontend: `frontend/static/js/main.js`
   - Backend: `app/api/report.py`
   - External Data: `app/sources/json_data_provider.py`

---

## 🤝 Contributing

Want to improve the web interface?

**Ideas:**
- Add real-time progress tracking
- Support file upload for resume
- Add report history/comparison
- Theme customization UI
- Multi-language support

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

**🔥 Enjoy using GrillRadar!**

For issues or questions, open an issue on [GitHub](https://github.com/lllllllama/GrillRadar).
