"""
Report Quality Evaluation

Lightweight quality metrics and comparison tools for GrillRadar reports.
"""
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
from dataclasses import dataclass, asdict
import difflib

from app.models.report import Report
from app.models.question_item import QuestionItem


@dataclass
class ReportQualitySummary:
    """
    Quality metrics summary for a generated report

    Attributes:
        num_questions: Total number of questions in report
        unique_question_ratio: Ratio of unique questions (detects duplication)
        num_missing_rationale: Count of questions without rationale
        num_missing_baseline: Count of questions without baseline answer
        num_missing_support: Count of questions without support notes
        avg_question_length: Average character length of questions
        avg_rationale_length: Average character length of rationales
        avg_baseline_length: Average character length of baseline answers
        tag_distribution: Distribution of question tags
        role_distribution: Distribution of view roles
        dimension_distribution: Distribution of dimensions (if available)
        difficulty_distribution: Distribution of difficulty levels (if available)
        quality_score: Overall quality score (0-100)
        issues: List of quality issues detected
    """
    num_questions: int
    unique_question_ratio: float
    num_missing_rationale: int
    num_missing_baseline: int
    num_missing_support: int
    avg_question_length: float
    avg_rationale_length: float
    avg_baseline_length: float
    tag_distribution: Dict[str, int]
    role_distribution: Dict[str, int]
    dimension_distribution: Dict[str, int]
    difficulty_distribution: Dict[str, int]
    quality_score: float
    issues: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


def evaluate_report(report: Report) -> ReportQualitySummary:
    """
    Evaluate quality metrics for a generated report

    Args:
        report: The Report object to evaluate

    Returns:
        ReportQualitySummary with computed metrics
    """
    questions = report.questions
    num_questions = len(questions)

    if num_questions == 0:
        return ReportQualitySummary(
            num_questions=0,
            unique_question_ratio=0.0,
            num_missing_rationale=0,
            num_missing_baseline=0,
            num_missing_support=0,
            avg_question_length=0.0,
            avg_rationale_length=0.0,
            avg_baseline_length=0.0,
            tag_distribution={},
            role_distribution={},
            dimension_distribution={},
            difficulty_distribution={},
            quality_score=0.0,
            issues=["No questions generated"]
        )

    # Compute uniqueness ratio
    unique_ratio = _compute_uniqueness_ratio(questions)

    # Count missing fields
    num_missing_rationale = sum(1 for q in questions if not q.rationale or len(q.rationale.strip()) < 10)
    num_missing_baseline = sum(1 for q in questions if not q.baseline_answer or len(q.baseline_answer.strip()) < 10)
    num_missing_support = sum(1 for q in questions if not q.support_notes or len(q.support_notes.strip()) < 10)

    # Compute average lengths
    avg_question_length = sum(len(q.question) for q in questions) / num_questions
    avg_rationale_length = sum(len(q.rationale) for q in questions if q.rationale) / max(1, num_questions - num_missing_rationale)
    avg_baseline_length = sum(len(q.baseline_answer) for q in questions if q.baseline_answer) / max(1, num_questions - num_missing_baseline)

    # Distribution analysis
    tag_distribution = Counter(q.tag for q in questions if q.tag)
    role_distribution = Counter(q.view_role for q in questions if q.view_role)

    # Multi-agent enhanced fields (optional)
    dimension_distribution = Counter(
        getattr(q, 'dimension', None) for q in questions
        if hasattr(q, 'dimension') and getattr(q, 'dimension', None)
    )
    difficulty_distribution = Counter(
        getattr(q, 'difficulty', None) for q in questions
        if hasattr(q, 'difficulty') and getattr(q, 'difficulty', None)
    )

    # Detect quality issues
    issues = _detect_quality_issues(
        num_questions=num_questions,
        unique_ratio=unique_ratio,
        num_missing_rationale=num_missing_rationale,
        num_missing_baseline=num_missing_baseline,
        avg_question_length=avg_question_length,
        avg_baseline_length=avg_baseline_length,
        tag_distribution=tag_distribution,
        role_distribution=role_distribution
    )

    # Compute overall quality score (0-100)
    quality_score = _compute_quality_score(
        num_questions=num_questions,
        unique_ratio=unique_ratio,
        num_missing_rationale=num_missing_rationale,
        num_missing_baseline=num_missing_baseline,
        avg_question_length=avg_question_length,
        avg_baseline_length=avg_baseline_length
    )

    return ReportQualitySummary(
        num_questions=num_questions,
        unique_question_ratio=unique_ratio,
        num_missing_rationale=num_missing_rationale,
        num_missing_baseline=num_missing_baseline,
        num_missing_support=num_missing_support,
        avg_question_length=avg_question_length,
        avg_rationale_length=avg_rationale_length,
        avg_baseline_length=avg_baseline_length,
        tag_distribution=dict(tag_distribution),
        role_distribution=dict(role_distribution),
        dimension_distribution=dict(dimension_distribution),
        difficulty_distribution=dict(difficulty_distribution),
        quality_score=quality_score,
        issues=issues
    )


