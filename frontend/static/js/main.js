// GrillRadar Frontend JavaScript

let currentReport = null;
let currentMarkdown = null;
let currentReportId = null;
let practiceFilter = 'all'; // 'all', 'mastered', 'need_practice'

// Role color mapping
const ROLE_COLORS = {
    '技术面试官': '#3498db',
    'Technical Interviewer': '#3498db',
    '招聘经理': '#e74c3c',
    'Hiring Manager': '#e74c3c',
    'HR': '#9b59b6',
    'HR专员': '#9b59b6',
    'HR Specialist': '#9b59b6',
    '学术导师': '#2ecc71',
    'Academic Advisor': '#2ecc71',
    '学术评审': '#f39c12',
    'Academic Reviewer': '#f39c12',
    '候选人拥护者': '#16a085',
    'Candidate Advocate': '#16a085',
    '默认': '#34495e'
};

document.addEventListener('DOMContentLoaded', function() {
    const reportForm = document.getElementById('reportForm');
    const resumeTextarea = document.getElementById('resume_text');
    const charCount = document.getElementById('charCount');

    // Character counter
    resumeTextarea.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });

    // Form submission
    reportForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await generateReport();
    });

    // Export buttons
    document.getElementById('downloadMd').addEventListener('click', downloadMarkdown);
    document.getElementById('downloadHtml').addEventListener('click', downloadHTML);
    document.getElementById('generateNew').addEventListener('click', resetForm);
    document.getElementById('tryAgain').addEventListener('click', resetForm);
});

