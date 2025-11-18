#!/usr/bin/env python3
"""
Report Evaluation Script

Evaluate quality of a single generated report using fixed test cases or custom inputs.

Usage:
    # Evaluate using a named test case
    python scripts/eval_report.py --case job_backend

    # Evaluate using custom config and resume
    python scripts/eval_report.py --config config.json --resume resume.md

    # Save report JSON for later comparison
    python scripts/eval_report.py --case job_llm_app --output report_v1.json

    # Use custom provider/model
    python scripts/eval_report.py --case job_backend --provider anthropic --model claude-sonnet-4
"""
import argparse
import json
import sys
import yaml
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.pipeline import GrillRadarPipeline
from app.models.user_config import UserConfig
from app.models.report import Report
from app.eval.report_quality import evaluate_report, format_quality_summary


def load_test_cases(test_cases_file: Path) -> dict:
    """Load test cases configuration"""
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_config(config_path: Path) -> dict:
    """Load config JSON/YAML file"""
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.suffix == '.json':
            return json.load(f)
        else:
            return yaml.safe_load(f)


def load_resume(resume_path: Path) -> str:
    """Load resume file"""
    with open(resume_path, 'r', encoding='utf-8') as f:
        return f.read()


def save_report(report: Report, output_path: Path):
    """Save report to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Use model_dump for Pydantic v2
        if hasattr(report, 'model_dump'):
            json.dump(report.model_dump(), f, ensure_ascii=False, indent=2)
        else:
            # Fallback for Pydantic v1
            json.dump(report.dict(), f, ensure_ascii=False, indent=2)


def run_evaluation(
    resume_path: Path,
    config_path: Path,
    output_path: Optional[Path] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    verbose: bool = True
) -> Report:
    """
    Run report generation and evaluation

    Args:
        resume_path: Path to resume file
        config_path: Path to config file
        output_path: Optional path to save report JSON
        provider: Optional LLM provider override
        model: Optional LLM model override
        verbose: Whether to print detailed output

    Returns:
        Generated Report object
    """
    print(f"📄 Loading resume from: {resume_path}")
    resume_text = load_resume(resume_path)

    print(f"⚙️  Loading config from: {config_path}")
    config_data = load_config(config_path)

    # Build UserConfig
    config_data['resume_text'] = resume_text
    user_config = UserConfig(**config_data)

    print(f"🤖 Generating report (mode={user_config.mode}, domain={user_config.domain})...")
    print()

    # Initialize pipeline
    pipeline = GrillRadarPipeline(
        llm_provider=provider,
        llm_model=model
    )

    # Generate report
    report = pipeline.run(resume_path=resume_path, user_config=user_config)

    # Save report if requested
    if output_path:
        print(f"💾 Saving report to: {output_path}")
        save_report(report, output_path)
        print()

    # Evaluate quality
    print("📊 Evaluating report quality...")
    print()
    summary = evaluate_report(report)

    # Print formatted summary
    formatted = format_quality_summary(summary, verbose=verbose)
    print(formatted)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate quality of a generated report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate using a named test case
  python scripts/eval_report.py --case job_backend

  # Evaluate using custom config and resume
  python scripts/eval_report.py --config config.json --resume resume.md

  # Save report for later comparison
  python scripts/eval_report.py --case job_llm_app --output report_v1.json

  # Use custom provider/model
  python scripts/eval_report.py --case job_backend --provider anthropic --model claude-sonnet-4
        """
    )

    # Input selection
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--case',
        type=str,
        help='Named test case from test_cases.yaml'
    )
    input_group.add_argument(
        '--config',
        type=Path,
        help='Path to config JSON/YAML file'
    )

    # Custom resume (only needed if not using --case)
    parser.add_argument(
        '--resume',
        type=Path,
        help='Path to resume file (required if using --config)'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=Path,
        help='Path to save report JSON for later comparison'
    )

    # LLM options
    parser.add_argument(
        '--provider',
        type=str,
        help='LLM provider override (e.g., anthropic, openai)'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='LLM model override (e.g., claude-sonnet-4)'
    )

    # Display options
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Less verbose output (hide distributions)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.config and not args.resume:
        parser.error("--resume is required when using --config")

    # Resolve paths
    project_root = Path(__file__).parent.parent

    if args.case:
        # Load test case
        test_cases_file = project_root / "evaluation" / "test_cases.yaml"
        if not test_cases_file.exists():
            print(f"❌ Test cases file not found: {test_cases_file}", file=sys.stderr)
            sys.exit(1)

        test_cases_data = load_test_cases(test_cases_file)
        test_cases = {tc['name']: tc for tc in test_cases_data['test_cases']}

        if args.case not in test_cases:
            print(f"❌ Test case '{args.case}' not found", file=sys.stderr)
            print(f"Available cases: {', '.join(test_cases.keys())}", file=sys.stderr)
            sys.exit(1)

        test_case = test_cases[args.case]
        resume_path = project_root / test_case['resume_path']
        config_path = project_root / test_case['config_path']

        print(f"🧪 Running test case: {args.case}")
        print(f"   {test_case['description']}")
        print()
    else:
        # Use custom paths
        resume_path = args.resume
        config_path = args.config

        if not resume_path.exists():
            print(f"❌ Resume file not found: {resume_path}", file=sys.stderr)
            sys.exit(1)
        if not config_path.exists():
            print(f"❌ Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)

    # Run evaluation
    try:
        report = run_evaluation(
            resume_path=resume_path,
            config_path=config_path,
            output_path=args.output,
            provider=args.provider,
            model=args.model,
            verbose=not args.quiet
        )
        sys.exit(0)
    except Exception as e:
        print(f"❌ Evaluation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
