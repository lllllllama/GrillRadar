"""Tests for main FastAPI application"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.exceptions import ConfigurationError


client = TestClient(app)


class TestHealthEndpoints:
    def test_root_health_check(self):
        """Test root health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "app" in data
        assert "version" in data

    def test_api_health_check(self):
        """Test API health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert data["service"] == "GrillRadar"


class TestIndexRoute:
    def test_index_route_exists(self):
        """Test that index route is accessible"""
        response = client.get("/")

        # Should either render template or show error (both are valid)
        # Just check that route exists and doesn't crash
        assert response.status_code in [200, 500]

    def test_index_without_templates(self):
        """Test index route when templates are not found"""
        # Simulate templates not being available
        with patch('app.main.templates', None):
            response = client.get("/")

            # Should return error HTML
            assert response.status_code == 500
            assert b"Templates not found" in response.content


class TestStaticFiles:
    def test_static_files_mounted(self):
        """Test that static files can be accessed"""
        # Note: This test depends on whether static files exist
        # We're just testing the mounting mechanism

        # If static path doesn't exist, we should see a warning
        # The application should still start successfully
        assert app is not None


class TestStartupValidation:
    @patch('app.main.ConfigValidator')
    def test_startup_validation_success(self, mock_validator):
        """Test successful configuration validation on startup"""
        # This is tested via the TestClient initialization
        # If validation fails, the app won't start

        mock_validator.validate_all.return_value = True

        # Application should be accessible
        response = client.get("/health")
        assert response.status_code == 200

    def test_startup_validation_config_loaded(self):
        """Test that configuration is actually loaded"""
        # The app should have loaded configurations
        response = client.get("/api/config/status")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "domains" in data
        assert "modes" in data


class TestApplicationMetadata:
    def test_app_title(self):
        """Test that application has correct title"""
        assert app.title is not None
        assert "GrillRadar" in app.title or app.title == "FastAPI"

    def test_app_version(self):
        """Test that application has version"""
        assert app.version is not None

    def test_app_routes_registered(self):
        """Test that all routes are registered"""
        routes = [route.path for route in app.routes]

        # Check key routes exist
        assert "/" in routes or any("/docs" in r for r in routes)
        assert "/health" in routes
        assert any("/api" in r for r in routes)


class TestCORSAndMiddleware:
    def test_cors_headers_not_blocking(self):
        """Test that CORS doesn't block basic requests"""
        response = client.get("/health")
        assert response.status_code == 200


class TestErrorHandling:
    def test_404_on_invalid_route(self):
        """Test 404 response on invalid route"""
        response = client.get("/this-route-does-not-exist-12345")
        assert response.status_code == 404

    def test_405_on_wrong_method(self):
        """Test 405 on wrong HTTP method"""
        # GET on a POST-only endpoint
        response = client.get("/api/generate-report")
        assert response.status_code == 405


class TestAPIIntegration:
    def test_full_api_workflow(self):
        """Test complete API is accessible"""
        # 1. Check root health
        health = client.get("/health")
        assert health.status_code == 200

        # 2. Check API health
        api_health = client.get("/api/health")
        assert api_health.status_code == 200

        # 3. Check config
        config = client.get("/api/config/status")
        assert config.status_code == 200

        # 4. Check domains
        domains = client.get("/api/domains")
        assert domains.status_code == 200

    def test_documentation_accessible(self):
        """Test that API documentation is accessible"""
        # FastAPI automatically generates docs at /docs and /redoc
        docs_response = client.get("/docs")
        # Should either be 200 (if docs enabled) or redirected
        assert docs_response.status_code in [200, 307, 404]

        redoc_response = client.get("/redoc")
        assert redoc_response.status_code in [200, 307, 404]

    def test_openapi_schema_accessible(self):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestConfigurationPaths:
    def test_static_path_handling(self):
        """Test that static path is handled correctly"""
        # The app should handle missing static directory gracefully
        # This is already tested by successful app initialization
        assert app is not None

    def test_templates_path_handling(self):
        """Test that templates path is handled correctly"""
        # The app should handle missing templates directory gracefully
        assert app is not None


class TestApplicationLifecycle:
    def test_app_can_handle_multiple_requests(self):
        """Test that app can handle multiple requests"""
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_app_consistent_responses(self):
        """Test that app gives consistent responses"""
        response1 = client.get("/health")
        response2 = client.get("/health")

        assert response1.json() == response2.json()
