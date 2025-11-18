# Research Domain Configuration Guide

This document describes how GrillRadar handles research-oriented (grad/PhD) interview preparation, with special support for Chinese academic contexts.

## Overview

GrillRadar provides structured configuration for research domains and Chinese graduate school interviews to generate academically grounded questions without fabricating specific papers or authors.

### Key Principles

1. **No Paper Fabrication**: Reference conferences by name only (e.g., "read recent CVPR papers")
2. **Search Query Guidance**: Provide legitimate search queries (e.g., "search for 'image segmentation survey'")
3. **General Methodologies**: Focus on common methods and baselines, not specific implementations
4. **Cultural Context**: Incorporate Chinese academic culture for Chinese-language interviews

## Configuration Files

### 1. Research Domains (`config/research_domains.yaml`)

Structured knowledge base for research areas, including:
- **Conferences**: Top-tier conferences and journals (by acronym only)
- **Core Topics**: Key research subfields
- **Recommended Queries**: Search phrases for literature review
- **Common Methods**: Typical approaches and baselines
- **Evaluation Metrics**: Standard performance measures

#### Currently Supported Domains

| Domain Key | Display Name | Category |
|------------|--------------|----------|
| `cv_segmentation` | 计算机视觉 - 图像分割 | research |
| `nlp` | 自然语言处理 | research |
| `llm_application` | 大语言模型应用 | engineering_research |
| `multimodal` | 多模态学习 | research |
| `general_ml` | 机器学习（通用） | research |
| `graph_learning` | 图学习 | research |
| `reinforcement_learning` | 强化学习 | research |
| `robotics` | 机器人学 | research |
| `generative_ai` | 生成式AI | research |

#### Example Domain Entry

```yaml
cv_segmentation:
  display_name: "计算机视觉 - 图像分割"
  display_name_en: "Computer Vision - Image Segmentation"
  category: "research"

  conferences:
    tier1:
      - CVPR
      - ICCV
      - ECCV
    medical:
      - MICCAI
      - IPMI

  core_topics:
    - Semantic segmentation
    - Instance segmentation
    - Medical image segmentation
    - Transformer-based segmentation

  recommended_queries:
    - "image segmentation survey"
    - "semantic segmentation review"
    - "Transformer segmentation"

  common_methods:
    - U-Net and variants
    - DeepLab series
    - Mask R-CNN
    - SegFormer

  typical_baselines:
    - FCN
    - U-Net
    - DeepLabv3+
```

### 2. China Grad School (`config/china_grad.yaml`)

Chinese-specific interview context, including:
- **Interview Structure**: Typical components (self-intro, fundamentals, research discussion, etc.)
- **Evaluation Dimensions**: Core assessment criteria (fundamentals, research potential, commitment, etc.)
- **Killer Question Patterns**: High-level patterns (NO specific real questions)
- **Academic Culture**: Important cultural contexts
- **Preparation Checklist**: What candidates should prepare

#### Key Sections

**Interview Structure:**
- 自我介绍 (Self-Introduction)
- 基础课程考察 (Core Course Questions)
- 科研/项目讨论 (Research/Project Discussion)
- 未来规划 (Future Plans)
- 英语能力考察 (English Proficiency)

**Evaluation Dimensions:**
- 专业基础 (Fundamental Knowledge)
- 科研潜力 (Research Potential)
- 长期投入意愿 (Long-term Commitment)
- 与实验室契合度 (Lab Fit)
- 综合素质 (Overall Quality)

**Killer Question Patterns:**
- 深度追问项目细节 (Deep Dive into Project Details)
- 理论基础考察 (Theoretical Foundation)
- 研究方法论 (Research Methodology)
- 文献阅读深度 (Literature Understanding)
- 开放性研究问题 (Open Research Questions)

## How It Works

### When Research Guidance is Injected

Research-specific guidance is automatically injected when:
1. `mode` is `grad` or `mixed`, AND
2. Either:
   - A research domain is specified (e.g., `domain=cv_segmentation`)
   - Language is Chinese (`language=zh`)

### Prompt Building Flow

```
User Config (mode=grad, domain=cv_segmentation, language=zh)
    ↓
PromptBuilder.build()
    ↓
_get_research_guidance()
    ├─ _format_research_domain() → Injects conference names, topics, queries
    └─ _format_china_grad_context() → Injects interview structure, patterns
    ↓
Fills {research_guidance} placeholder in prompt template
    ↓
Complete system prompt sent to LLM
```

### What Gets Injected

**For Research Domains:**
```markdown
### 研究领域知识库: 计算机视觉 - 图像分割

**相关顶级会议/期刊:**
- tier1: CVPR, ICCV, ECCV
- medical: MICCAI, IPMI

**核心研究主题:**
Semantic segmentation, Instance segmentation, Medical image segmentation...

**推荐文献检索关键词:**
- "image segmentation survey"
- "semantic segmentation review"

**重要提示:**
- 在support_notes中，应引导学生阅读相关顶会论文（仅提及会议名，不编造具体论文标题/作者）
- 避免编造不存在的论文、作者或具体实验结果
```

