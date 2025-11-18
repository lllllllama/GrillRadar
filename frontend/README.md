# GrillRadar Web UI

A minimal but useful web interface for GrillRadar with practice mode support.

## Features

### 1. Report Generation Form
- Mode selection (Job / Grad / Mixed)
- Target description input
- Optional domain selection
- Resume text input with character counter
- Real-time validation

### 2. Report Display

**Summary Section:**
- Mode and target information
- Total assessment
- Candidate highlights
- Key risk points

**Question Cards:**
- Clean, card-based layout
- Question number badge
- Colored role tags (Technical / HR / Advisor / Reviewer)
- Domain tags
- Expandable details (toggle)

**Question Details (Expandable):**
- 💡 Rationale - Why this question is asked
- 📝 Baseline Answer - Suggested answer structure
- 📚 Support Notes - Reference materials
- 🎯 Practice Prompt - Copy-to-clipboard prompt template

### 3. Practice Mode ✨

**Local-Only State Management:**
- Mark questions as "✅ Mastered" or "❌ Need practice"
- State persisted in `localStorage` (no backend required)
- Practice state keyed by report ID (generated from config hash)

**Filter UI:**
- Show all questions
- Show only "Need practice" questions
- Show only "Mastered" questions
- Real-time question count updates

**Practice Workflow:**
1. Generate a report
2. Mark questions based on your preparation level
3. Filter to focus on questions needing practice
4. Copy practice prompts to use with ChatGPT/Claude
5. Update practice state as you improve

### 4. Copy Prompt Feature

Each question includes a practice prompt template that can be:
- Copied to clipboard with one click
- Used directly with ChatGPT, Claude, or other LLMs
- Customized with your experience

### 5. Export Options

- **Download Markdown**: Get full report as .md file
- **Download HTML**: Get styled HTML for offline viewing
- **Generate New**: Clear current report and start fresh

## Architecture

### Frontend-Only Practice State

Practice mode is intentionally designed with **no backend state**:
- ✅ All practice state in browser `localStorage`
- ✅ No database required
- ✅ No server-side sessions
- ✅ Works offline after report generation
- ✅ Privacy-friendly (data stays local)

**localStorage Keys:**
```
practice_{reportId}_{questionId} = "mastered" | "need_practice" | null
```

**Report ID Generation:**
- Generated from hash of config (mode + target_desc + domain + resume hash)
- Same inputs = same report ID = persistent practice state
- Different inputs = different report ID = separate practice tracking

### Role Colors

Roles are color-coded for easy visual scanning:
- **Technical Interviewer** (蓝色 #3498db)
- **Hiring Manager** (红色 #e74c3c)
- **HR Specialist** (紫色 #9b59b6)
- **Academic Advisor** (绿色 #2ecc71)
- **Academic Reviewer** (橙色 #f39c12)
- **Candidate Advocate** (青色 #16a085)

## Usage

### Starting the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export ANTHROPIC_API_KEY="your-key-here"

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Accessing the Web UI

Open your browser and navigate to:
```
http://localhost:8000
```

### Generating a Report

1. Select mode (Job / Grad / Mixed)
2. Enter target description
3. Optionally select domain
4. Paste resume content (50-10000 characters)
5. Click "🔥 生成报告"
6. Wait 15-30 seconds for AI committee discussion

### Using Practice Mode

1. **After report generation:**
   - Each question card has two practice buttons
   - Click "✅ 已掌握" when you've mastered a question
   - Click "❌ 需要练习" for questions needing work
   - Click again to clear the state

2. **Filtering questions:**
   - Use filter buttons at top of question list
   - "全部" shows all questions
   - "❌ 需要练习" shows only questions marked for practice
   - "✅ 已掌握" shows only mastered questions

3. **Practice workflow:**
   - Expand question details
   - Copy practice prompt
   - Paste into ChatGPT/Claude
   - Practice answering
   - Mark as mastered when confident

## Technical Details

### Files

```
frontend/
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── css/
│   │   └── main.css        # All styles
│   └── js/
│       └── main.js         # All JavaScript logic
└── README.md               # This file
```

### JavaScript Functions

**Report Generation:**
- `generateReport()` - Call API and display report
- `displayReport()` - Render report HTML
- `renderQuestionCard()` - Create question card HTML

**Practice Mode:**
- `togglePracticeState()` - Toggle mastered/need practice
- `getPracticeState()` - Get state from localStorage
- `setPracticeState()` - Save state to localStorage
- `updatePracticeCounts()` - Update filter counts
- `applyPracticeFilter()` - Show/hide questions based on filter

**UI Interactions:**
- `toggleQuestionDetails()` - Expand/collapse question details
- `copyPrompt()` - Copy practice prompt to clipboard
- `setPracticeFilter()` - Change active filter

### CSS Classes

**Question Cards:**
- `.question-card` - Main card container
- `.question-card.expanded` - Expanded state
- `.question-header` - Top section with number, tags, buttons
- `.question-text` - Main question text
- `.question-details` - Expandable details section

**Practice Mode:**
- `.practice-btn` - Practice state button
- `.practice-btn.active` - Active state (green for mastered, yellow for need practice)
- `.filter-btn` - Filter button
- `.filter-btn.active` - Active filter

**Role Tags:**
- `.tag.role` - Role tag with dynamic color
- `.tag.domain` - Domain tag (gray)

## Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (responsive design)

**Required Browser Features:**
- localStorage API
- Clipboard API (for copy prompt)
- Fetch API
- ES6+ JavaScript

## Design Principles

1. **Minimal but Useful**: Essential features only, no bloat
2. **Local-First**: Practice state stays in browser
3. **No Backend State**: Backend only generates reports
4. **Privacy-Friendly**: No tracking, no analytics
5. **Accessible**: Clear visual hierarchy, semantic HTML
6. **Responsive**: Works on desktop and mobile

## Future Enhancements

Potential improvements (not currently implemented):
- Export practice state as JSON
- Import practice state from JSON
- Practice session timer
- Progress statistics dashboard
- Question difficulty voting
- Personal notes per question
- Spaced repetition scheduling

## Limitations

1. **Practice state is per-browser**: Clearing localStorage loses practice state
2. **No cloud sync**: Practice state doesn't sync across devices
3. **Report ID collisions**: Different resumes with same config = same ID (rare)
4. **No practice history**: Only current state, no historical tracking

## Support

For issues or questions:
- Check API logs: `tail -f logs/app.log`
- Check browser console for JS errors
- Verify API endpoint: `curl http://localhost:8000/api/health`
- Verify static files: `curl http://localhost:8000/static/js/main.js`