def _compute_uniqueness_ratio(questions: List[QuestionItem]) -> float:
    """
    Compute ratio of unique questions to detect duplication

    Uses fuzzy string matching to detect semantically similar questions.

    Args:
        questions: List of QuestionItem objects

    Returns:
        Ratio from 0.0 to 1.0 (1.0 = all unique)
    """
    if len(questions) <= 1:
        return 1.0

    question_texts = [q.question.lower().strip() for q in questions]

    # Count how many questions are truly unique (not similar to any other)
    unique_count = 0

    for i, q1 in enumerate(question_texts):
        is_unique = True
        for j, q2 in enumerate(question_texts):
            if i != j:
                # Use sequence matcher for fuzzy comparison
                similarity = difflib.SequenceMatcher(None, q1, q2).ratio()
                if similarity > 0.75:  # >75% similar = duplicate
                    is_unique = False
                    break
        if is_unique:
            unique_count += 1

    return unique_count / len(questions)


def _detect_quality_issues(
    num_questions: int,
    unique_ratio: float,
    num_missing_rationale: int,
    num_missing_baseline: int,
    avg_question_length: float,
    avg_baseline_length: float,
    tag_distribution: Counter,
    role_distribution: Counter
) -> List[str]:
    """
    Detect quality issues in the report

    Returns:
        List of issue descriptions
    """
    issues = []

    # Question count issues
    if num_questions < 8:
        issues.append(f"Too few questions ({num_questions}). Target: 10-15.")
    elif num_questions > 20:
        issues.append(f"Too many questions ({num_questions}). Target: 10-15. May overwhelm candidate.")

    # Uniqueness issues
    if unique_ratio < 0.85:
        issues.append(f"Low uniqueness ratio ({unique_ratio:.2f}). Possible duplicate questions.")

    # Missing content issues
    if num_missing_rationale > 2:
        issues.append(f"{num_missing_rationale} questions missing rationale.")
    if num_missing_baseline > 2:
        issues.append(f"{num_missing_baseline} questions missing baseline answer.")

    # Length issues
    if avg_question_length < 20:
        issues.append(f"Questions too short (avg {avg_question_length:.0f} chars). May be too vague.")
    elif avg_question_length > 150:
        issues.append(f"Questions too long (avg {avg_question_length:.0f} chars). May be too wordy.")

    if avg_baseline_length < 50:
        issues.append(f"Baseline answers too short (avg {avg_baseline_length:.0f} chars). Insufficient guidance.")
    elif avg_baseline_length > 800:
        issues.append(f"Baseline answers too long (avg {avg_baseline_length:.0f} chars). Too verbose.")

    # Diversity issues
    if len(role_distribution) < 2:
        issues.append("Low role diversity. All questions from same perspective.")

    if tag_distribution and len(tag_distribution) < 3:
        issues.append(f"Low tag diversity ({len(tag_distribution)} unique tags). Limited topic coverage.")

    return issues


def _compute_quality_score(
    num_questions: int,
    unique_ratio: float,
    num_missing_rationale: int,
    num_missing_baseline: int,
    avg_question_length: float,
    avg_baseline_length: float
) -> float:
    """
    Compute overall quality score (0-100)

    Weighted scoring:
    - Question count: 20 points (10-15 ideal)
    - Uniqueness: 30 points (>0.9 ideal)
    - Completeness: 20 points (no missing fields)
    - Question length: 15 points (30-100 chars ideal)
    - Baseline length: 15 points (100-500 chars ideal)

    Returns:
        Score from 0 to 100
    """
    score = 0.0

    # Question count score (20 points)
    if 10 <= num_questions <= 15:
        score += 20
    elif 8 <= num_questions <= 20:
        score += 15
    elif num_questions > 0:
        score += 5

    # Uniqueness score (30 points)
    if unique_ratio >= 0.95:
        score += 30
    elif unique_ratio >= 0.90:
        score += 25
    elif unique_ratio >= 0.85:
        score += 20
    elif unique_ratio >= 0.80:
        score += 10

    # Completeness score (20 points)
    completeness_penalty = (num_missing_rationale + num_missing_baseline) * 2
    completeness_score = max(0, 20 - completeness_penalty)
    score += completeness_score

    # Question length score (15 points)
    if 30 <= avg_question_length <= 100:
        score += 15
    elif 20 <= avg_question_length <= 150:
        score += 10
    elif avg_question_length > 0:
        score += 5

    # Baseline answer length score (15 points)
    if 100 <= avg_baseline_length <= 500:
        score += 15
    elif 50 <= avg_baseline_length <= 800:
        score += 10
    elif avg_baseline_length > 0:
        score += 5

    return min(100.0, score)


