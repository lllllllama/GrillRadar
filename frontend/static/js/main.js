// GrillRadar Main JavaScript

// State management
let currentReport = null;
let currentMarkdown = null;

// DOM elements
const reportForm = document.getElementById('reportForm');
const loadingIndicator = document.getElementById('loadingIndicator');
const reportContainer = document.getElementById('reportContainer');
const reportContent = document.getElementById('reportContent');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');
const submitBtn = document.getElementById('submitBtn');
const resumeTextarea = document.getElementById('resume_text');
const charCount = document.getElementById('charCount');

// Character counter
if (resumeTextarea && charCount) {
    resumeTextarea.addEventListener('input', () => {
        const count = resumeTextarea.value.length;
        charCount.textContent = count;

        if (count > 10000) {
            charCount.style.color = 'var(--error-color)';
        } else {
            charCount.style.color = 'var(--text-secondary)';
        }
    });
}

// Form submission
if (reportForm) {
    reportForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await generateReport();
    });
}

// Generate report function
async function generateReport() {
    // Get form data
    const formData = new FormData(reportForm);
    const data = {
        mode: formData.get('mode'),
        target_desc: formData.get('target_desc'),
        domain: formData.get('domain') || null,
        resume_text: formData.get('resume_text')
    };

    // Validate
    if (!data.mode || !data.target_desc || !data.resume_text) {
        showError('请填写所有必填项');
        return;
    }

    if (data.resume_text.length < 50) {
        showError('简历内容至少需要50个字符');
        return;
    }

    if (data.resume_text.length > 10000) {
        showError('简历内容不能超过10000个字符');
        return;
    }

    // Show loading
    showLoading();

    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            currentReport = result.report;
            currentMarkdown = result.markdown;
            showReport(result.markdown);
        } else {
            showError(result.error || '报告生成失败，请重试');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('网络错误或服务器异常，请检查网络连接后重试');
    }
}

// Show loading state
function showLoading() {
    reportForm.style.display = 'none';
    reportContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    loadingIndicator.style.display = 'block';

    // Disable submit button
    if (submitBtn) {
        submitBtn.disabled = true;
    }
}

// Show report
function showReport(markdown) {
    loadingIndicator.style.display = 'none';
    reportContainer.style.display = 'block';

    // Convert markdown to HTML
    reportContent.innerHTML = markdownToHtml(markdown);

    // Scroll to report
    reportContainer.scrollIntoView({ behavior: 'smooth' });

    // Re-enable submit button
    if (submitBtn) {
        submitBtn.disabled = false;
    }
}

// Show error
function showError(message) {
    reportForm.style.display = 'none';
    loadingIndicator.style.display = 'none';
    reportContainer.style.display = 'none';
    errorContainer.style.display = 'block';
    errorMessage.textContent = message;

    // Re-enable submit button
    if (submitBtn) {
        submitBtn.disabled = false;
    }
}

// Simple markdown to HTML converter
function markdownToHtml(markdown) {
    let html = markdown;

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Code blocks
    html = html.replace(/```([\s\S]+?)```/g, '<pre><code>$1</code></pre>');

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Lists (unordered)
    html = html.replace(/^\- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Lists (ordered)
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    // Line breaks to paragraphs
    html = html.split('\n\n').map(para => {
        if (!para.match(/^<[h|u|o|p|l]/)) {
            return '<p>' + para + '</p>';
        }
        return para;
    }).join('\n');

    return html;
}

// Download markdown
const downloadMdBtn = document.getElementById('downloadMd');
if (downloadMdBtn) {
    downloadMdBtn.addEventListener('click', () => {
        if (currentMarkdown) {
            downloadFile(currentMarkdown, 'grillradar-report.md', 'text/markdown');
        }
    });
}

// Download HTML
const downloadHtmlBtn = document.getElementById('downloadHtml');
if (downloadHtmlBtn) {
    downloadHtmlBtn.addEventListener('click', () => {
        if (currentMarkdown) {
            const html = generateFullHtml(currentMarkdown);
            downloadFile(html, 'grillradar-report.html', 'text/html');
        }
    });
}

// Generate new report
const generateNewBtn = document.getElementById('generateNew');
if (generateNewBtn) {
    generateNewBtn.addEventListener('click', () => {
        reportContainer.style.display = 'none';
        reportForm.style.display = 'flex';
        reportForm.scrollIntoView({ behavior: 'smooth' });
    });
}

// Try again button
const tryAgainBtn = document.getElementById('tryAgain');
if (tryAgainBtn) {
    tryAgainBtn.addEventListener('click', () => {
        errorContainer.style.display = 'none';
        reportForm.style.display = 'flex';
        reportForm.scrollIntoView({ behavior: 'smooth' });
    });
}

// Download file helper
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Generate full HTML document
function generateFullHtml(markdown) {
    const htmlContent = markdownToHtml(markdown);
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GrillRadar 面试准备报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB",
                         "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 40px;
            line-height: 1.8;
            color: #2b2d42;
            background: #f8f9fa;
        }
        h1 {
            font-size: 2rem;
            border-bottom: 3px solid #ff6b35;
            padding-bottom: 12px;
            margin-bottom: 24px;
        }
        h2 {
            font-size: 1.5rem;
            color: #ff6b35;
            margin-top: 32px;
            margin-bottom: 16px;
        }
        h3 {
            font-size: 1.2rem;
            margin-top: 24px;
            margin-bottom: 12px;
        }
        p {
            margin-bottom: 16px;
        }
        ul, ol {
            margin-left: 24px;
            margin-bottom: 16px;
        }
        li {
            margin-bottom: 8px;
        }
        strong {
            color: #ff6b35;
        }
        code {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            padding: 0;
        }
        .footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    ${htmlContent}
    <div class="footer">
        <p>生成于 ${new Date().toLocaleString('zh-CN')} | GrillRadar v1.0.0 | Powered by Claude AI</p>
    </div>
</body>
</html>`;
}
