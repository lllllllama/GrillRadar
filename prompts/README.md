# GrillRadar Prompts Directory

This directory contains all prompt templates used by GrillRadar, extracted from Python code for easier editing and maintenance.

## Structure

```
prompts/
├── system/
│   └── committee_zh.md       # Main committee system prompt (Chinese)
└── agents/
    ├── technical_interviewer_zh.md   # Technical interviewer agent
    ├── hiring_manager_zh.md          # Hiring manager agent
    ├── hr_zh.md                      # HR/behavioral interviewer
    ├── advisor_zh.md                 # Academic advisor/PI
    ├── reviewer_zh.md                # Academic reviewer
    └── advocate_zh.md                # Candidate advocate

```

## How It Works

1. **Prompt Builder** (`app/core/prompt_builder.py`) loads templates from these files
2. Templates use Python format strings with placeholders like `{resume_text}`, `{domain}`, etc.
3. The builder fills in placeholders with actual values at runtime

## Editing Prompts

### System Prompts (`system/`)

The main committee prompt (`committee_zh.md`) defines the overall task and workflow.

**Placeholders**:
- `{mode}` - job/grad/mixed
- `{target_desc}` - Target position
- `{resume_text}` - User's resume
- `{domain_knowledge}` - Domain-specific knowledge
- `{external_info}` - External JD/interview info
- `{role_weights}` - Role weight distribution
- `{question_distribution}` - Question category distribution
- `{target_question_count}` - Target number of questions
- `{min_questions}`, `{max_questions}` - Question count range

### Agent Prompts (`agents/`)

Individual agent prompts for multi-agent mode (future).

## Benefits of External Prompts

✅ **Easy to Edit**: No need to touch Python code to improve prompts
✅ **Version Control**: Changes are tracked in git
✅ **Testing**: Can quickly A/B test different prompt versions
✅ **Collaboration**: Non-programmers can contribute to prompt engineering
✅ **Localization**: Easy to add English versions (e.g., `committee_en.md`)

## Adding New Prompts

1. Create a new `.md` file in the appropriate directory
2. Use `{placeholder}` syntax for dynamic values
3. Update `PromptBuilder` to load the new template
4. Document placeholders in this README

---

Last updated: 2025-11-18