@dataclass
class ReportComparison:
    """
    Comparison result between two reports

    Attributes:
        baseline_summary: Quality summary for baseline report
        candidate_summary: Quality summary for candidate report
        question_count_delta: Change in question count
        uniqueness_delta: Change in uniqueness ratio
        quality_score_delta: Change in overall quality score
        common_questions: Number of questions present in both reports
        new_questions: Number of questions only in candidate
        removed_questions: Number of questions only in baseline
        tag_overlap: Jaccard similarity of tag sets
        improvements: List of detected improvements
        regressions: List of detected regressions
    """
    baseline_summary: ReportQualitySummary
    candidate_summary: ReportQualitySummary
    question_count_delta: int
    uniqueness_delta: float
    quality_score_delta: float
    common_questions: int
    new_questions: int
    removed_questions: int
    tag_overlap: float
    improvements: List[str]
    regressions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "baseline_summary": self.baseline_summary.to_dict(),
            "candidate_summary": self.candidate_summary.to_dict(),
            "question_count_delta": self.question_count_delta,
            "uniqueness_delta": self.uniqueness_delta,
            "quality_score_delta": self.quality_score_delta,
            "common_questions": self.common_questions,
            "new_questions": self.new_questions,
            "removed_questions": self.removed_questions,
            "tag_overlap": self.tag_overlap,
            "improvements": self.improvements,
            "regressions": self.regressions
        }


def compare_reports(baseline: Report, candidate: Report) -> ReportComparison:
    """
    Compare two reports to detect improvements or regressions

    Args:
        baseline: The baseline (old) report
        candidate: The candidate (new) report

    Returns:
        ReportComparison with detected changes
    """
    baseline_summary = evaluate_report(baseline)
    candidate_summary = evaluate_report(candidate)

    # Compute deltas
    question_count_delta = candidate_summary.num_questions - baseline_summary.num_questions
    uniqueness_delta = candidate_summary.unique_question_ratio - baseline_summary.unique_question_ratio
    quality_score_delta = candidate_summary.quality_score - baseline_summary.quality_score

    # Compute question overlap
    baseline_questions = {q.question.lower().strip() for q in baseline.questions}
    candidate_questions = {q.question.lower().strip() for q in candidate.questions}

    common_questions = len(baseline_questions & candidate_questions)
    new_questions = len(candidate_questions - baseline_questions)
    removed_questions = len(baseline_questions - candidate_questions)

    # Compute tag overlap (Jaccard similarity)
    baseline_tags = set(baseline_summary.tag_distribution.keys())
    candidate_tags = set(candidate_summary.tag_distribution.keys())
    tag_overlap = (
        len(baseline_tags & candidate_tags) / len(baseline_tags | candidate_tags)
        if baseline_tags or candidate_tags else 0.0
    )

    # Detect improvements and regressions
    improvements, regressions = _detect_changes(
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
        question_count_delta=question_count_delta,
        uniqueness_delta=uniqueness_delta,
        quality_score_delta=quality_score_delta
    )

    return ReportComparison(
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
        question_count_delta=question_count_delta,
        uniqueness_delta=uniqueness_delta,
        quality_score_delta=quality_score_delta,
        common_questions=common_questions,
        new_questions=new_questions,
        removed_questions=removed_questions,
        tag_overlap=tag_overlap,
        improvements=improvements,
        regressions=regressions
    )


