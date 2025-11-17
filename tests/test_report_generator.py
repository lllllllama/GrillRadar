"""Tests for ReportGenerator"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.core.report_generator import ReportGenerator
from app.models.user_config import UserConfig
from app.models.report import Report, ReportMeta
from app.models.question_item import QuestionItem


class TestReportGeneratorInitialization:
    @patch('app.core.report_generator.LLMClient')
    def test_init_with_defaults(self, mock_llm_client):
        """Test initialization with default parameters"""
        generator = ReportGenerator()

        assert generator.prompt_builder is not None
        mock_llm_client.assert_called_once_with(provider=None, model=None)

    @patch('app.core.report_generator.LLMClient')
    def test_init_with_custom_params(self, mock_llm_client):
        """Test initialization with custom provider and model"""
        generator = ReportGenerator(
            llm_provider="anthropic",
            llm_model="claude-3-opus-20240229"
        )

        mock_llm_client.assert_called_once_with(
            provider="anthropic",
            model="claude-3-opus-20240229"
        )


class TestReportGeneration:
    @pytest.fixture
    def sample_user_config(self):
        """Sample user config for testing"""
        return UserConfig(
            resume_text="候选人简历内容：3年后端开发经验，熟悉分布式系统" * 10,
            mode="job",
            target_desc="字节跳动后端开发工程师",
            domain="backend"
        )

    @pytest.fixture
    def sample_llm_response(self):
        """Sample LLM response matching Report schema"""
        questions = []
        for i in range(1, 11):
            questions.append({
                "id": i,
                "view_role": "技术面试官" if i % 2 == 0 else "招聘经理",
                "tag": f"标签{i}",
                "question": f"这是测试问题{i}的内容" * 3,
                "rationale": f"这是测试问题{i}的提问理由" * 5,
                "baseline_answer": f"这是测试问题{i}的基准答案" * 10,
                "support_notes": f"这是测试问题{i}的支持材料" * 5,
                "prompt_template": f"这是测试问题{i}的练习提示词，请描述：{{your_experience}}" * 10
            })

        return {
            "summary": "候选人具有3年后端开发经验，在分布式系统和微服务架构方面有实践经验" * 5,
            "mode": "job",
            "target_desc": "字节跳动后端开发工程师",
            "highlights": "1. 有丰富的分布式系统实践经验\n2. 熟悉主流后端技术栈\n3. 有高并发系统的设计和优化经验",
            "risks": "1. 算法和数据结构的理论深度需要加强\n2. 系统设计的方法论不够系统\n3. 对新技术的学习和跟进可以更主动",
            "questions": questions
        }

    @patch('app.core.report_generator.LLMClient')
    def test_generate_report_success(self, mock_llm_client, sample_user_config, sample_llm_response):
        """Test successful report generation"""
        # Setup mock
        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = sample_llm_response

        generator = ReportGenerator()
        report = generator.generate_report(sample_user_config)

        # Verify report structure
        assert isinstance(report, Report)
        assert report.mode == "job"
        assert report.target_desc == "字节跳动后端开发工程师"
        assert len(report.questions) == 10
        assert report.meta.num_questions == 10

    @patch('app.core.report_generator.LLMClient')
    def test_generate_report_adds_meta_if_missing(self, mock_llm_client, sample_user_config, sample_llm_response):
        """Test that meta field is added if missing from LLM response"""
        # Remove meta from response
        response_without_meta = sample_llm_response.copy()
        if 'meta' in response_without_meta:
            del response_without_meta['meta']

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response_without_meta

        generator = ReportGenerator()
        report = generator.generate_report(sample_user_config)

        # Meta should be added with correct num_questions
        assert report.meta is not None
        assert report.meta.num_questions == 10

    @patch('app.core.report_generator.LLMClient')
    def test_generate_report_adds_num_questions_to_meta(self, mock_llm_client, sample_user_config, sample_llm_response):
        """Test that num_questions is added to meta if missing"""
        # Add empty meta
        response_with_empty_meta = sample_llm_response.copy()
        response_with_empty_meta['meta'] = {}

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response_with_empty_meta

        generator = ReportGenerator()
        report = generator.generate_report(sample_user_config)

        assert report.meta.num_questions == 10

    @patch('app.core.report_generator.LLMClient')
    def test_generate_report_llm_error(self, mock_llm_client, sample_user_config):
        """Test that LLM errors are propagated"""
        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.side_effect = Exception("LLM API Error")

        generator = ReportGenerator()

        with pytest.raises(Exception, match="LLM API Error"):
            generator.generate_report(sample_user_config)

    @patch('app.core.report_generator.LLMClient')
    def test_generate_report_invalid_response(self, mock_llm_client, sample_user_config):
        """Test that invalid LLM response raises ValueError"""
        # Invalid response (missing required fields)
        invalid_response = {
            "summary": "Short",  # Too short
            "mode": "job"
            # Missing other required fields
        }

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = invalid_response

        generator = ReportGenerator()

        with pytest.raises(ValueError, match="生成的报告不符合规范"):
            generator.generate_report(sample_user_config)


class TestReportValidation:
    @pytest.fixture
    def sample_user_config(self):
        """Sample user config"""
        return UserConfig(
            resume_text="测试简历" * 20,
            mode="job",
            target_desc="后端工程师",
            domain="backend"
        )

    @pytest.fixture
    def create_report_data(self):
        """Factory function to create report data"""
        def _create(num_questions=10, mode="job", include_placeholders=True):
            questions = []
            for i in range(1, num_questions + 1):
                template = f"测试模板{i}"
                if include_placeholders:
                    template += " {your_experience}"
                template *= 10

                questions.append({
                    "id": i,
                    "view_role": "技术面试官",
                    "tag": f"标签{i}",
                    "question": f"问题{i}" * 3,
                    "rationale": f"理由{i}" * 5,
                    "baseline_answer": f"答案{i}" * 10,
                    "support_notes": f"材料{i}" * 5,
                    "prompt_template": template
                })

            return {
                "summary": "测试摘要" * 20,
                "mode": mode,
                "target_desc": "后端工程师",
                "highlights": "测试亮点" * 10,
                "risks": "测试风险" * 10,
                "questions": questions
            }
        return _create

    @patch('app.core.report_generator.LLMClient')
    def test_validate_too_few_questions(self, mock_llm_client, sample_user_config, create_report_data):
        """Test validation fails with too few questions"""
        response = create_report_data(num_questions=5)  # Less than 10

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        # Pydantic validation fails before custom validation
        with pytest.raises(ValueError, match="生成的报告不符合规范"):
            generator.generate_report(sample_user_config)

    @patch('app.core.report_generator.LLMClient')
    def test_validate_too_many_questions(self, mock_llm_client, sample_user_config, create_report_data):
        """Test validation fails with too many questions"""
        response = create_report_data(num_questions=25)  # More than 20

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        # Pydantic validation fails before custom validation
        with pytest.raises(ValueError, match="生成的报告不符合规范"):
            generator.generate_report(sample_user_config)

    @patch('app.core.report_generator.LLMClient')
    def test_validate_mode_mismatch(self, mock_llm_client, sample_user_config, create_report_data):
        """Test validation fails when mode doesn't match user config"""
        response = create_report_data(mode="grad")  # User config is "job"

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        with pytest.raises(ValueError, match="报告模式.*与用户配置.*不匹配"):
            generator.generate_report(sample_user_config)

    @patch('app.core.report_generator.LLMClient')
    def test_validate_mixed_mode_summary(self, mock_llm_client, create_report_data):
        """Test warning for mixed mode without dual assessment markers"""
        user_config = UserConfig(
            resume_text="测试" * 20,
            mode="mixed",
            target_desc="全栈工程师",
            domain="backend"
        )

        response = create_report_data(mode="mixed")
        # Summary doesn't have the required markers

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        # Should generate warning but not fail
        report = generator.generate_report(user_config)
        assert report is not None

    @patch('app.core.report_generator.LLMClient')
    def test_validate_question_id_discontinuity(self, mock_llm_client, sample_user_config, create_report_data):
        """Test warning for discontinuous question IDs"""
        response = create_report_data()
        # Make IDs discontinuous
        response['questions'][5]['id'] = 999

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        # Should generate warning but not fail
        report = generator.generate_report(sample_user_config)
        assert report is not None

    @patch('app.core.report_generator.LLMClient')
    def test_validate_missing_placeholders(self, mock_llm_client, sample_user_config, create_report_data):
        """Test warning for prompt templates without placeholders"""
        response = create_report_data(include_placeholders=False)

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        # Should generate warning but not fail
        report = generator.generate_report(sample_user_config)
        assert report is not None

    @patch('app.core.report_generator.LLMClient')
    def test_validate_valid_report(self, mock_llm_client, sample_user_config, create_report_data):
        """Test that valid report passes all validations"""
        response = create_report_data(num_questions=15, mode="job", include_placeholders=True)

        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = response

        generator = ReportGenerator()

        report = generator.generate_report(sample_user_config)

        assert isinstance(report, Report)
        assert len(report.questions) == 15
        assert report.mode == "job"


