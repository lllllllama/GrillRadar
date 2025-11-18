// GrillRadar Frontend JavaScript

let currentReport = null;
let currentMarkdown = null;

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

function displayReport(report, markdown) {
    const reportContent = document.getElementById('reportContent');
    let html = '<div class="report-meta"><div class="meta-item"><div class="meta-label">模式</div><div class="meta-value">' + getModeDisplay(report.mode) + '</div></div><div class="meta-item"><div class="meta-label">目标</div><div class="meta-value">' + escapeHtml(report.target_desc) + '</div></div><div class="meta-item"><div class="meta-label">问题数量</div><div class="meta-value">' + report.questions.length + ' 个</div></div></div>';
    html += '<div class="report-section"><h3>📊 总体评估</h3><div class="detail-content"><p>' + formatText(report.summary) + '</p></div></div>';
    html += '<div class="report-section"><h3>✨ 候选人亮点</h3><div class="detail-content"><p>' + formatText(report.highlights) + '</p></div></div>';
    html += '<div class="report-section"><h3>⚠️ 关键风险点</h3><div class="detail-content"><p>' + formatText(report.risks) + '</p></div></div>';
    html += '<div class="report-section"><h3>🔥 精选问题列表</h3>';
    
    report.questions.forEach(q => {
        html += '<div class="question-card"><div class="question-header"><div class="question-number">' + q.id + '</div><div class="question-tags"><span class="tag role">' + escapeHtml(q.view_role) + '</span><span class="tag">' + escapeHtml(q.tag) + '</span></div></div>';
        html += '<div class="question-text">' + escapeHtml(q.question) + '</div>';
        html += '<div class="question-detail"><div class="detail-label">💡 提问理由</div><div class="detail-content">' + formatText(q.rationale) + '</div></div>';
        html += '<div class="question-detail"><div class="detail-label">📝 答案结构建议</div><div class="detail-content">' + formatText(q.baseline_answer) + '</div></div>';
        html += '<div class="question-detail"><div class="detail-label">📚 支撑材料</div><div class="detail-content">' + formatText(q.support_notes) + '</div></div>';
        html += '<div class="question-detail"><div class="detail-label">🎯 练习提示词</div><div class="highlight-box">' + formatText(q.prompt_template) + '</div></div></div>';
    });
    
    html += '</div>';
    reportContent.innerHTML = html;
}

function getModeDisplay(mode) {
    const modes = {'job': '求职模式 🎯', 'grad': '读研模式 🎓', 'mixed': '混合模式 🔀'};
    return modes[mode] || mode;
}

function formatText(text) {
    return escapeHtml(text).replace(/\n/g, '<br>');
}

function escapeHtml(text) {
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
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function downloadMarkdown() {
    if (!currentMarkdown) return alert('No report available');
    const blob = new Blob([currentMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'grillradar-report-' + Date.now() + '.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadHTML() {
    if (!currentReport) return alert('No report available');
    const reportContent = document.getElementById('reportContent').innerHTML;
    const html = '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>GrillRadar Report</title><style>body{font-family:sans-serif;padding:40px;max-width:1200px;margin:0 auto;background:#f7f9fc}.report-meta{background:white;padding:20px;border-radius:8px;margin-bottom:24px}.question-card{background:white;padding:24px;border-radius:12px;margin-bottom:24px;border-left:4px solid #ff6b6b;box-shadow:0 2px 8px rgba(0,0,0,0.1)}.question-text{font-size:1.2em;font-weight:600;margin-bottom:12px}</style></head><body><h1 style="color:#ff6b6b;text-align:center;margin-bottom:40px">🔥 GrillRadar 面试准备报告</h1>' + reportContent + '</body></html>';
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'grillradar-report-' + Date.now() + '.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