def _detect_changes(
    baseline_summary: ReportQualitySummary,
    candidate_summary: ReportQualitySummary,
    question_count_delta: int,
    uniqueness_delta: float,
    quality_score_delta: float
) -> Tuple[List[str], List[str]]:
    """
    Detect improvements and regressions between reports

    Returns:
        Tuple of (improvements, regressions)
    """
    improvements = []
    regressions = []

    # Quality score change
    if quality_score_delta >= 5:
        improvements.append(f"Overall quality improved by {quality_score_delta:.1f} points")
    elif quality_score_delta <= -5:
        regressions.append(f"Overall quality decreased by {abs(quality_score_delta):.1f} points")

    # Uniqueness change
    if uniqueness_delta >= 0.05:
        improvements.append(f"Uniqueness improved by {uniqueness_delta:.2f} (less duplication)")
    elif uniqueness_delta <= -0.05:
        regressions.append(f"Uniqueness decreased by {abs(uniqueness_delta):.2f} (more duplication)")

    # Question count change
    if question_count_delta > 0 and candidate_summary.num_questions <= 15:
        improvements.append(f"Added {question_count_delta} more questions")
    elif question_count_delta < 0 and baseline_summary.num_questions > 15:
        improvements.append(f"Removed {abs(question_count_delta)} questions (more focused)")
    elif question_count_delta > 5:
        regressions.append(f"Added too many questions (+{question_count_delta})")
    elif question_count_delta < -5:
        regressions.append(f"Removed too many questions ({question_count_delta})")

    # Missing content change
    rationale_delta = candidate_summary.num_missing_rationale - baseline_summary.num_missing_rationale
    if rationale_delta < 0:
        improvements.append(f"Fewer missing rationales ({abs(rationale_delta)} improvement)")
    elif rationale_delta > 0:
        regressions.append(f"More missing rationales (+{rationale_delta})")

    baseline_delta = candidate_summary.num_missing_baseline - baseline_summary.num_missing_baseline
    if baseline_delta < 0:
        improvements.append(f"Fewer missing baseline answers ({abs(baseline_delta)} improvement)")
    elif baseline_delta > 0:
        regressions.append(f"More missing baseline answers (+{baseline_delta})")

    # Length changes
    question_length_delta = candidate_summary.avg_question_length - baseline_summary.avg_question_length
    if 30 <= candidate_summary.avg_question_length <= 100 and (
        baseline_summary.avg_question_length < 30 or baseline_summary.avg_question_length > 100
    ):
        improvements.append("Question length now in ideal range (30-100 chars)")
    elif abs(question_length_delta) > 30:
        if candidate_summary.avg_question_length < 30:
            regressions.append(f"Questions too short (avg {candidate_summary.avg_question_length:.0f} chars)")
        elif candidate_summary.avg_question_length > 100:
            regressions.append(f"Questions too long (avg {candidate_summary.avg_question_length:.0f} chars)")

    return improvements, regressions


