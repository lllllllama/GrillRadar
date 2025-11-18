"""
Evaluation Module

Quality evaluation and regression testing toolkit for GrillRadar reports.
"""
from app.eval.report_quality import (
    ReportQualitySummary,
    evaluate_report,
    compare_reports,
)

__all__ = [
    "ReportQualitySummary",
    "evaluate_report",
    "compare_reports",
]