async function generateReport() {
    const form = document.getElementById('reportForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const reportContainer = document.getElementById('reportContainer');
    const errorContainer = document.getElementById('errorContainer');

    // Hide everything
    form.style.display = 'none';
    reportContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    loadingIndicator.style.display = 'block';

    // Get form data
    const formData = new FormData(form);
    const data = {
        mode: formData.get('mode'),
        target_desc: formData.get('target_desc'),
        domain: formData.get('domain') || null,
        resume_text: formData.get('resume_text')
    };

    try {
        // Call API
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            currentReport = result.report;
            currentMarkdown = result.markdown;
            // Generate report ID from config hash
            currentReportId = generateReportId(data);
            displayReport(result.report, result.markdown);

            loadingIndicator.style.display = 'none';
            reportContainer.style.display = 'block';
            reportContainer.scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
        loadingIndicator.style.display = 'none';
        errorContainer.style.display = 'block';
    }
}

function generateReportId(config) {
    // Simple hash function for generating report ID
    const str = JSON.stringify(config);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return 'report_' + Math.abs(hash).toString(36);
}

function displayReport(report, markdown) {
    const reportContent = document.getElementById('reportContent');

    let html = '';

    // Report metadata
    html += `<div class="report-meta">
        <div class="meta-item">
            <div class="meta-label">模式</div>
            <div class="meta-value">${getModeDisplay(report.mode)}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">目标</div>
            <div class="meta-value">${escapeHtml(report.target_desc)}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">问题数量</div>
            <div class="meta-value">${report.questions.length} 个</div>
        </div>
    </div>`;

    // Summary section
    html += `<div class="report-section">
        <h3>📊 总体评估</h3>
        <div class="summary-content">${formatText(report.summary)}</div>
    </div>`;

    html += `<div class="report-section">
        <h3>✨ 候选人亮点</h3>
        <div class="summary-content">${formatText(report.highlights)}</div>
    </div>`;

    html += `<div class="report-section">
        <h3>⚠️ 关键风险点</h3>
        <div class="summary-content">${formatText(report.risks)}</div>
    </div>`;

    // Practice mode filter UI
    html += `<div class="report-section">
        <div class="questions-header">
            <h3>🔥 精选问题列表</h3>
            <div class="practice-filters">
                <button class="filter-btn active" data-filter="all" onclick="setPracticeFilter('all')">
                    全部 (${report.questions.length})
                </button>
                <button class="filter-btn" data-filter="need_practice" onclick="setPracticeFilter('need_practice')">
                    ❌ 需要练习 (<span id="needPracticeCount">0</span>)
                </button>
                <button class="filter-btn" data-filter="mastered" onclick="setPracticeFilter('mastered')">
                    ✅ 已掌握 (<span id="masteredCount">0</span>)
                </button>
            </div>
        </div>
        <div id="questionsList" class="questions-list">`;

    // Render questions
    report.questions.forEach(q => {
        html += renderQuestionCard(q, report);
    });

    html += `</div></div>`;

    reportContent.innerHTML = html;

    // Update practice counts
    updatePracticeCounts();

    // Setup event listeners for question cards
    setupQuestionInteractions();
}

function renderQuestionCard(question, report) {
    const practiceState = getPracticeState(currentReportId, question.id);
    const roleColor = getRoleColor(question.view_role);

    let html = `<div class="question-card" data-question-id="${question.id}" data-practice-state="${practiceState}">
        <div class="question-header">
            <div class="question-number">${question.id}</div>
            <div class="question-meta-right">
                <div class="question-tags">
                    <span class="tag role" style="background-color: ${roleColor}">${escapeHtml(question.view_role)}</span>
                    <span class="tag domain">${escapeHtml(question.tag)}</span>
                </div>
                <div class="practice-buttons">
                    <button class="practice-btn ${practiceState === 'mastered' ? 'active' : ''}"
                            data-state="mastered"
                            onclick="togglePracticeState(${question.id}, 'mastered')"
                            title="标记为已掌握">
                        ✅ 已掌握
                    </button>
                    <button class="practice-btn ${practiceState === 'need_practice' ? 'active' : ''}"
                            data-state="need_practice"
                            onclick="togglePracticeState(${question.id}, 'need_practice')"
                            title="标记为需要练习">
                        ❌ 需要练习
                    </button>
                </div>
            </div>
        </div>

        <div class="question-text">${escapeHtml(question.question)}</div>

        <div class="question-details-toggle">
            <button class="toggle-btn" onclick="toggleQuestionDetails(${question.id})">
                <span class="toggle-icon">▼</span>
                <span class="toggle-text">展开详情</span>
            </button>
        </div>

        <div class="question-details" id="details-${question.id}" style="display: none;">
            <div class="question-detail">
                <div class="detail-label">💡 提问理由</div>
                <div class="detail-content">${formatText(question.rationale)}</div>
            </div>

            <div class="question-detail">
                <div class="detail-label">📝 答案结构建议</div>
                <div class="detail-content">${formatText(question.baseline_answer)}</div>
            </div>

            <div class="question-detail">
                <div class="detail-label">📚 支撑材料</div>
                <div class="detail-content">${formatText(question.support_notes)}</div>
            </div>

            <div class="question-detail">
                <div class="detail-label">🎯 练习提示词</div>
                <div class="prompt-box">
                    <div class="prompt-content">${formatText(question.prompt_template)}</div>
                    <button class="copy-prompt-btn" onclick="copyPrompt(${question.id})" title="复制提示词">
                        📋 复制提示词
                    </button>
                </div>
            </div>
        </div>
    </div>`;

    return html;
}

function toggleQuestionDetails(questionId) {
    const details = document.getElementById(`details-${questionId}`);
    const card = details.closest('.question-card');
    const toggleBtn = card.querySelector('.toggle-btn');
    const toggleIcon = toggleBtn.querySelector('.toggle-icon');
    const toggleText = toggleBtn.querySelector('.toggle-text');

    if (details.style.display === 'none') {
        details.style.display = 'block';
        toggleIcon.textContent = '▲';
        toggleText.textContent = '收起详情';
        card.classList.add('expanded');
    } else {
        details.style.display = 'none';
        toggleIcon.textContent = '▼';
        toggleText.textContent = '展开详情';
        card.classList.remove('expanded');
    }
}

function togglePracticeState(questionId, state) {
    const currentState = getPracticeState(currentReportId, questionId);

    // If clicking the same state, clear it
    const newState = currentState === state ? 'none' : state;

    // Save to localStorage
    setPracticeState(currentReportId, questionId, newState);

    // Update UI
    const card = document.querySelector(`.question-card[data-question-id="${questionId}"]`);
    card.dataset.practiceState = newState;

    // Update button states
    const buttons = card.querySelectorAll('.practice-btn');
    buttons.forEach(btn => {
        if (btn.dataset.state === newState) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Update counts
    updatePracticeCounts();

    // Reapply filter
    applyPracticeFilter();
}

function getPracticeState(reportId, questionId) {
    if (!reportId) return 'none';
    const key = `practice_${reportId}_${questionId}`;
    return localStorage.getItem(key) || 'none';
}

function setPracticeState(reportId, questionId, state) {
    if (!reportId) return;
    const key = `practice_${reportId}_${questionId}`;
    if (state === 'none') {
        localStorage.removeItem(key);
    } else {
        localStorage.setItem(key, state);
    }
}

function updatePracticeCounts() {
    if (!currentReport) return;

    let masteredCount = 0;
    let needPracticeCount = 0;

    currentReport.questions.forEach(q => {
        const state = getPracticeState(currentReportId, q.id);
        if (state === 'mastered') masteredCount++;
        if (state === 'need_practice') needPracticeCount++;
    });

    const masteredEl = document.getElementById('masteredCount');
    const needPracticeEl = document.getElementById('needPracticeCount');

    if (masteredEl) masteredEl.textContent = masteredCount;
    if (needPracticeEl) needPracticeEl.textContent = needPracticeCount;
}

function setPracticeFilter(filter) {
    practiceFilter = filter;

    // Update filter button states
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => {
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Apply filter
    applyPracticeFilter();
}

function applyPracticeFilter() {
    const cards = document.querySelectorAll('.question-card');

    cards.forEach(card => {
        const state = card.dataset.practiceState;
        let shouldShow = false;

        if (practiceFilter === 'all') {
            shouldShow = true;
        } else if (practiceFilter === 'mastered' && state === 'mastered') {
            shouldShow = true;
        } else if (practiceFilter === 'need_practice' && state === 'need_practice') {
            shouldShow = true;
        }

        card.style.display = shouldShow ? 'block' : 'none';
    });
}

function copyPrompt(questionId) {
    const question = currentReport.questions.find(q => q.id === questionId);
    if (!question) return;

    const promptText = question.prompt_template;

    // Copy to clipboard
    navigator.clipboard.writeText(promptText).then(() => {
        // Show feedback
        const card = document.querySelector(`.question-card[data-question-id="${questionId}"]`);
        const btn = card.querySelector('.copy-prompt-btn');
        const originalText = btn.textContent;

        btn.textContent = '✅ 已复制！';
        btn.classList.add('copied');

        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('复制失败，请手动复制');
    });
}

function getRoleColor(role) {
    return ROLE_COLORS[role] || ROLE_COLORS['默认'];
}

function setupQuestionInteractions() {
    // All interactions are handled via onclick attributes for simplicity
}

function getModeDisplay(mode) {
    const modes = {
        'job': '求职模式 🎯',
        'grad': '读研模式 🎓',
        'mixed': '混合模式 🔀'
    };
    return modes[mode] || mode;
}

function formatText(text) {
    if (!text) return '';
    return escapeHtml(text).replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
}

function resetForm() {
    document.getElementById('reportForm').style.display = 'block';
    document.getElementById('reportContainer').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'none';
    currentReport = null;
    currentMarkdown = null;
    currentReportId = null;
    practiceFilter = 'all';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function downloadMarkdown() {
    if (!currentMarkdown) {
        alert('No report available');
        return;
    }

    const blob = new Blob([currentMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `grillradar-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadHTML() {
    if (!currentReport) {
        alert('No report available');
        return;
    }

    const reportContent = document.getElementById('reportContent').innerHTML;
    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrillRadar Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; max-width: 1200px; margin: 0 auto; background: #f7f9fc; line-height: 1.6; }
        .report-meta { background: white; padding: 20px; border-radius: 8px; margin-bottom: 24px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
        .report-section { margin-bottom: 36px; }
        .report-section h3 { color: #ff6b6b; font-size: 1.6em; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e1e8ed; }
        .question-card { background: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; border-left: 4px solid #ff6b6b; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); }
        .question-text { font-size: 1.2em; font-weight: 600; margin-bottom: 12px; }
        .question-detail { margin-bottom: 16px; }
        .detail-label { font-weight: 600; color: #ff6b6b; margin-bottom: 6px; }
        .detail-content { padding-left: 16px; }
        .tag { padding: 4px 12px; background: #4ecdc4; color: white; border-radius: 16px; font-size: 0.85em; display: inline-block; margin-right: 8px; }
    </style>
</head>
<body>
    <h1 style="color: #ff6b6b; text-align: center; margin-bottom: 40px">🔥 GrillRadar 面试准备报告</h1>
    ${reportContent}
</body>
</html>`;

    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `grillradar-report-${Date.now()}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
