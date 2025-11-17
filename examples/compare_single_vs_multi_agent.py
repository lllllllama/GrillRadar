#!/usr/bin/env python3
"""
GrillRadar Multi-Agent Comparison Demo

This script demonstrates the value of BettaFish-style multi-agent architecture
by comparing single-agent vs multi-agent report generation for the same resume.

Key comparisons:
1. Question diversity (role perspectives)
2. Question quality scores
3. Coverage of different dimensions
4. Generation time and cost

Usage:
    python examples/compare_single_vs_multi_agent.py
    python examples/compare_single_vs_multi_agent.py --case job_backend
    python examples/compare_single_vs_multi_agent.py --output comparison_report.md
"""
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

from app.models.user_config import UserConfig
from app.models.report import Report
from app.core.report_generator import ReportGenerator
from app.core.agent_orchestrator import AgentOrchestrator


class ComparisonMetrics:
    """Metrics for comparing single vs multi-agent approaches"""

    def __init__(self, report: Report, generation_time: float):
        self.report = report
        self.generation_time = generation_time

    def get_role_diversity(self) -> Dict[str, int]:
        """Count questions by role"""
        role_counter = Counter()
        for q in self.report.questions:
            role_counter[q.view_role] += 1
        return dict(role_counter)

    def get_tag_diversity(self) -> Dict[str, int]:
        """Count questions by tag"""
        tag_counter = Counter()
        for q in self.report.questions:
            tag_counter[q.tag] += 1
        return dict(tag_counter)

    def get_avg_question_length(self) -> float:
        """Average question length"""
        if not self.report.questions:
            return 0
        return sum(len(q.question) for q in self.report.questions) / len(self.report.questions)

    def get_avg_rationale_length(self) -> float:
        """Average rationale length"""
        if not self.report.questions:
            return 0
        return sum(len(q.rationale) for q in self.report.questions) / len(self.report.questions)

    def get_avg_answer_length(self) -> float:
        """Average baseline answer length"""
        if not self.report.questions:
            return 0
        return sum(len(q.baseline_answer) for q in self.report.questions) / len(self.report.questions)

    def count_resume_references(self) -> int:
        """Count how many questions explicitly reference resume content"""
        count = 0
        resume_keywords = ['项目', '经历', '简历', '你的', '你在', '你做']
        for q in self.report.questions:
            if any(kw in q.question for kw in resume_keywords):
                count += 1
        return count

    def get_summary(self) -> Dict[str, Any]:
        """Get complete metrics summary"""
        return {
            'total_questions': len(self.report.questions),
            'generation_time': round(self.generation_time, 2),
            'role_diversity': self.get_role_diversity(),
            'tag_diversity': self.get_tag_diversity(),
            'unique_roles': len(self.get_role_diversity()),
            'unique_tags': len(self.get_tag_diversity()),
            'avg_question_length': round(self.get_avg_question_length(), 1),
            'avg_rationale_length': round(self.get_avg_rationale_length(), 1),
            'avg_answer_length': round(self.get_avg_answer_length(), 1),
            'resume_references': self.count_resume_references(),
            'resume_reference_rate': round(
                self.count_resume_references() / len(self.report.questions) * 100, 1
            ) if self.report.questions else 0
        }


def generate_single_agent_report(user_config: UserConfig) -> tuple[Report, float]:
    """
    Generate report using single-agent approach (traditional prompt)

    Args:
        user_config: User configuration

    Returns:
        Tuple of (Report, generation_time)
    """
    print("  📝 Generating single-agent report...")
    print("  (Using traditional single-prompt approach)")

    start_time = time.time()

    # Use standard ReportGenerator (single LLM call)
    generator = ReportGenerator()
    report = generator.generate_report(user_config)

    generation_time = time.time() - start_time

    print(f"  ✓ Single-agent report generated in {generation_time:.2f}s")
    return report, generation_time


