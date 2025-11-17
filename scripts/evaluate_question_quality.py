#!/usr/bin/env python3
"""
GrillRadar Question Quality Evaluation Script

This script evaluates the quality of generated questions by checking:
- Question clarity and length
- Rationale contextual relevance
- Baseline answer structure and depth
- Support notes specificity
- Prompt template validity

Usage:
    python scripts/evaluate_question_quality.py
    python scripts/evaluate_question_quality.py --verbose
    python scripts/evaluate_question_quality.py --case job_backend
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

from app.models.user_config import UserConfig
from app.models.report import Report, QuestionItem
from app.core.report_generator import ReportGenerator


# Quality Check Results
class CheckSeverity(Enum):
    """Severity level of quality issues"""
    PASS = "✓ PASS"
    WARNING = "⚠ WARNING"
    FAIL = "✗ FAIL"


@dataclass
class QualityIssue:
    """Represents a quality issue found in a question"""
    check_name: str
    severity: CheckSeverity
    message: str
    details: str = ""


@dataclass
class QuestionQualityReport:
    """Quality report for a single question"""
    question_id: int
    question_text: str
    issues: List[QualityIssue] = field(default_factory=list)
    passed_checks: int = 0
    total_checks: int = 0

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage"""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100

    @property
    def has_failures(self) -> bool:
        """Check if there are any FAIL severity issues"""
        return any(issue.severity == CheckSeverity.FAIL for issue in self.issues)

    @property
    def has_warnings(self) -> bool:
        """Check if there are any WARNING severity issues"""
        return any(issue.severity == CheckSeverity.WARNING for issue in self.issues)


