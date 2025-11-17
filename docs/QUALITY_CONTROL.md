# GrillRadar Question Quality Control System

## 📖 Overview

The Quality Control System is a lightweight inspection mechanism designed to evaluate the quality of generated interview questions. It helps developers and QA teams ensure that questions meet high standards before being presented to users.

## 🎯 Purpose

- **Automated Quality Assurance**: Systematically check question quality across multiple dimensions
- **Early Issue Detection**: Identify problems before they reach end users
- **Continuous Improvement**: Track quality metrics over time as the system evolves
- **Developer Tool**: Help developers understand what makes a high-quality question

## 🏗️ Architecture

```
scripts/
└── evaluate_question_quality.py    # Main evaluation script

examples/
└── quality_cases/                  # Test case repository
    ├── README.md                   # Test case documentation
    ├── resume_job_backend.txt      # Backend engineer resume
    ├── config_job_backend.json     # Backend config
    ├── resume_job_frontend.txt     # Frontend engineer resume
    ├── config_job_frontend.json    # Frontend config
    ├── resume_grad_nlp.txt         # NLP PhD applicant resume
    └── config_grad_nlp.json        # NLP config
```

## 🔍 Quality Dimensions

### 1. Question Quality

#### Question Length
- **Minimum**: 10 characters (FAIL if below)
- **Recommended**: 20+ characters (WARNING if below)
- **Rationale**: Questions should be specific enough to provide clear direction

#### Question Clarity
- **Check**: Not overly generic (e.g., "请介绍一下...")
- **Check**: Contains specific context or technical terms
- **Severity**: WARNING
- **Rationale**: Specific questions are more valuable for preparation

### 2. Rationale Quality

#### Rationale Length
- **Minimum**: 30 characters (FAIL if below)
- **Recommended**: 50+ characters (WARNING if below)
- **Rationale**: Rationale should explain WHY the question matters

#### Rationale Context
- **Check**: Mentions resume content, target position, or domain
- **Keywords**: 简历, 经历, 项目, 岗位, 目标, 领域, etc.
- **Severity**: WARNING
- **Rationale**: Rationale should tie question to user's specific situation

### 3. Baseline Answer Quality

#### Answer Structure
- **Check**: Has paragraphs (2+ line breaks) OR bullet points OR sections
- **Severity**: WARNING
- **Rationale**: Structured answers are easier to learn from

#### Answer Depth
- **Minimum**: 50 characters (FAIL if below)
- **Recommended**: 200+ characters (WARNING if below)
- **Rationale**: Answers should provide substantial guidance

### 4. Support Notes Quality

#### Support Notes Specificity
- **Check**: Contains technical terms, papers, tools, or resources
- **Check**: Has numbers, versions, or specific references
- **Severity**: WARNING
- **Rationale**: Specific resources are more actionable

#### Support Notes Length
- **Minimum**: 20 characters (FAIL if below)
- **Recommended**: 100+ characters (WARNING if below)
- **Rationale**: Should provide concrete learning directions

### 5. Prompt Template Quality

#### Template Validity
- **Check**: Contains placeholders (e.g., `{your_experience}`, `{your_project}`)
- **Check**: More detailed than the question itself
- **Severity**: WARNING
- **Rationale**: Templates should guide users in practice sessions

## 🚀 Usage

### Quick Start

```bash
# Run quality evaluation on all test cases
python scripts/evaluate_question_quality.py

# Run on a specific case
python scripts/evaluate_question_quality.py --case job_backend

# Run with verbose output (includes detailed recommendations)
python scripts/evaluate_question_quality.py --verbose

# Run on multiple specific cases
python scripts/evaluate_question_quality.py --case grad_nlp --verbose
```

### Command-Line Options

```
--verbose, -v          Show detailed output including improvement suggestions
--case CASE, -c CASE   Run specific test case (job_backend, job_frontend, grad_nlp)
--skip-generation, -s  Skip report generation (for cached reports)
```

## 📊 Output Format

### Summary Statistics

```
📊 Overall Statistics:
  Total Questions: 15
  ✓ Passed: 12 (80.0%)
  ⚠ Warnings: 2 (13.3%)
  ✗ Failures: 1 (6.7%)
  Total Issues: 8
```

### Per-Question Details

