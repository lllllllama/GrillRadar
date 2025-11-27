import pytest
from app.models.report import Report, ReportMeta
from app.models.question_item import QuestionItem
from pydantic import ValidationError

class TestReportLimits:
    def create_dummy_questions(self, count):
        questions = []
        for i in range(1, count + 1):
            questions.append(QuestionItem(
                id=i,
                view_role="技术面试官",
                tag=f"标签{i}",
                question=f"问题{i}" * 5,
                rationale=f"理由{i}" * 5,
                baseline_answer=f"答案{i}" * 10,
                support_notes=f"材料{i}" * 5,
                prompt_template=f"模板{i}" * 10
            ))
        return questions

    def create_report(self, num_questions):
        questions = self.create_dummy_questions(num_questions)
        return Report(
            summary="总结" * 30,
            mode="job",
            target_desc="岗位",
            highlights="亮点" * 20,
            risks="风险" * 20,
            questions=questions,
            meta=ReportMeta(
                generated_at="2025-11-17T10:00:00Z",
                model="claude-sonnet-4",
                num_questions=num_questions
            )
        )

    def test_report_with_50_questions(self):
        """Test that a report with 50 questions is allowed (Job mode max)"""
        try:
            report = self.create_report(50)
            assert len(report.questions) == 50
        except ValidationError as e:
            pytest.fail(f"Should allow 50 questions: {e}")

    def test_report_with_10_questions(self):
        """Test that a report with 10 questions is allowed (Fix for existing tests)"""
        try:
            report = self.create_report(10)
            assert len(report.questions) == 10
        except ValidationError as e:
            pytest.fail(f"Should allow 10 questions: {e}")

    def test_report_with_51_questions(self):
        """Test that a report with 51 questions is NOT allowed"""
        with pytest.raises(ValidationError) as excinfo:
            self.create_report(51)
        assert "List should have at most" in str(excinfo.value)
