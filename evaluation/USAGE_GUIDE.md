# Evaluation Toolkit - Quick Usage Guide

## Quick Start

### 1. Single Report Evaluation

Evaluate a report using a predefined test case:

```bash
# Evaluate backend job interview case
python scripts/eval_report.py --case job_backend

# Evaluate LLM application case
python scripts/eval_report.py --case job_llm_app

# Evaluate grad school CV case
python scripts/eval_report.py --case grad_cv_segmentation
```

**Output Example:**
```
🧪 Running test case: job_backend
   Backend engineer job interview preparation

📄 Loading resume from: examples/mixed_backend_grad/resume.md
⚙️  Loading config from: examples/quality_cases/config_job_backend.json
🤖 Generating report (mode=job, domain=backend)...

📊 Evaluating report quality...

============================================================
📊 REPORT QUALITY EVALUATION
============================================================

✅ Overall Quality Score: 85.0/100

Core Metrics:
  • Question Count: ✅ 12
  • Uniqueness Ratio: ✅ 0.95
  • Missing Rationales: ✅ 0
  • Missing Baselines: ✅ 0

Length Metrics:
  • Avg Question Length: ✅ 65 chars
  • Avg Rationale Length: 120 chars
  • Avg Baseline Length: ✅ 280 chars

✅ No quality issues detected!

============================================================
```

### 2. Save Report for Comparison

Save a report before making code changes:

```bash
# Save baseline report
python scripts/eval_report.py \
  --case job_backend \
  --output baseline_v1.0.json
```

After making changes, generate a new report:

```bash
# Save candidate report after refactoring
python scripts/eval_report.py \
  --case job_backend \
  --output candidate_v2.0.json
```

### 3. Compare Reports

Compare the two reports to detect improvements or regressions:

```bash
# Basic comparison
python scripts/compare_reports.py \
  baseline_v1.0.json \
  candidate_v2.0.json

# Comparison with custom names
python scripts/compare_reports.py \
  --baseline baseline_v1.0.json \
  --candidate candidate_v2.0.json \
  --names "v1.0-original" "v2.0-refactored"

# Export comparison results
python scripts/compare_reports.py \
  baseline_v1.0.json \
  candidate_v2.0.json \
  --output comparison.json \
  --markdown comparison.md
```

**Output Example:**
```
============================================================
🔍 REPORT COMPARISON
============================================================

Baseline: v1.0-original
Candidate: v2.0-refactored

📈 Quality Score: 78.5 → 85.0 (+6.5)

Key Metrics:
  • Questions: 15 → 12 (-3)
  • Uniqueness: 0.87 → 0.95 (+0.08)
  • Missing Rationales: 2 → 0
  • Missing Baselines: 1 → 0

Question Overlap:
  • Common questions: 8
  • New questions: 4
  • Removed questions: 7
  • Tag overlap: 0.75

✅ Improvements:
  • Overall quality improved by 6.5 points
  • Uniqueness improved by 0.08 (less duplication)
  • Removed 3 questions (more focused)
  • Fewer missing rationales (2 improvement)
  • Fewer missing baseline answers (1 improvement)

❌ Regressions:
  (none detected)

============================================================
```

## Common Workflows

### Workflow 1: Regression Testing Before PR

```bash
# 1. Save baseline before changes
python scripts/eval_report.py --case job_backend --output reports/baseline.json

# 2. Make your code changes
# ... edit code ...

# 3. Generate report with changes
python scripts/eval_report.py --case job_backend --output reports/candidate.json

# 4. Compare
python scripts/compare_reports.py \
  reports/baseline.json \
  reports/candidate.json \
  --markdown reports/pr_comparison.md

# 5. Review comparison in reports/pr_comparison.md
cat reports/pr_comparison.md
```

### Workflow 2: Batch Evaluation Across Test Cases

```bash
#!/bin/bash
# evaluate_all.sh

CASES=("job_backend" "job_llm_app" "grad_cv_segmentation" "job_frontend")

for case in "${CASES[@]}"; do
  echo "Evaluating $case..."
  python scripts/eval_report.py --case "$case" --output "reports/${case}_report.json"
  echo ""
done

echo "✅ All test cases evaluated!"
```

### Workflow 3: Compare Across Different Models