```
✓ Question 1: 你在简历中提到使用Go语言开发了用户认证服务...
  Pass Rate: 100% (9/9 checks)
  All checks passed!

⚠ Question 2: 请描述一下你对Redis的理解
  Pass Rate: 89% (8/9 checks)
  ⚠ WARNING Question Clarity: Question may be too generic
     → Consider adding specific context or technical details

✗ Question 3: 项目经验
  Pass Rate: 33% (3/9 checks)
  ✗ FAIL Question Length: Question too short (8 chars)
  ✗ FAIL Rationale Length: Rationale too short (15 chars)
  ⚠ WARNING Answer Depth: Baseline answer is brief (85 chars)
```

### Quality Grading

```
📈 Overall Quality Score: 85.2%
   Grade: B (Good)
```

- **Grade A (90%+)**: Excellent - ready for production
- **Grade B (80-89%)**: Good - minor improvements recommended
- **Grade C (70-79%)**: Acceptable - some improvements needed
- **Grade D (<70%)**: Needs improvement - significant issues

## 🛠️ Extending the System

### Adding New Quality Checks

1. Add a new check method to `QuestionQualityChecker` class:

```python
def _check_your_new_rule(self, q: QuestionItem) -> QualityIssue | None:
    """Check your new quality dimension"""
    # Your validation logic here

    if condition_not_met:
        return QualityIssue(
            check_name="Your Check Name",
            severity=CheckSeverity.WARNING,  # or FAIL
            message="Brief description of issue",
            details="Detailed explanation and recommendation"
        )
    return None
```

2. Add the check to the `checks` list in `check_question()` method:

```python
checks = [
    # ... existing checks ...
    self._check_your_new_rule,
]
```

### Adding New Test Cases

1. Create resume file: `examples/quality_cases/resume_{your_case}.txt`
2. Create config file: `examples/quality_cases/config_{your_case}.json`
3. Add case name to `available_cases` list in `main()` function
4. Update `examples/quality_cases/README.md` with case description

Example config:
```json
{
  "target_desc": "Your target position",
  "mode": "job",  // or "grad" or "mixed"
  "domain": "your_domain",
  "level": "junior",  // or "mid" or "senior"
  "enable_external_info": false,
  "multi_agent_enabled": true
}
```

## 📈 Best Practices

### For Developers

1. **Run quality checks before major releases**
   ```bash
   python scripts/evaluate_question_quality.py --verbose
   ```

2. **Create test cases for new domains**
   - When adding a new domain, create corresponding quality test cases
   - Ensures consistent quality across all domains

3. **Track quality metrics over time**
   - Document quality scores for each release
   - Set quality thresholds (e.g., 85%+ required for production)

4. **Use verbose mode for debugging**
   - Detailed recommendations help understand failure reasons
   - Useful for improving prompts and generation logic

### For QA Teams

1. **Regression Testing**
   - Run quality checks after prompt changes
   - Verify that changes improve quality scores

2. **Domain Coverage**
   - Ensure all domains have quality test cases
   - Test both job and grad modes

3. **Edge Case Testing**
   - Create test cases for challenging scenarios
   - E.g., very short resumes, rare domains, mixed mode

## 🔬 Quality Metrics Interpretation

### Pass Rate Thresholds

- **95%+**: Exceptional quality - best-in-class questions
- **90-94%**: Excellent quality - production ready
- **85-89%**: Good quality - minor polish recommended
- **80-84%**: Acceptable quality - some improvements beneficial
- **<80%**: Needs improvement - review generation logic

### Issue Severity Interpretation

- **FAIL**: Critical issues that significantly impact user experience
  - Must be fixed before production deployment
  - E.g., empty questions, missing baseline answers

- **WARNING**: Quality issues that reduce value but don't break functionality
  - Should be addressed but not blocking
  - E.g., generic questions, brief rationales

- **PASS**: Meets all quality criteria
  - Ready for user consumption
  - No action required

## 📚 Related Documentation

- [Test Cases README](../examples/quality_cases/README.md) - Detailed test case descriptions
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute quality improvements
- [Architecture Overview](./ARCHITECTURE.md) - System design and components

## 🤝 Contributing

We welcome contributions to improve the quality control system:

1. **New quality checks**: Propose additional validation rules
2. **Test cases**: Add diverse scenarios for better coverage
3. **Metrics**: Suggest new quality metrics to track
4. **Tooling**: Enhance the evaluation script with new features

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📞 Support

If you encounter issues with quality evaluation:

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify API keys are configured in `.env`
3. Run with `--verbose` flag for detailed error messages
4. Open an issue on GitHub with quality evaluation output

---

**Version**: 1.0.0
**Last Updated**: 2024-11
**Maintainer**: GrillRadar Team