def generate_multi_agent_report(user_config: UserConfig) -> tuple[Report, float]:
    """
    Generate report using multi-agent approach (BettaFish-style)

    Args:
        user_config: User configuration

    Returns:
        Tuple of (Report, generation_time)
    """
    print("  🤖 Generating multi-agent report...")
    print("  (Using 6-agent collaboration with ForumEngine)")

    start_time = time.time()

    # Use AgentOrchestrator (multi-agent system)
    orchestrator = AgentOrchestrator()
    report = await_sync(orchestrator.generate_report(user_config, enable_multi_agent=True))

    generation_time = time.time() - start_time

    print(f"  ✓ Multi-agent report generated in {generation_time:.2f}s")
    return report, generation_time


def await_sync(coroutine):
    """Synchronously run async coroutine"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coroutine)


def print_comparison(single_metrics: ComparisonMetrics, multi_metrics: ComparisonMetrics):
    """Print comparison results to console"""
    single_summary = single_metrics.get_summary()
    multi_summary = multi_metrics.get_summary()

    print("\n" + "=" * 80)
    print("📊 COMPARISON RESULTS")
    print("=" * 80 + "\n")

    # Basic metrics
    print("📈 Basic Metrics:")
    print(f"  {'Metric':<30} {'Single-Agent':<20} {'Multi-Agent':<20}")
    print("  " + "-" * 70)
    print(f"  {'Total Questions':<30} {single_summary['total_questions']:<20} {multi_summary['total_questions']:<20}")
    print(f"  {'Generation Time (s)':<30} {single_summary['generation_time']:<20} {multi_summary['generation_time']:<20}")
    print(f"  {'Unique Roles':<30} {single_summary['unique_roles']:<20} {multi_summary['unique_roles']:<20}")
    print(f"  {'Unique Tags':<30} {single_summary['unique_tags']:<20} {multi_summary['unique_tags']:<20}")
    print()

    # Quality metrics
    print("✨ Quality Metrics:")
    print(f"  {'Metric':<30} {'Single-Agent':<20} {'Multi-Agent':<20} {'Improvement':<20}")
    print("  " + "-" * 90)

    # Average lengths
    question_improvement = (
        (multi_summary['avg_question_length'] - single_summary['avg_question_length'])
        / single_summary['avg_question_length'] * 100
    ) if single_summary['avg_question_length'] > 0 else 0

    print(f"  {'Avg Question Length':<30} {single_summary['avg_question_length']:<20} {multi_summary['avg_question_length']:<20} {question_improvement:+.1f}%")
    print(f"  {'Avg Rationale Length':<30} {single_summary['avg_rationale_length']:<20} {multi_summary['avg_rationale_length']:<20}")
    print(f"  {'Resume Reference Rate':<30} {single_summary['resume_reference_rate']}%{'':<15} {multi_summary['resume_reference_rate']}%")
    print()

    # Role diversity
    print("🎭 Role Diversity:")
    all_roles = set(list(single_summary['role_diversity'].keys()) + list(multi_summary['role_diversity'].keys()))
    for role in sorted(all_roles):
        single_count = single_summary['role_diversity'].get(role, 0)
        multi_count = multi_summary['role_diversity'].get(role, 0)
        print(f"  {role:<40} {single_count:<10} {multi_count:<10}")
    print()

    # Key insights
    print("💡 Key Insights:")
    insights = []

    if multi_summary['unique_roles'] > single_summary['unique_roles']:
        insights.append(f"  ✓ Multi-agent approach includes {multi_summary['unique_roles']} different role perspectives")
        insights.append(f"    vs {single_summary['unique_roles']} in single-agent")

    if multi_summary['unique_tags'] > single_summary['unique_tags']:
        insights.append(f"  ✓ Multi-agent covers {multi_summary['unique_tags']} unique topics")
        insights.append(f"    vs {single_summary['unique_tags']} in single-agent")

    if multi_summary['resume_reference_rate'] > single_summary['resume_reference_rate']:
        insights.append(f"  ✓ Multi-agent questions are {multi_summary['resume_reference_rate']:.1f}% resume-specific")
        insights.append(f"    vs {single_summary['resume_reference_rate']:.1f}% in single-agent")

    if multi_summary['generation_time'] < single_summary['generation_time'] * 2:
        insights.append(f"  ✓ Multi-agent generation time is acceptable")
        insights.append(f"    (only {multi_summary['generation_time'] / single_summary['generation_time']:.1f}x of single-agent)")

    for insight in insights:
        print(insight)

    if not insights:
        print("  (No significant differences detected)")

    print()


def export_markdown_report(
    single_metrics: ComparisonMetrics,
    multi_metrics: ComparisonMetrics,
    output_path: Path,
    case_name: str
):
    """Export comparison report to Markdown file"""
    single_summary = single_metrics.get_summary()
    multi_summary = multi_metrics.get_summary()

    lines = []
    lines.append(f"# GrillRadar Multi-Agent Comparison Report")
    lines.append(f"")
    lines.append(f"**Test Case**: {case_name}")
    lines.append(f"**Generated At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    lines.append(f"## 📊 Quantitative Comparison")
    lines.append(f"")
    lines.append(f"### Basic Metrics")
    lines.append(f"")
    lines.append(f"| Metric | Single-Agent | Multi-Agent | Difference |")
    lines.append(f"|--------|--------------|-------------|------------|")
    lines.append(f"| Total Questions | {single_summary['total_questions']} | {multi_summary['total_questions']} | {multi_summary['total_questions'] - single_summary['total_questions']:+d} |")
    lines.append(f"| Generation Time (s) | {single_summary['generation_time']} | {multi_summary['generation_time']} | {multi_summary['generation_time'] - single_summary['generation_time']:+.2f} |")
    lines.append(f"| Unique Roles | {single_summary['unique_roles']} | {multi_summary['unique_roles']} | {multi_summary['unique_roles'] - single_summary['unique_roles']:+d} |")
    lines.append(f"| Unique Tags | {single_summary['unique_tags']} | {multi_summary['unique_tags']} | {multi_summary['unique_tags'] - single_summary['unique_tags']:+d} |")
    lines.append(f"")

    lines.append(f"### Quality Metrics")
    lines.append(f"")
    lines.append(f"| Metric | Single-Agent | Multi-Agent |")
    lines.append(f"|--------|--------------|-------------|")
    lines.append(f"| Avg Question Length | {single_summary['avg_question_length']} | {multi_summary['avg_question_length']} |")
    lines.append(f"| Avg Rationale Length | {single_summary['avg_rationale_length']} | {multi_summary['avg_rationale_length']} |")
    lines.append(f"| Avg Answer Length | {single_summary['avg_answer_length']} | {multi_summary['avg_answer_length']} |")
    lines.append(f"| Resume References | {single_summary['resume_references']} ({single_summary['resume_reference_rate']}%) | {multi_summary['resume_references']} ({multi_summary['resume_reference_rate']}%) |")
    lines.append(f"")

    lines.append(f"## 🎭 Role Diversity Analysis")
    lines.append(f"")
    lines.append(f"### Single-Agent Role Distribution")
    lines.append(f"")
    for role, count in single_summary['role_diversity'].items():
        lines.append(f"- **{role}**: {count} questions")
    lines.append(f"")

    lines.append(f"### Multi-Agent Role Distribution")
    lines.append(f"")
    for role, count in multi_summary['role_diversity'].items():
        lines.append(f"- **{role}**: {count} questions")
    lines.append(f"")

    lines.append(f"## 💡 Key Findings")
    lines.append(f"")
    lines.append(f"### Advantages of Multi-Agent Approach")
    lines.append(f"")
    lines.append(f"1. **Enhanced Perspective Diversity**: Multi-agent system incorporates {multi_summary['unique_roles']} different role perspectives")
    lines.append(f"2. **Improved Topic Coverage**: Covers {multi_summary['unique_tags']} unique topics")
    lines.append(f"3. **Resume Specificity**: {multi_summary['resume_reference_rate']:.1f}% of questions reference resume content")
    lines.append(f"4. **Collaborative Quality**: Questions benefit from virtual forum discussion and deduplication")
    lines.append(f"")

    lines.append(f"### Trade-offs")
    lines.append(f"")
    lines.append(f"- **Generation Time**: {multi_summary['generation_time']:.2f}s vs {single_summary['generation_time']:.2f}s ({multi_summary['generation_time'] / single_summary['generation_time']:.1f}x)")
    lines.append(f"- **Complexity**: Multi-agent system requires coordination and deduplication logic")
    lines.append(f"")

    lines.append(f"## 📝 Sample Questions Comparison")
    lines.append(f"")
    lines.append(f"### Single-Agent Sample")
    lines.append(f"")
    if single_metrics.report.questions:
        q = single_metrics.report.questions[0]
        lines.append(f"**Question**: {q.question}")
        lines.append(f"")
        lines.append(f"**Role**: {q.view_role}")
        lines.append(f"")
        lines.append(f"**Rationale**: {q.rationale}")
        lines.append(f"")

    lines.append(f"### Multi-Agent Sample")
    lines.append(f"")
    if multi_metrics.report.questions:
        q = multi_metrics.report.questions[0]
        lines.append(f"**Question**: {q.question}")
        lines.append(f"")
        lines.append(f"**Role**: {q.view_role}")
        lines.append(f"")
        lines.append(f"**Rationale**: {q.rationale}")
        lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*Generated by GrillRadar Multi-Agent Comparison Tool*")

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"  ✓ Markdown report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare single-agent vs multi-agent report generation"
    )
    parser.add_argument(
        "--case", "-c",
        type=str,
        default="job_backend",
        help="Test case to use (job_backend, job_frontend, grad_nlp)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file for markdown report (default: examples/comparison_{case}.md)"
    )

    args = parser.parse_args()

    # Banner
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║         🔬 GrillRadar Multi-Agent Comparison Demo                     ║
║                                                                        ║
║  Demonstrating BettaFish-style multi-agent value vs single-agent     ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)

    # Load test case
    print(f"\n📂 Loading test case: {args.case}")

    quality_cases_dir = project_root / "examples" / "quality_cases"
    resume_path = quality_cases_dir / f"resume_{args.case}.txt"
    config_path = quality_cases_dir / f"config_{args.case}.json"

    if not resume_path.exists() or not config_path.exists():
        print(f"❌ Test case files not found:")
        print(f"   Resume: {resume_path}")
        print(f"   Config: {config_path}")
        sys.exit(1)

    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    user_config = UserConfig(
        mode=config_data["mode"],
        target_desc=config_data["target_desc"],
        domain=config_data.get("domain"),
        resume_text=resume_text,
        enable_external_info=config_data.get("enable_external_info", False)
    )

    print(f"  ✓ Loaded resume ({len(resume_text)} chars)")
    print(f"  ✓ Mode: {user_config.mode}, Domain: {user_config.domain}")
    print()

    # Generate reports
    print("=" * 80)
    print("🔄 GENERATING REPORTS")
    print("=" * 80 + "\n")

    print("1️⃣  Single-Agent Approach")
    single_report, single_time = generate_single_agent_report(user_config)
    single_metrics = ComparisonMetrics(single_report, single_time)
    print()

    print("2️⃣  Multi-Agent Approach")
    multi_report, multi_time = generate_multi_agent_report(user_config)
    multi_metrics = ComparisonMetrics(multi_report, multi_time)
    print()

    # Compare results
    print_comparison(single_metrics, multi_metrics)

    # Export markdown report
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "examples" / f"comparison_{args.case}.md"

    export_markdown_report(single_metrics, multi_metrics, output_path, args.case)

    print("\n" + "=" * 80)
    print("✅ COMPARISON COMPLETE")
    print("=" * 80)
    print(f"\n📄 Full report: {output_path}")
    print()


if __name__ == "__main__":
    main()
