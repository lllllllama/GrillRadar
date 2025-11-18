# GrillRadar Quality Test Cases

This directory contains test cases for evaluating the quality of generated questions.

## 📁 Test Cases

### 1. Job - Backend Engineer (`job_backend`)
- **Resume**: `resume_job_backend.txt`
- **Config**: `config_job_backend.json`
- **Scenario**: Backend engineer (Go/Python) applying to Alibaba Cloud
- **Key points**: Microservices, distributed systems, API gateway

### 2. Job - Frontend Engineer (`job_frontend`)
- **Resume**: `resume_job_frontend.txt`
- **Config**: `config_job_frontend.json`
- **Scenario**: Frontend engineer (React) applying to ByteDance
- **Key points**: React, TypeScript, performance optimization, collaboration tools

### 3. Graduate - NLP PhD (`grad_nlp`)
- **Resume**: `resume_grad_nlp.txt`
- **Config**: `config_grad_nlp.json`
- **Scenario**: NLP researcher applying to Stanford/CMU PhD programs
- **Key points**: Large language models, few-shot learning, controllable generation

## 🔧 Usage

### Run quality evaluation on all cases:
```bash
python scripts/evaluate_question_quality.py
```

### Run quality evaluation on a specific case:
```bash
python scripts/evaluate_question_quality.py --case job_backend
python scripts/evaluate_question_quality.py --case grad_nlp
```

### Run with verbose output:
```bash
python scripts/evaluate_question_quality.py --verbose
```

## 📊 Quality Checks

The evaluation script checks the following quality dimensions:

### Question Quality
- ✓ Length (minimum 10 chars, recommended 20+)
- ✓ Clarity (not too generic, has specific context)

### Rationale Quality
- ✓ Length (minimum 30 chars, recommended 50+)
- ✓ Contextual relevance (mentions resume/target/domain)

### Baseline Answer Quality
- ✓ Structure (has paragraphs, bullets, or sections)
- ✓ Depth (minimum 50 chars, recommended 200+)

### Support Notes Quality
- ✓ Specificity (contains knowledge points, resources)
- ✓ Length (minimum 20 chars, recommended 100+)

### Prompt Template Quality
- ✓ Has placeholders for practice (e.g., {your_experience})
- ✓ More detailed than the question itself

## 📈 Quality Grading

- **Grade A (90%+)**: Excellent - ready for production
- **Grade B (80-89%)**: Good - minor improvements recommended
- **Grade C (70-79%)**: Acceptable - some improvements needed
- **Grade D (<70%)**: Needs improvement - significant issues

## 🎯 Adding New Test Cases

To add a new test case:

1. Create resume file: `resume_{your_case}.txt`
2. Create config file: `config_{your_case}.json`
3. Add case name to `available_cases` in `evaluate_question_quality.py`
4. Run evaluation: `python scripts/evaluate_question_quality.py --case {your_case}`

## 💡 Tips for Quality Improvement

If you see quality issues:

1. **Question too generic**: Add specific technical context or domain terms
2. **Rationale lacks context**: Reference specific resume items or target requirements
3. **Answer lacks structure**: Use paragraphs, bullet points, or numbered lists
4. **Support notes not specific**: Include concrete papers, tools, or concepts
5. **Prompt template missing placeholders**: Add {your_experience}, {your_project}, etc.
