# GrillRadar Evaluation Toolkit

A lightweight quality evaluation and regression comparison toolkit for generated reports.

## Purpose

This toolkit helps developers answer: **"Did this change make our grills more focused, less repetitive, and overall better?"**

## Components

### 1. Test Cases (`test_cases.yaml`)

Fixed input cases for consistent evaluation:
- Backend job interview
- LLM application job interview
- CV segmentation PhD application
- Frontend job interview

Each case includes:
- Resume path (reusing examples)
- Config path
- Expected quality thresholds

### 2. Quality Metrics (`app/eval/report_quality.py`)

Computes metrics for a generated report:
- **Question count**: Total number of questions
- **Uniqueness ratio**: Detects duplicate questions
- **Missing rationales**: Questions without proper rationale
- **Average lengths**: Question, rationale, baseline answer
- **Tag/role distribution**: Coverage across dimensions

### 3. Single Report Evaluation (`scripts/eval_report.py`)

Evaluate a single report:

```bash
# Evaluate using a named test case
python scripts/eval_report.py --case job_backend

# Evaluate using custom config and resume
python scripts/eval_report.py --config config.json --resume resume.md

# Save report JSON for comparison
python scripts/eval_report.py --case job_llm_app --output report_v1.json
```

### 4. Report Comparison (`scripts/compare_reports.py`)

Compare two reports (e.g., old vs new engine):

```bash
# Compare two saved reports
python scripts/compare_reports.py report_v1.json report_v2.json

# Compare with human-readable names
python scripts/compare_reports.py \
  --baseline report_v1.json \
  --candidate report_v2.json \
  --names "v1.0" "v2.0-refactored"
```

## Workflow

### Evaluating Quality

```bash
# Run evaluation on all test cases
for case in job_backend job_llm_app grad_cv_segmentation; do
  python scripts/eval_report.py --case $case
done
```

### Regression Testing

```bash
# Before making changes
python scripts/eval_report.py --case job_backend --output baseline.json

# After making changes
python scripts/eval_report.py --case job_backend --output candidate.json

# Compare
python scripts/compare_reports.py baseline.json candidate.json
```

## Quality Indicators

The evaluation script provides visual indicators:

- ✅ **Pass**: Metric within expected range
- ⚠️  **Warning**: Metric slightly outside expected range
- ❌ **Fail**: Metric significantly outside expected range

## Metrics Reference

### Question Count
- **Good**: 10-15 questions (focused)
- **Warning**: 8-9 or 16-20 questions
- **Bad**: <8 (insufficient) or >20 (overwhelming)

### Uniqueness Ratio
- **Good**: >0.90 (highly unique)
- **Warning**: 0.85-0.90 (some similarity)
- **Bad**: <0.85 (too many duplicates)

### Missing Rationales
- **Good**: 0 missing
- **Warning**: 1-2 missing
- **Bad**: >2 missing

### Average Question Length
- **Good**: 30-100 characters
- **Warning**: 20-30 or 100-150 characters
- **Bad**: <20 (too vague) or >150 (too wordy)

### Baseline Answer Length
- **Good**: 100-500 characters
- **Warning**: 50-100 or 500-800 characters
- **Bad**: <50 (insufficient) or >800 (too verbose)

## Non-Intrusive Design

This toolkit:
- ✅ Uses public API (GrillRadarPipeline) only
- ✅ Uses public models (Report, QuestionItem)
- ✅ Does not modify core runtime behavior
- ✅ Can be run independently of main application
- ✅ Safe to use in CI/CD pipelines

## Future Enhancements

Potential additions:
- LLM-as-judge evaluation (semantic quality scoring)
- Automated regression detection in CI
- Historical trend tracking
- Benchmark leaderboard
- Question diversity metrics (semantic embeddings)
