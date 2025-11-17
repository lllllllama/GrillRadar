"""Tests for API endpoints"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.report import Report, ReportMeta
from app.models.question_item import QuestionItem
from app.models.external_info import ExternalInfoSummary, JobDescription, InterviewExperience


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "GrillRadar"


class TestDomainsEndpoints:
    def test_get_domains_list(self):
        """Test getting domains list"""
        response = client.get("/api/domains")
        assert response.status_code == 200
        data = response.json()

        # Should have engineering and research categories
        assert "engineering" in data
        assert "research" in data
        assert isinstance(data["engineering"], list)
        assert isinstance(data["research"], list)

    def test_get_domain_detail_valid(self):
        """Test getting valid domain detail"""
        # First get list of domains to find a valid one
        domains_response = client.get("/api/domains")
        domains_data = domains_response.json()

        # Get first engineering domain
        if domains_data.get("engineering") and len(domains_data["engineering"]) > 0:
            first_domain = domains_data["engineering"][0]["value"]

            response = client.get(f"/api/domains/{first_domain}")
            assert response.status_code == 200
            data = response.json()

            # Should have domain details
            assert "display_name" in data
            assert "description" in data
            assert "keywords" in data
            assert "category" in data

    def test_get_domain_detail_invalid(self):
        """Test getting invalid domain returns 404"""
        response = client.get("/api/domains/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_domains_stats(self):
        """Test getting domains statistics"""
        response = client.get("/api/domains-stats")
        assert response.status_code == 200
        data = response.json()

        # Should have counts (actual field names from domain_helper)
        assert "total" in data
        assert "engineering" in data
        assert "research" in data
        assert isinstance(data["total"], int)
        assert isinstance(data["engineering"], int)
        assert isinstance(data["research"], int)


class TestConfigEndpoints:
    def test_get_config_status(self):
        """Test getting configuration status"""
        response = client.get("/api/config/status")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "last_reload" in data
        assert "domains" in data
        assert "modes" in data

        # Check domains structure
        assert "engineering_count" in data["domains"]
        assert "research_count" in data["domains"]
        assert "total" in data["domains"]

        # Check modes structure
        assert "available" in data["modes"]
        assert "count" in data["modes"]
        assert isinstance(data["modes"]["available"], list)

    def test_reload_configuration(self):
        """Test reloading configuration"""
        response = client.post("/api/config/reload")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "message" in data
        assert "last_reload" in data
        assert "domains_count" in data
        assert "modes_count" in data


class TestExternalInfoEndpoints:
    def test_search_external_info_with_params(self):
        """Test searching external info with parameters"""
        response = client.get(
            "/api/external-info/search",
            params={
                "company": "字节跳动",
                "position": "后端开发",
                "enable_jd": True,
                "enable_interview_exp": True
            }
        )

        # Using mock provider, should return data
        assert response.status_code == 200
        data = response.json()

        assert "job_descriptions" in data
        assert "interview_experiences" in data
        assert "aggregated_keywords" in data

    def test_search_external_info_no_params(self):
        """Test searching external info without parameters"""
        response = client.get("/api/external-info/search")
        assert response.status_code == 200

        # Should return empty or default data from mock
        data = response.json()
        assert isinstance(data, dict)

    def test_preview_external_info(self):
        """Test previewing external info"""
        response = client.get(
            "/api/external-info/preview",
            params={
                "company": "字节跳动",
                "position": "后端开发"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "summary" in data
        assert "jd_count" in data
        assert "experience_count" in data
        assert "keywords" in data

    def test_preview_external_info_no_results(self):
        """Test preview when no results found"""
        with patch('app.sources.external_info_service.external_info_service.retrieve_external_info', return_value=None):
            response = client.get("/api/external-info/preview")

            assert response.status_code == 200
            data = response.json()
            assert "未找到" in data["summary"]


class TestGenerateReportEndpoint:
    @pytest.fixture
    def sample_report(self):
        """Sample report for mocking"""
        questions = []
        for i in range(1, 11):
            questions.append(QuestionItem(
                id=i,
                view_role="技术面试官",
                tag=f"标签{i}",
                question=f"测试问题{i}" * 3,
                rationale=f"测试理由{i}" * 5,
                baseline_answer=f"测试答案{i}" * 10,
                support_notes=f"测试材料{i}" * 5,
                prompt_template=f"测试模板{i}" * 10
            ))

        return Report(
            summary="测试摘要" * 20,
            mode="job",
            target_desc="后端开发工程师",
            highlights="测试亮点" * 10,
            risks="测试风险" * 10,
            questions=questions,
            meta=ReportMeta(
                generated_at="2025-11-17T10:00:00Z",
                model="claude-sonnet-4",
                num_questions=10
            )
        )

    @patch('app.api.report.ReportGenerator')
    def test_generate_report_success(self, mock_generator_class, sample_report):
        """Test successful report generation"""
        # Setup mock
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_report.return_value = sample_report

        # Make request
        request_data = {
            "mode": "job",
            "target_desc": "字节跳动后端开发工程师",
            "domain": "backend",
            "resume_text": "资深后端工程师，5年经验，熟悉分布式系统" * 10
        }

        response = client.post("/api/generate-report", json=request_data)

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["report"] is not None
        assert data["markdown"] is not None
        assert data["error"] is None

        # Verify report structure
        assert data["report"]["mode"] == "job"
        assert len(data["report"]["questions"]) == 10

        # Verify markdown content
        assert "# GrillRadar 面试准备报告" in data["markdown"]

    @patch('app.api.report.ReportGenerator')
    def test_generate_report_with_external_info(self, mock_generator_class, sample_report):
        """Test report generation with external info enabled"""
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_report.return_value = sample_report

        request_data = {
            "mode": "job",
            "target_desc": "字节跳动后端开发工程师",
            "domain": "backend",
            "resume_text": "资深后端工程师，5年经验" * 10,
            "enable_external_info": True,
            "target_company": "字节跳动"
        }

        response = client.post("/api/generate-report", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_report_invalid_mode(self):
        """Test report generation with invalid mode"""
        request_data = {
            "mode": "invalid_mode",  # Invalid
            "target_desc": "后端工程师",
            "resume_text": "测试简历" * 10
        }

        response = client.post("/api/generate-report", json=request_data)

        # Should return validation error
        assert response.status_code == 422  # Unprocessable Entity

    def test_generate_report_missing_fields(self):
        """Test report generation with missing required fields"""
        request_data = {
            "mode": "job"
            # Missing target_desc and resume_text
        }

        response = client.post("/api/generate-report", json=request_data)
        assert response.status_code == 422

    def test_generate_report_resume_too_short(self):
        """Test report generation with too short resume"""
        request_data = {
            "mode": "job",
            "target_desc": "后端工程师",
            "resume_text": "短"  # Too short (< 50 chars)
        }

        response = client.post("/api/generate-report", json=request_data)
        assert response.status_code == 422

    @patch('app.api.report.ReportGenerator')
    def test_generate_report_llm_error(self, mock_generator_class):
        """Test report generation when LLM fails"""
        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_report.side_effect = Exception("LLM API Error")

        request_data = {
            "mode": "job",
            "target_desc": "后端工程师",
            "resume_text": "资深后端工程师，拥有5年分布式系统开发经验，熟悉微服务架构" * 5  # Long enough
        }

        response = client.post("/api/generate-report", json=request_data)

        # Should return error response (not raise exception)
        assert response.status_code == 200  # Returns 200 but with success=False
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
        assert "失败" in data["error"]


class TestGenerateReportFormEndpoint:
    @patch('app.api.report.ReportGenerator')
    def test_generate_report_form_success(self, mock_generator_class):
        """Test form-based report generation"""
        # Setup mock
        questions = []
        for i in range(1, 11):
            questions.append(QuestionItem(
                id=i,
                view_role="技术面试官",
                tag=f"标签{i}",
                question=f"问题{i}" * 3,
                rationale=f"理由{i}" * 5,
                baseline_answer=f"答案{i}" * 10,
                support_notes=f"材料{i}" * 5,
                prompt_template=f"模板{i}" * 10
            ))

        sample_report = Report(
            summary="测试摘要" * 20,
            mode="job",
            target_desc="后端工程师",
            highlights="亮点" * 10,
            risks="风险" * 10,
            questions=questions,
            meta=ReportMeta(num_questions=10)
        )

        mock_generator = Mock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_report.return_value = sample_report

        # Make form request
        form_data = {
            "mode": "job",
            "target_desc": "后端工程师",
            "domain": "backend",
            "resume_text": "测试简历内容" * 10
        }

        response = client.post("/api/generate-report-form", data=form_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_report_form_invalid_data(self):
        """Test form submission with invalid data"""
        form_data = {
            "mode": "invalid",
            "target_desc": "short",
            "resume_text": "too short"
        }

        response = client.post("/api/generate-report-form", data=form_data)

        # Should return error (400 or validation error)
        assert response.status_code in [400, 422]


class TestAPIIntegration:
    """Integration tests for API workflow"""

    def test_full_workflow(self):
        """Test complete API workflow"""
        # 1. Check health
        health_response = client.get("/api/health")
        assert health_response.status_code == 200

        # 2. Get domains
        domains_response = client.get("/api/domains")
        assert domains_response.status_code == 200
        domains_data = domains_response.json()

        # 3. Get specific domain
        if domains_data.get("engineering"):
            first_domain = domains_data["engineering"][0]["value"]
            domain_response = client.get(f"/api/domains/{first_domain}")
            assert domain_response.status_code == 200

        # 4. Check configuration
        config_response = client.get("/api/config/status")
        assert config_response.status_code == 200

    def test_domains_workflow(self):
        """Test domain exploration workflow"""
        # Get all domains
        all_domains = client.get("/api/domains")
        assert all_domains.status_code == 200

        # Get stats
        stats = client.get("/api/domains-stats")
        assert stats.status_code == 200
        stats_data = stats.json()

        # Stats should match domains list
        all_data = all_domains.json()
        eng_count = len(all_data.get("engineering", []))
        res_count = len(all_data.get("research", []))

        # Check actual field names from domain_helper
        assert stats_data["engineering"] == eng_count
        assert stats_data["research"] == res_count
        assert stats_data["total"] == eng_count + res_count

    def test_config_reload_workflow(self):
        """Test configuration reload workflow"""
        # Get initial status
        status1 = client.get("/api/config/status")
        assert status1.status_code == 200
        data1 = status1.json()

        # Reload config
        reload_response = client.post("/api/config/reload")
        assert reload_response.status_code == 200

        # Get status again
        status2 = client.get("/api/config/status")
        assert status2.status_code == 200
        data2 = status2.json()

        # Counts should be the same
        assert data1["domains"]["total"] == data2["domains"]["total"]
        assert data1["modes"]["count"] == data2["modes"]["count"]