class TestReportGeneratorIntegration:
    @patch('app.core.report_generator.LLMClient')
    def test_full_workflow(self, mock_llm_client):
        """Test complete report generation workflow"""
        # Setup user config
        user_config = UserConfig(
            resume_text="资深后端工程师，5年分布式系统开发经验" * 10,
            mode="job",
            target_desc="阿里巴巴高级后端工程师",
            domain="backend"
        )

        # Setup LLM response
        questions = []
        for i in range(1, 16):
            questions.append({
                "id": i,
                "view_role": "技术面试官",
                "tag": "分布式系统",
                "question": f"请设计一个分布式系统解决方案{i}" * 3,
                "rationale": f"考察分布式系统理解{i}" * 5,
                "baseline_answer": f"应该考虑一致性、可用性、分区容错性{i}" * 10,
                "support_notes": f"参考CAP定理、BASE理论{i}" * 5,
                "prompt_template": f"描述你的分布式系统经验：{{your_experience}} - 案例{i}" * 10
            })

        llm_response = {
            "summary": "候选人在分布式系统方面有扎实的实践经验，但需要补充理论深度和系统设计方法论" * 5,
            "mode": "job",
            "target_desc": "阿里巴巴高级后端工程师",
            "highlights": "1. 5年分布式系统开发经验\n2. 熟悉微服务架构\n3. 有高并发系统优化经验",
            "risks": "1. 系统设计理论不够系统\n2. 缺少大规模系统架构经验\n3. 需要准备更多具体案例",
            "questions": questions,
            "meta": {
                "generated_at": "2025-11-17T10:00:00Z",
                "model": "claude-sonnet-4",
                "config_version": "v1.0",
                "num_questions": 15
            }
        }

        # Setup mock
        mock_client = Mock()
        mock_llm_client.return_value = mock_client
        mock_client.call_json.return_value = llm_response

        # Generate report
        generator = ReportGenerator(
            llm_provider="anthropic",
            llm_model="claude-sonnet-4"
        )
        report = generator.generate_report(user_config)

        # Verify report
        assert isinstance(report, Report)
        assert report.mode == "job"
        assert report.target_desc == "阿里巴巴高级后端工程师"
        assert len(report.questions) == 15
        assert "分布式系统" in report.summary
        assert report.meta.num_questions == 15

        # Verify LLM was called
        mock_client.call_json.assert_called_once()

        # Verify prompt builder was used
        call_args = mock_client.call_json.call_args
        system_prompt = call_args[0][0]
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 100  # Should be a substantial prompt