class QuestionQualityChecker:
    """Evaluates the quality of generated questions"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def check_question(self, question: QuestionItem) -> QuestionQualityReport:
        """
        Run all quality checks on a single question

        Args:
            question: The QuestionItem to evaluate

        Returns:
            QuestionQualityReport with all findings
        """
        report = QuestionQualityReport(
            question_id=question.id,
            question_text=question.question
        )

        # Run all checks
        checks = [
            self._check_question_length,
            self._check_question_clarity,
            self._check_rationale_length,
            self._check_rationale_context,
            self._check_baseline_answer_structure,
            self._check_baseline_answer_depth,
            self._check_support_notes_specificity,
            self._check_support_notes_length,
            self._check_prompt_template_validity,
        ]

        for check_func in checks:
            issue = check_func(question)
            report.total_checks += 1

            if issue:
                report.issues.append(issue)
                if issue.severity != CheckSeverity.FAIL:
                    report.passed_checks += 1  # WARNING still counts as passed
            else:
                report.passed_checks += 1

        return report

    # ==================== Individual Quality Checks ====================

    def _check_question_length(self, q: QuestionItem) -> QualityIssue | None:
        """Check if question is too short"""
        length = len(q.question)

        if length < 10:
            return QualityIssue(
                check_name="Question Length",
                severity=CheckSeverity.FAIL,
                message=f"Question too short ({length} chars)",
                details="Questions should be at least 10 characters"
            )
        elif length < 20:
            return QualityIssue(
                check_name="Question Length",
                severity=CheckSeverity.WARNING,
                message=f"Question is short ({length} chars)",
                details="Consider making questions more specific (20+ chars recommended)"
            )
        return None

    def _check_question_clarity(self, q: QuestionItem) -> QualityIssue | None:
        """Check if question is clear and not too generic"""
        question_lower = q.question.lower()

        # Check for overly generic patterns
        generic_patterns = [
            "请介绍",
            "请说明",
            "请描述",
            "你能说说",
            "你了解",
        ]

        is_generic = any(pattern in question_lower for pattern in generic_patterns)

        # Check if question has specific technical terms or context
        has_specific_context = any(char.isdigit() for char in q.question) or \
                               len(q.question.split()) > 8

        if is_generic and not has_specific_context:
            return QualityIssue(
                check_name="Question Clarity",
                severity=CheckSeverity.WARNING,
                message="Question may be too generic",
                details="Consider adding specific context or technical details"
            )
        return None

    def _check_rationale_length(self, q: QuestionItem) -> QualityIssue | None:
        """Check if rationale is sufficiently detailed"""
        length = len(q.rationale)

        if length < 30:
            return QualityIssue(
                check_name="Rationale Length",
                severity=CheckSeverity.FAIL,
                message=f"Rationale too short ({length} chars)",
                details="Rationale should explain why this question matters (30+ chars)"
            )
        elif length < 50:
            return QualityIssue(
                check_name="Rationale Length",
                severity=CheckSeverity.WARNING,
                message=f"Rationale is brief ({length} chars)",
                details="More detailed rationale improves question value (50+ chars recommended)"
            )
        return None

    def _check_rationale_context(self, q: QuestionItem) -> QualityIssue | None:
        """Check if rationale mentions resume/target/domain context"""
        rationale_lower = q.rationale.lower()

        # Keywords that indicate contextual relevance
        context_keywords = [
            "简历", "resume", "经历", "experience", "项目", "project",
            "岗位", "position", "目标", "target", "申请", "application",
            "领域", "domain", "方向", "direction", "专业", "major",
            "技能", "skill", "背景", "background", "工作", "work",
            "研究", "research", "论文", "paper", "实习", "intern"
        ]

        has_context = any(keyword in rationale_lower for keyword in context_keywords)

        if not has_context:
            return QualityIssue(
                check_name="Rationale Context",
                severity=CheckSeverity.WARNING,
                message="Rationale lacks specific context",
                details="Rationale should reference resume content, target position, or domain"
            )
        return None

    def _check_baseline_answer_structure(self, q: QuestionItem) -> QualityIssue | None:
        """Check if baseline answer has clear structure"""
        answer = q.baseline_answer

        # Check for structural indicators
        has_paragraphs = answer.count('\n\n') >= 1 or answer.count('\n') >= 2
        has_bullets = '•' in answer or '-' in answer or any(f"{i}." in answer for i in range(1, 10))
        has_sections = '**' in answer or '#' in answer or '：' in answer

        structure_score = sum([has_paragraphs, has_bullets, has_sections])

        if structure_score == 0:
            return QualityIssue(
                check_name="Answer Structure",
                severity=CheckSeverity.WARNING,
                message="Baseline answer lacks clear structure",
                details="Consider adding paragraphs, bullet points, or sections"
            )
        return None

    def _check_baseline_answer_depth(self, q: QuestionItem) -> QualityIssue | None:
        """Check if baseline answer is detailed enough"""
        length = len(q.baseline_answer)

        if length < 50:
            return QualityIssue(
                check_name="Answer Depth",
                severity=CheckSeverity.FAIL,
                message=f"Baseline answer too short ({length} chars)",
                details="Answer should provide substantial guidance (50+ chars minimum)"
            )
        elif length < 100:
            return QualityIssue(
                check_name="Answer Depth",
                severity=CheckSeverity.WARNING,
                message=f"Baseline answer is brief ({length} chars)",
                details="More detailed answers help users prepare better (200+ chars recommended)"
            )
        return None

    def _check_support_notes_specificity(self, q: QuestionItem) -> QualityIssue | None:
        """Check if support notes provide specific knowledge points"""
        notes = q.support_notes
        notes_lower = notes.lower()

        # Check for specific technical terms, concepts, or resources
        specific_indicators = [
            # Technical terms
            any(term in notes for term in ['API', 'HTTP', 'SQL', 'CPU', 'GPU', 'RAM']),
            # Algorithms/concepts
            any(term in notes_lower for term in ['algorithm', '算法', 'pattern', '模式', 'theory', '理论']),
            # Resources
            any(term in notes_lower for term in ['paper', '论文', 'book', '书', 'doc', '文档', 'article', '文章']),
            # Specific numbers or versions
            any(char.isdigit() for char in notes),
        ]

        if not any(specific_indicators):
            return QualityIssue(
                check_name="Support Notes Specificity",
                severity=CheckSeverity.WARNING,
                message="Support notes lack specific knowledge points",
                details="Include specific concepts, papers, tools, or resources"
            )
        return None

    def _check_support_notes_length(self, q: QuestionItem) -> QualityIssue | None:
        """Check if support notes are detailed enough"""
        length = len(q.support_notes)

        if length < 20:
            return QualityIssue(
                check_name="Support Notes Length",
                severity=CheckSeverity.FAIL,
                message=f"Support notes too short ({length} chars)",
                details="Support notes should provide learning resources (20+ chars)"
            )
        elif length < 50:
            return QualityIssue(
                check_name="Support Notes Length",
                severity=CheckSeverity.WARNING,
                message=f"Support notes are brief ({length} chars)",
                details="More detailed notes improve learning value (100+ chars recommended)"
            )
        return None

    def _check_prompt_template_validity(self, q: QuestionItem) -> QualityIssue | None:
        """Check if prompt template contains placeholders"""
        template = q.prompt_template

        # Check for common placeholders
        placeholders = ['{', '{{', '[', '【']
        has_placeholder = any(ph in template for ph in placeholders)

        # Check if template is different from question (should be more detailed)
        is_different = template != q.question and len(template) > len(q.question)

        if not has_placeholder:
            return QualityIssue(
                check_name="Prompt Template",
                severity=CheckSeverity.WARNING,
                message="Prompt template lacks placeholders",
                details="Template should contain placeholders like {your_experience} for practice"
            )

        if not is_different:
            return QualityIssue(
                check_name="Prompt Template",
                severity=CheckSeverity.WARNING,
                message="Prompt template is too similar to question",
                details="Template should expand the question with context and placeholders"
            )

        return None


class QualityEvaluationRunner:
    """Orchestrates quality evaluation on test cases"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.checker = QuestionQualityChecker(verbose=verbose)

    def load_test_case(self, case_name: str) -> Tuple[str, Dict]:
        """Load resume and config for a test case"""
        quality_cases_dir = project_root / "examples" / "quality_cases"

        resume_path = quality_cases_dir / f"resume_{case_name}.txt"
        config_path = quality_cases_dir / f"config_{case_name}.json"

        if not resume_path.exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        return resume_text, config_data

    def generate_report(self, case_name: str) -> Report:
        """Generate report for a test case"""
        print(f"\n{'='*70}")
        print(f"📊 Generating Report for: {case_name}")
        print(f"{'='*70}")

        resume_text, config_data = self.load_test_case(case_name)

        user_config = UserConfig(
            mode=config_data["mode"],
            target_desc=config_data["target_desc"],
            domain=config_data.get("domain"),
            resume_text=resume_text,
            enable_external_info=config_data.get("enable_external_info", False)
        )

        print(f"  Mode: {user_config.mode}")
        print(f"  Target: {user_config.target_desc}")
        print(f"  Domain: {user_config.domain}")
        print(f"  Resume length: {len(resume_text)} chars")
        print(f"\n  Calling LLM to generate report...")
        print(f"  (This may take 30-60 seconds)")

        generator = ReportGenerator()
        report = generator.generate_report(user_config)

        print(f"  ✓ Report generated successfully!")
        print(f"  ✓ Questions: {len(report.questions)}")
        print(f"  ✓ Mode: {report.mode}")

        return report

    def evaluate_report(self, report: Report, case_name: str) -> List[QuestionQualityReport]:
        """Evaluate all questions in a report"""
        print(f"\n{'='*70}")
        print(f"🔍 Quality Evaluation: {case_name}")
        print(f"{'='*70}")

        question_reports = []

        for question in report.questions:
            quality_report = self.checker.check_question(question)
            question_reports.append(quality_report)

        return question_reports

    def print_results(self, question_reports: List[QuestionQualityReport], case_name: str):
        """Print human-readable evaluation results"""
        print(f"\n{'='*70}")
        print(f"📋 Quality Report Summary: {case_name}")
        print(f"{'='*70}\n")

        total_questions = len(question_reports)
        total_issues = sum(len(qr.issues) for qr in question_reports)
        total_failures = sum(1 for qr in question_reports if qr.has_failures)
        total_warnings = sum(1 for qr in question_reports if qr.has_warnings and not qr.has_failures)
        total_passed = total_questions - total_failures - total_warnings

        # Overall statistics
        print(f"📊 Overall Statistics:")
        print(f"  Total Questions: {total_questions}")
        print(f"  ✓ Passed: {total_passed} ({total_passed/total_questions*100:.1f}%)")
        print(f"  ⚠ Warnings: {total_warnings} ({total_warnings/total_questions*100:.1f}%)")
        print(f"  ✗ Failures: {total_failures} ({total_failures/total_questions*100:.1f}%)")
        print(f"  Total Issues: {total_issues}")
        print()

        # Per-question details
        for qr in question_reports:
            status_icon = "✓" if not qr.has_failures and not qr.has_warnings else \
                         "⚠" if qr.has_warnings else "✗"

            print(f"{status_icon} Question {qr.question_id}: {qr.question_text[:60]}...")
            print(f"  Pass Rate: {qr.pass_rate:.0f}% ({qr.passed_checks}/{qr.total_checks} checks)")

            if qr.issues:
                for issue in qr.issues:
                    print(f"    {issue.severity.value} {issue.check_name}: {issue.message}")
                    if self.verbose and issue.details:
                        print(f"       → {issue.details}")
            else:
                print(f"    All checks passed!")
            print()

        # Quality recommendations
        print(f"{'='*70}")
        print(f"💡 Recommendations:")
        print(f"{'='*70}\n")

        if total_failures > 0:
            print(f"⚠️  CRITICAL: {total_failures} questions have FAIL-level issues.")
            print(f"   → Review and fix these questions before production use.\n")

        if total_warnings > 0:
            print(f"⚠️  {total_warnings} questions have warnings.")
            print(f"   → Consider improving these for better quality.\n")

        if total_passed == total_questions:
            print(f"✅ Excellent! All questions passed quality checks!")
            print(f"   → Questions are ready for production use.\n")

        # Calculate overall quality score
        avg_pass_rate = sum(qr.pass_rate for qr in question_reports) / len(question_reports)
        print(f"📈 Overall Quality Score: {avg_pass_rate:.1f}%")

        if avg_pass_rate >= 90:
            print(f"   Grade: A (Excellent)")
        elif avg_pass_rate >= 80:
            print(f"   Grade: B (Good)")
        elif avg_pass_rate >= 70:
            print(f"   Grade: C (Acceptable)")
        else:
            print(f"   Grade: D (Needs Improvement)")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate the quality of GrillRadar generated questions"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output including recommendations"
    )
    parser.add_argument(
        "--case", "-c",
        type=str,
        default="all",
        help="Specific test case to run (e.g., 'job_backend', 'grad_nlp'). Default: run all cases"
    )
    parser.add_argument(
        "--skip-generation", "-s",
        action="store_true",
        help="Skip report generation (requires cached reports)"
    )

    args = parser.parse_args()

    # Banner
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        🔍 GrillRadar Question Quality Evaluation Tool            ║
║                                                                  ║
║  Evaluates generated questions for clarity, depth, and value    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    runner = QualityEvaluationRunner(verbose=args.verbose)

    # Determine which cases to run
    available_cases = [
        "job_backend",
        "job_frontend",
        "grad_nlp",
    ]

    if args.case == "all":
        cases_to_run = available_cases
    elif args.case in available_cases:
        cases_to_run = [args.case]
    else:
        print(f"❌ Error: Unknown case '{args.case}'")
        print(f"   Available cases: {', '.join(available_cases)}")
        sys.exit(1)

    print(f"📦 Test cases to evaluate: {', '.join(cases_to_run)}")
    print(f"🔧 Verbose mode: {'ON' if args.verbose else 'OFF'}")
    print()

    # Run evaluation for each case
    all_results = {}

    for case_name in cases_to_run:
        try:
            # Generate report
            if not args.skip_generation:
                report = runner.generate_report(case_name)
            else:
                print(f"⚠️  Skipping generation for {case_name} (not implemented)")
                continue

            # Evaluate questions
            question_reports = runner.evaluate_report(report, case_name)

            # Print results
            runner.print_results(question_reports, case_name)

            all_results[case_name] = question_reports

        except Exception as e:
            print(f"\n❌ Error evaluating {case_name}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            continue

    # Final summary for multiple cases
    if len(cases_to_run) > 1:
        print(f"\n{'='*70}")
        print(f"🏆 Multi-Case Summary")
        print(f"{'='*70}\n")

        for case_name, question_reports in all_results.items():
            avg_pass_rate = sum(qr.pass_rate for qr in question_reports) / len(question_reports)
            total_failures = sum(1 for qr in question_reports if qr.has_failures)
            total_warnings = sum(1 for qr in question_reports if qr.has_warnings and not qr.has_failures)

            status = "✓" if total_failures == 0 else "✗"
            print(f"{status} {case_name:20s} - Quality: {avg_pass_rate:5.1f}% | "
                  f"Warnings: {total_warnings:2d} | Failures: {total_failures:2d}")

        print()

    print("✅ Evaluation complete!")


if __name__ == "__main__":
    main()
