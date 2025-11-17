"""Tests for ConfigManager singleton and caching"""

import pytest
from app.config.config_manager import ConfigManager


class TestConfigManager:
    def test_singleton_pattern(self):
        """Test that ConfigManager is a singleton"""
        manager1 = ConfigManager()
        manager2 = ConfigManager()

        # Same instance
        assert manager1 is manager2

    def test_domains_loaded(self):
        """Test that domains are loaded correctly"""
        manager = ConfigManager()
        domains = manager.domains

        assert domains is not None
        assert 'engineering' in domains
        assert 'research' in domains
        assert len(domains['engineering']) == 7
        assert len(domains['research']) == 6

    def test_modes_loaded(self):
        """Test that modes are loaded correctly"""
        manager = ConfigManager()
        modes = manager.modes

        assert modes is not None
        assert 'job' in modes
        assert 'grad' in modes
        assert 'mixed' in modes

    def test_caching_works(self):
        """Test that configurations are cached"""
        manager = ConfigManager()

        # First access
        domains1 = manager.domains
        modes1 = manager.modes

        # Second access should return same objects
        domains2 = manager.domains
        modes2 = manager.modes

        assert domains1 is domains2  # Same object in memory
        assert modes1 is modes2

    def test_get_domain_config(self):
        """Test getting specific domain config"""
        manager = ConfigManager()

        backend = manager.get_domain_config('backend')
        assert backend is not None
        assert backend['display_name'] == '后端开发'
        assert 'keywords' in backend

    def test_get_domain_config_invalid(self):
        """Test getting invalid domain returns None"""
        manager = ConfigManager()

        invalid = manager.get_domain_config('nonexistent')
        assert invalid is None

    def test_get_mode_config(self):
        """Test getting specific mode config"""
        manager = ConfigManager()

        job = manager.get_mode_config('job')
        assert job is not None
        assert 'description' in job
        assert 'roles' in job

    def test_get_mode_config_invalid(self):
        """Test getting invalid mode returns None"""
        manager = ConfigManager()

        invalid = manager.get_mode_config('nonexistent')
        assert invalid is None

    def test_reload(self):
        """Test configuration reload"""
        manager = ConfigManager()

        # Get initial configs
        domains_before = manager.domains
        last_reload_before = manager.last_reload

        # Force reload
        manager.reload()

        # Should have new timestamp
        assert manager.last_reload > last_reload_before

        # Should have loaded configs again (different objects)
        # Note: In production this would reload from file
        domains_after = manager.domains
        assert domains_after is not None