**For China Grad Context:**
```markdown
### 中国研究生面试情境知识

**典型面试环节:**
- 自我介绍: 简要介绍教育背景、科研经历、申请动机
- 科研/项目讨论: 深入讨论简历中的科研项目

**核心评估维度:**
- 专业基础: 数学、编程、专业课程基础是否扎实
- 科研潜力: 是否具备独立科研能力和创新思维

**面试问题生成指导:**
- 问题应符合中国研究生面试的评估维度和提问风格
- 考虑导师制、组会文化、科研产出压力等中国特色学术环境
```

## Adding New Research Domains

### Step-by-Step Guide

1. **Open `config/research_domains.yaml`**

2. **Copy an existing domain template** (e.g., `cv_segmentation`)

3. **Fill in the required fields:**
   - `display_name`: Chinese name
   - `display_name_en`: English name
   - `category`: "research" or "engineering_research"
   - `conferences`: List of relevant conferences/journals
   - `core_topics`: 5-15 key topics
   - `recommended_queries`: Search queries for students
   - `common_methods` (optional): Typical approaches
   - `typical_baselines` (optional): Standard baselines

4. **Example - Adding "AI Safety" domain:**

```yaml
ai_safety:
  display_name: "AI安全"
  display_name_en: "AI Safety"
  category: "research"

  conferences:
    ml:
      - NeurIPS
      - ICML
      - ICLR
    safety:
      - SafeAI

  core_topics:
    - Adversarial Robustness
    - Model Interpretability
    - Alignment
    - Fairness and Bias
    - Privacy-Preserving ML

  recommended_queries:
    - "adversarial robustness survey"
    - "AI alignment research"
    - "model interpretability methods"

  common_methods:
    - Adversarial Training
    - LIME / SHAP
    - Differential Privacy
    - RLHF
```

5. **Validate your YAML** (use online YAML validator or `python -c "import yaml; yaml.safe_load(open('config/research_domains.yaml'))"`)

6. **Test with a grad-mode config:**

```json
{
  "mode": "grad",
  "target_desc": "清华大学AI安全方向博士",
  "domain": "ai_safety",
  "language": "zh"
}
```

### Field Guidelines

| Field | Required | Guidelines |
|-------|----------|------------|
| `display_name` | Yes | Use standard Chinese terminology |
| `display_name_en` | Yes | Use standard English terminology |
| `category` | Yes | "research" for pure research, "engineering_research" for applied |
| `conferences` | Recommended | Use official acronyms (CVPR, NeurIPS, etc.) |
| `core_topics` | Recommended | 5-15 items, focus on subfields |
| `recommended_queries` | Recommended | Search phrases students can actually use |
| `common_methods` | Optional | Well-known approaches |
| `typical_baselines` | Optional | Standard comparison methods |
| `evaluation_metrics` | Optional | Standard metrics (e.g., Dice, BLEU) |

### Important Constraints

**DO:**
- ✅ Use official conference names (CVPR, NeurIPS, etc.)
- ✅ List general methodologies (U-Net, Transformer, etc.)
- ✅ Provide verifiable search queries
- ✅ Focus on publicly known information

**DON'T:**
- ❌ Fabricate paper titles or authors
- ❌ Claim specific experimental results
- ❌ Make up conference names
- ❌ Include proprietary or confidential information

## Usage Examples

### Example 1: CV Segmentation PhD Application

**Config:**
```json
{
  "mode": "grad",
  "target_desc": "清华大学计算机系 医疗影像分割方向 博士申请",
  "domain": "cv_segmentation",
  "language": "zh"
}
```

**Generated Question Example:**
```markdown
**问题**: 你提到在医疗影像分割项目中使用了Transformer架构，请详细解释你的设计思路，以及相比于U-Net的优势和劣势是什么？

**支撑材料**:
- **会议参考**: 建议阅读近期MICCAI和CVPR上关于Transformer-based segmentation的论文
- **文献检索**: 搜索"medical image segmentation Transformer"、"U-Net variants comparison"
- **经典方法**: 熟悉U-Net、Attention U-Net、TransUNet等方法的核心思想
- **评估指标**: 理解Dice Score、IoU、Hausdorff Distance等医疗影像分割常用指标
```

### Example 2: NLP Master's Interview (Chinese)

**Config:**
```json
{
  "mode": "grad",
  "target_desc": "北京大学NLP方向硕士面试",
  "domain": "nlp",
  "language": "zh"
}
```

