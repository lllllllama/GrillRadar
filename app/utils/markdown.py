"""Markdown格式转换工具"""
from datetime import datetime
from app.models.report import Report


def report_to_markdown(report: Report) -> str:
    """
    将Report对象转换为Markdown格式

    Args:
        report: Report对象

    Returns:
        Markdown格式的字符串
    """
    md = f"""# GrillRadar 面试准备报告

**目标岗位：** {report.target_desc}

**生成时间：** {report.meta.generated_at}

**模式：** {report.mode}

**问题数量：** {report.meta.num_questions}

---

## 📊 总体评估

{report.summary}

---

## ⭐ 候选人亮点

{report.highlights}

---

## ⚠️ 关键风险点

{report.risks}

---

## 📝 问题清单

"""

    # 添加每个问题
    for question in report.questions:
        md += f"""
### Q{question.id}. [{question.tag}] {question.view_role}

**问题：**

{question.question}

**为什么问这个问题：**

{question.rationale}

**如何回答：**

{question.baseline_answer}

**参考资料：**

{question.support_notes}

**练习提示词：**

```
{question.prompt_template}
```

---

"""

    # 添加页脚
    md += f"""
## 📌 使用说明

1. **准备答案**：针对每个问题，结合你的真实经历准备答案
2. **使用练习提示词**：将"练习提示词"复制到ChatGPT/Claude中，填入你的真实经历，进行深度练习
3. **补充薄弱点**：重点关注"关键风险点"部分，针对性补充知识和项目经验
4. **模拟面试**：找朋友或使用AI工具进行模拟面试，反复练习

---

**报告生成信息：**
- 生成时间：{report.meta.generated_at}
- 使用模型：{report.meta.model}
- 配置版本：{report.meta.config_version}

*本报告由 GrillRadar 自动生成*
"""

    return md
