"""Tests for markdown utility"""

import pytest
from app.utils.markdown import report_to_markdown
from app.models.report import Report, ReportMeta
from app.models.question_item import QuestionItem


class TestMarkdownConversion:
    @pytest.fixture
    def sample_report(self):
        """Sample report for testing"""
        # Create 10 questions (minimum required by Report model)
        questions = []
        for i in range(1, 11):
            questions.append(QuestionItem(
                id=i,
                view_role="技术面试官" if i % 2 == 0 else "招聘经理",
                tag=f"标签{i}",
                question=f"这是测试问题{i}的内容" * 3,
                rationale=f"这是测试问题{i}的提问理由" * 5,
                baseline_answer=f"这是测试问题{i}的基准答案" * 10,
                support_notes=f"这是测试问题{i}的支持材料" * 5,
                prompt_template=f"这是测试问题{i}的练习提示词" * 10
            ))

        return Report(
            summary="候选人具有3年后端开发经验，在分布式系统和微服务架构方面有实践经验。技术栈涵盖Java、Go、MySQL、Redis等主流技术。整体来看，候选人技术基础扎实，但在系统设计的理论深度方面还有提升空间。" * 2,
            mode="job",
            target_desc="字节跳动后端开发工程师",
            highlights="1. 有丰富的分布式系统实践经验\n2. 熟悉主流后端技术栈\n3. 有高并发系统的设计和优化经验\n4. 具备良好的问题排查和解决能力",
            risks="1. 算法和数据结构的理论深度需要加强\n2. 系统设计的方法论不够系统\n3. 对新技术的学习和跟进可以更主动\n4. 需要准备更多的项目细节和数据",
            questions=questions,
            meta=ReportMeta(
                generated_at="2025-11-17T10:00:00Z",
                model="claude-sonnet-4",
                config_version="v1.0",
                num_questions=10
            )
        )

    def test_report_to_markdown_structure(self, sample_report):
        """Test that markdown output has correct structure"""
        markdown = report_to_markdown(sample_report)

        # Check main sections exist
        assert "# GrillRadar 面试准备报告" in markdown
        assert "## 📊 总体评估" in markdown
        assert "## ⭐ 候选人亮点" in markdown
        assert "## ⚠️ 关键风险点" in markdown
        assert "## 📝 问题清单" in markdown
        assert "## 📌 使用说明" in markdown

    def test_report_metadata_in_markdown(self, sample_report):
        """Test that report metadata appears in markdown"""
        markdown = report_to_markdown(sample_report)

        assert "字节跳动后端开发工程师" in markdown
        assert "2025-11-17T10:00:00Z" in markdown
        assert "job" in markdown
        assert "10" in markdown  # num_questions

    def test_questions_in_markdown(self, sample_report):
        """Test that all questions appear in markdown"""
        markdown = report_to_markdown(sample_report)

        # Check question 1
        assert "Q1" in markdown
        assert "标签1" in markdown
        assert "招聘经理" in markdown
        assert "测试问题1" in markdown

        # Check question 2
        assert "Q2" in markdown
        assert "标签2" in markdown
        assert "技术面试官" in markdown
        assert "测试问题2" in markdown

        # Check all 10 questions are present
        for i in range(1, 11):
            assert f"Q{i}" in markdown

    def test_question_sections_in_markdown(self, sample_report):
        """Test that question sections are formatted correctly"""
        markdown = report_to_markdown(sample_report)

        # Each question should have these sections
        assert "**问题：**" in markdown
        assert "**为什么问这个问题：**" in markdown
        assert "**如何回答：**" in markdown
        assert "**参考资料：**" in markdown
        assert "**练习提示词：**" in markdown

    def test_markdown_code_blocks(self, sample_report):
        """Test that prompt templates are in code blocks"""
        markdown = report_to_markdown(sample_report)

        # Count code block markers
        code_block_count = markdown.count("```")

        # Should have 2 questions * 2 markers (start and end) = 4
        assert code_block_count >= 4

    def test_markdown_separators(self, sample_report):
        """Test that sections are separated by horizontal rules"""
        markdown = report_to_markdown(sample_report)

        # Count horizontal rules (---)
        separator_count = markdown.count("---")

        # Should have multiple separators
        assert separator_count >= 5

    def test_usage_instructions_in_markdown(self, sample_report):
        """Test that usage instructions are included"""
        markdown = report_to_markdown(sample_report)

        assert "准备答案" in markdown
        assert "使用练习提示词" in markdown
        assert "补充薄弱点" in markdown
        assert "模拟面试" in markdown

    def test_footer_information(self, sample_report):
        """Test that footer contains correct information"""
        markdown = report_to_markdown(sample_report)

        assert "报告生成信息" in markdown
        assert "claude-sonnet-4" in markdown
        assert "v1.0" in markdown
        assert "GrillRadar 自动生成" in markdown

    def test_markdown_with_many_questions(self):
        """Test markdown generation with maximum questions"""
        questions = [
            QuestionItem(
                id=i,
                view_role="技术面试官",
                tag=f"标签{i}",
                question=f"这是第{i}个问题" * 3,
                rationale=f"这是第{i}个理由" * 5,
                baseline_answer=f"这是第{i}个答案" * 10,
                support_notes=f"这是第{i}个材料" * 5,
                prompt_template=f"这是第{i}个模板" * 10
            )
            for i in range(1, 21)
        ]

        report = Report(
            summary="测试摘要" * 20,
            mode="job",
            target_desc="测试岗位",
            highlights="测试亮点" * 10,
            risks="测试风险" * 10,
            questions=questions,
            meta=ReportMeta(
                generated_at="2025-11-17T10:00:00Z",
                model="claude-sonnet-4",
                num_questions=20
            )
        )

        markdown = report_to_markdown(report)

        # Should have all 20 questions
        for i in range(1, 21):
            assert f"Q{i}" in markdown

    def test_markdown_length(self, sample_report):
        """Test that generated markdown is substantial"""
        markdown = report_to_markdown(sample_report)

        # Should be a reasonably long document
        assert len(markdown) > 2000

    def test_markdown_format_consistency(self, sample_report):
        """Test that markdown formatting is consistent"""
        markdown = report_to_markdown(sample_report)

        # Check for consistent heading levels
        assert markdown.count("# ") >= 1  # Main title
        assert markdown.count("## ") >= 5  # Major sections
        assert markdown.count("### ") >= 2  # Questions

    def test_markdown_special_characters_handling(self):
        """Test handling of special characters in markdown"""
        questions = []
        for i in range(1, 11):
            questions.append(QuestionItem(
                id=i,
                view_role="技术面试官",
                tag="代码" if i == 1 else f"标签{i}",
                question="如何使用 `grep` 命令查找文件？" if i == 1 else f"问题{i}" * 3,
                rationale="考察候选人的命令行工具使用能力" if i == 1 else f"理由{i}" * 5,
                baseline_answer="使用 `grep -r pattern directory` 命令" * 5 if i == 1 else f"答案{i}" * 10,
                support_notes="参考 **Linux命令大全**" * 3 if i == 1 else f"材料{i}" * 5,
                prompt_template="描述你使用 `grep` 的经验\n{your_experience}" * 5 if i == 1 else f"模板{i}" * 10
            ))

        report = Report(
            summary="测试特殊字符处理：`代码`、**加粗**、*斜体*" * 10,
            mode="job",
            target_desc="Linux工程师",
            highlights="擅长 `命令行` 工具" * 10,
            risks="需要学习更多 **高级** 用法" * 10,
            questions=questions,
            meta=ReportMeta(
                generated_at="2025-11-17T10:00:00Z",
                model="claude-sonnet-4",
                num_questions=10
            )
        )

        markdown = report_to_markdown(report)

        # Should preserve markdown formatting
        assert "`grep`" in markdown
        assert "**Linux命令大全**" in markdown