```bash
# Generate with Claude Sonnet 4
python scripts/eval_report.py \
  --case job_backend \
  --provider anthropic \
  --model claude-sonnet-4 \
  --output reports/sonnet4.json

# Generate with Claude Opus 4
python scripts/eval_report.py \
  --case job_backend \
  --provider anthropic \
  --model claude-opus-4 \
  --output reports/opus4.json

# Compare models
python scripts/compare_reports.py \
  reports/sonnet4.json \
  reports/opus4.json \
  --names "Sonnet-4" "Opus-4" \
  --markdown reports/model_comparison.md
```

### Workflow 4: Custom Evaluation

```bash
# Evaluate custom resume and config
python scripts/eval_report.py \
  --config my_custom_config.json \
  --resume my_resume.md \
  --output custom_report.json
```

## Interpreting Results

### Quality Score Ranges

- **90-100**: Excellent - All metrics in ideal ranges
- **80-89**: Good - Minor issues, generally high quality
- **70-79**: Fair - Some quality issues need attention
- **60-69**: Poor - Multiple quality issues
- **<60**: Very Poor - Major quality problems

### Common Issues and Solutions

#### Issue: Low Uniqueness Ratio (<0.85)

**Problem**: Too many duplicate or similar questions

**Solutions**:
- Review question generation prompts
- Improve agent diversity in multi-agent mode
- Strengthen deduplication logic in ForumEngine

#### Issue: Too Many Questions (>20)

**Problem**: Report overwhelming for candidates

**Solutions**:
- Adjust question_count target in modes.yaml
- Improve selection criteria in ForumEngine
- Tighten relevance scoring

#### Issue: Missing Rationales/Baselines

**Problem**: Incomplete question metadata

**Solutions**:
- Check agent output validation
- Review enhancement logic in ForumEngine
- Ensure all agents provide required fields

#### Issue: Questions Too Short (<30 chars)

**Problem**: Questions too vague or unclear

**Solutions**:
- Improve question generation prompts
- Add length validation in agent validation
- Review examples in prompt templates

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Report Quality Check

on: [pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Evaluate test cases
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/eval_report.py --case job_backend --output report.json

      - name: Check quality threshold
        run: |
          python -c "
          import json
          from app.eval import evaluate_report
          from app.models.report import Report

          with open('report.json') as f:
              report_data = json.load(f)
          report = Report.model_validate(report_data)
          summary = evaluate_report(report)

          if summary.quality_score < 70:
              print(f'❌ Quality score too low: {summary.quality_score}')
              exit(1)
          print(f'✅ Quality score: {summary.quality_score}')
          "
```

## Tips and Best Practices

### 1. Consistent Test Cases

Always use the same test cases for comparison:
```bash
# Good: Same case for before/after
python scripts/eval_report.py --case job_backend --output before.json
# ... make changes ...
python scripts/eval_report.py --case job_backend --output after.json

# Bad: Different cases
python scripts/eval_report.py --case job_backend --output before.json
python scripts/eval_report.py --case job_llm_app --output after.json  # Wrong!
```

### 2. Save Intermediate Results

Keep a history of reports for trend analysis:
```bash
reports/
  2024-01-15_v1.0.json
  2024-01-20_v1.1.json
  2024-01-25_v2.0.json
```

### 3. Document Comparison Results

Export comparisons to markdown for documentation:
```bash
python scripts/compare_reports.py \
  reports/v1.0.json \
  reports/v2.0.json \
  --markdown docs/v2.0_improvements.md
```

### 4. Use Quiet Mode for CI

Less verbose output in automated environments:
```bash
python scripts/eval_report.py --case job_backend --quiet
```

### 5. Regular Baseline Updates

Update baselines after intentional improvements:
```bash
# After confirming v2.0 is better
cp reports/v2.0.json baselines/job_backend_baseline.json
```

## Troubleshooting

### "Test case not found"

Check test case names:
```bash
# View available cases
cat evaluation/test_cases.yaml | grep "name:"
```

### "Resume file not found"

Ensure paths are relative to project root:
```bash
# Check if file exists
ls -l examples/job_llm_app/resume.md
```

### Import Errors

Ensure you're running from project root:
```bash
# Run from project root
cd /path/to/GrillRadar
python scripts/eval_report.py --case job_backend
```

### API Key Not Set

Set environment variables:
```bash
export ANTHROPIC_API_KEY="your-key-here"
python scripts/eval_report.py --case job_backend
```

## Next Steps

1. **Run First Evaluation**: Start with `python scripts/eval_report.py --case job_backend`
2. **Save Baselines**: Create baseline reports for all test cases
3. **Make Improvements**: Enhance your code
4. **Compare Results**: Use comparison script to validate improvements
5. **Iterate**: Repeat until quality scores improve

For more details, see [evaluation/README.md](README.md)