**Generated Question Example:**
```markdown
**问题**: 你在简历中提到做过命名实体识别(NER)任务，请说明你是如何处理嵌套实体和歧义问题的？

**支撑材料**:
- **会议参考**: 阅读ACL、EMNLP近期关于NER的工作，了解当前主流方法
- **文献检索**: 搜索"nested NER survey"、"entity disambiguation methods"
- **基础准备**: 复习序列标注基础（BiLSTM-CRF、BERT-based NER等）
- **面试建议**:
  - 准备讨论你的实验设置和结果分析
  - 了解中国NLP社区的研究热点
  - 展示对相关工作的系统了解（不要只是堆砌论文名）
```

### Example 3: Mixed Mode (Job + Grad)

**Config:**
```json
{
  "mode": "mixed",
  "target_desc": "字节跳动大模型应用工程师（在职） + 清华NLP博士（备选）",
  "domain": "llm_application",
  "language": "zh"
}
```

**Result:**
- Engineering questions with practical focus (RAG, prompt engineering, etc.)
- Academic questions with research depth (LLM alignment, evaluation, etc.)
- Both perspectives informed by LLM application domain knowledge

## Testing Your Configurations

### Manual Testing

```bash
# 1. Generate a report with research domain
python cli.py --config examples/grad_cv_segmentation/config.json \
              --resume examples/grad_cv_segmentation/resume.md \
              --output test_report.md

# 2. Check support_notes for:
#    - Conference names (not specific papers)
#    - Search queries
#    - Method names
grep "CVPR\|ICCV\|search for" test_report.md
```

### Automated Testing

```bash
# Run evaluation toolkit
python scripts/eval_report.py --case grad_cv_segmentation --output grad_report.json

# Check for hallucination indicators
python -c "
import json
with open('grad_report.json') as f:
    report = json.load(f)
for q in report['questions']:
    notes = q.get('support_notes', '')
    # Check for specific paper patterns (should NOT appear)
    if 'et al.' in notes or '20' in notes[:50]:
        print(f'WARNING: Possible paper citation in Q{q[\"id\"]}')
"
```

## Troubleshooting

### Issue: Research guidance not appearing

**Check:**
1. Mode is `grad` or `mixed`
2. Domain exists in `research_domains.yaml`
3. For China context: `language='zh'`

**Debug:**
```python
from app.core.prompt_builder import PromptBuilder
from app.models import UserConfig

config = UserConfig(
    mode='grad',
    domain='cv_segmentation',
    language='zh',
    target_desc='Test',
    resume_text='Test resume'
)

builder = PromptBuilder()
prompt = builder.build(config)
print('=== Research Guidance ===')
print(prompt[prompt.find('研究领域知识库'):prompt.find('研究领域知识库')+500])
```

### Issue: YAML parsing error

**Common causes:**
- Indentation errors (use spaces, not tabs)
- Missing quotes around special characters
- Invalid list format

**Fix:**
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('config/research_domains.yaml'))"
```

### Issue: Conferences not showing up

**Check:**
1. `conferences` field is properly formatted
2. Nested structure (tier1, ml, medical) is correct
3. List items have proper indentation

## Best Practices

### For Research Domains

1. **Use Official Names**: Always use official conference/journal acronyms
2. **Keep It General**: Focus on methodologies, not specific implementations
3. **Verifiable Queries**: Only suggest searches that will return real results
4. **Regular Updates**: Review and update domains annually with new conferences

### For China Grad Context

1. **Cultural Sensitivity**: Respect Chinese academic norms and traditions
2. **Current Practices**: Keep interview patterns up-to-date with current practices
3. **No Specifics**: Use patterns only, never specific real questions
4. **Balanced Guidance**: Provide both what to expect and how to prepare

### For Contributors

1. **Test Before Commit**: Always test new domains with actual report generation
2. **Document Changes**: Update this file when adding significant domains
3. **Peer Review**: Have domain experts review new configurations
4. **Version Control**: Keep old domains for backward compatibility

## Future Enhancements

Potential improvements (not yet implemented):
- **Dynamic Conference Updates**: Auto-fetch latest conference deadlines
- **Domain Relationships**: Link related domains (e.g., CV → Multimodal)
- **Personalized Emphasis**: Adjust based on user's publication record
- **International Context**: Add configs for US/EU/SG grad schools
- **Domain Combinations**: Support multi-domain research (e.g., CV + NLP)

## Contributing

To contribute new research domains:

1. Fork the repository
2. Add your domain to `config/research_domains.yaml`
3. Test with grad-mode config
4. Submit PR with:
   - Domain configuration
   - Test example
   - Brief description of the domain

For questions or suggestions, open an issue on GitHub.

## References

- [CVPR](https://cvpr.thecvf.com/)
- [NeurIPS](https://nips.cc/)
- [ACL](https://www.aclweb.org/portal/)
- [MICCAI](http://www.miccai.org/)

---

*Last updated: 2025-11-18*