def format_quality_summary(summary: ReportQualitySummary, verbose: bool = True) -> str:
    """
    Format quality summary as human-readable text with visual indicators

    Args:
        summary: ReportQualitySummary to format
        verbose: Whether to include detailed distributions

    Returns:
        Formatted string with emoji indicators
    """
    lines = []
    lines.append("=" * 60)
    lines.append("📊 REPORT QUALITY EVALUATION")
    lines.append("=" * 60)
    lines.append("")

    # Overall score
    score_emoji = "✅" if summary.quality_score >= 80 else "⚠️" if summary.quality_score >= 60 else "❌"
    lines.append(f"{score_emoji} Overall Quality Score: {summary.quality_score:.1f}/100")
    lines.append("")

    # Core metrics
    lines.append("Core Metrics:")
    lines.append(f"  • Question Count: {_format_metric(summary.num_questions, 10, 15, 8, 20)}")
    lines.append(f"  • Uniqueness Ratio: {_format_metric(summary.unique_question_ratio, 0.90, 1.0, 0.85, 0.80)}")
    lines.append(f"  • Missing Rationales: {_format_count_metric(summary.num_missing_rationale, 0, 2)}")
    lines.append(f"  • Missing Baselines: {_format_count_metric(summary.num_missing_baseline, 0, 2)}")
    lines.append("")

    # Length metrics
    lines.append("Length Metrics:")
    lines.append(f"  • Avg Question Length: {_format_metric(summary.avg_question_length, 30, 100, 20, 150)} chars")
    lines.append(f"  • Avg Rationale Length: {summary.avg_rationale_length:.0f} chars")
    lines.append(f"  • Avg Baseline Length: {_format_metric(summary.avg_baseline_length, 100, 500, 50, 800)} chars")
    lines.append("")

    if verbose:
        # Distribution metrics
        if summary.tag_distribution:
            lines.append(f"Tag Distribution ({len(summary.tag_distribution)} unique):")
            for tag, count in sorted(summary.tag_distribution.items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"  • {tag}: {count}")
            if len(summary.tag_distribution) > 5:
                lines.append(f"  • ... and {len(summary.tag_distribution) - 5} more")
            lines.append("")

        if summary.role_distribution:
            lines.append(f"Role Distribution ({len(summary.role_distribution)} unique):")
            for role, count in sorted(summary.role_distribution.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  • {role}: {count}")
            lines.append("")

        if summary.dimension_distribution:
            lines.append(f"Dimension Distribution:")
            for dim, count in sorted(summary.dimension_distribution.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  • {dim}: {count}")
            lines.append("")

        if summary.difficulty_distribution:
            lines.append(f"Difficulty Distribution:")
            for diff, count in sorted(summary.difficulty_distribution.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  • {diff}: {count}")
            lines.append("")

    # Issues
    if summary.issues:
        lines.append("⚠️  Quality Issues:")
        for issue in summary.issues:
            lines.append(f"  • {issue}")
        lines.append("")
    else:
        lines.append("✅ No quality issues detected!")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)


def _format_metric(value: float, ideal_min: float, ideal_max: float, warn_min: float, warn_max: float) -> str:
    """Format metric value with visual indicator"""
    if ideal_min <= value <= ideal_max:
        return f"✅ {value:.2f}"
    elif warn_min <= value <= warn_max:
        return f"⚠️  {value:.2f}"
    else:
        return f"❌ {value:.2f}"


def _format_count_metric(value: int, ideal: int, warn_threshold: int) -> str:
    """Format count metric with visual indicator"""
    if value == ideal:
        return f"✅ {value}"
    elif value <= warn_threshold:
        return f"⚠️  {value}"
    else:
        return f"❌ {value}"


def format_comparison(comparison: ReportComparison, baseline_name: str = "Baseline", candidate_name: str = "Candidate") -> str:
    """
    Format report comparison as human-readable text

    Args:
        comparison: ReportComparison result
        baseline_name: Name for baseline report
        candidate_name: Name for candidate report

    Returns:
        Formatted comparison string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("🔍 REPORT COMPARISON")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Baseline: {baseline_name}")
    lines.append(f"Candidate: {candidate_name}")
    lines.append("")

    # Score comparison
    score_emoji = "📈" if comparison.quality_score_delta > 0 else "📉" if comparison.quality_score_delta < 0 else "➡️"
    lines.append(f"{score_emoji} Quality Score: {comparison.baseline_summary.quality_score:.1f} → {comparison.candidate_summary.quality_score:.1f} ({comparison.quality_score_delta:+.1f})")
    lines.append("")

    # Key metrics comparison
    lines.append("Key Metrics:")
    lines.append(f"  • Questions: {comparison.baseline_summary.num_questions} → {comparison.candidate_summary.num_questions} ({comparison.question_count_delta:+d})")
    lines.append(f"  • Uniqueness: {comparison.baseline_summary.unique_question_ratio:.2f} → {comparison.candidate_summary.unique_question_ratio:.2f} ({comparison.uniqueness_delta:+.2f})")
    lines.append(f"  • Missing Rationales: {comparison.baseline_summary.num_missing_rationale} → {comparison.candidate_summary.num_missing_rationale}")
    lines.append(f"  • Missing Baselines: {comparison.baseline_summary.num_missing_baseline} → {comparison.candidate_summary.num_missing_baseline}")
    lines.append("")

    # Question overlap
    lines.append("Question Overlap:")
    lines.append(f"  • Common questions: {comparison.common_questions}")
    lines.append(f"  • New questions: {comparison.new_questions}")
    lines.append(f"  • Removed questions: {comparison.removed_questions}")
    lines.append(f"  • Tag overlap: {comparison.tag_overlap:.2f}")
    lines.append("")

    # Improvements
    if comparison.improvements:
        lines.append("✅ Improvements:")
        for improvement in comparison.improvements:
            lines.append(f"  • {improvement}")
        lines.append("")

    # Regressions
    if comparison.regressions:
        lines.append("❌ Regressions:")
        for regression in comparison.regressions:
            lines.append(f"  • {regression}")
        lines.append("")

    if not comparison.improvements and not comparison.regressions:
        lines.append("➡️  No significant changes detected")
        lines.append("")

    lines.append("=" * 60)

    return "\n".join(lines)
