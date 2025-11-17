"""Configuration manager with caching"""

import yaml
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
from app.config.settings import settings

logger = logging.getLogger(__name__)


class ConfigManager:
    """Singleton configuration manager with caching"""

    _instance: Optional['ConfigManager'] = None
    _domains: Optional[Dict] = None
    _modes: Optional[Dict] = None
    _last_reload: Optional[datetime] = None

    def __new__(cls):
        """Ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("📦 ConfigManager singleton created")
        return cls._instance

    @property
    def domains(self) -> Dict:
        """Get cached domains configuration"""
        if self._domains is None:
            self._load_configs()
        return self._domains

    @property
    def modes(self) -> Dict:
        """Get cached modes configuration"""
        if self._modes is None:
            self._load_configs()
        return self._modes

    @property
    def last_reload(self) -> Optional[datetime]:
        """Get timestamp of last configuration reload"""
        return self._last_reload

    def _load_configs(self):
        """Load all configuration files"""
        logger.info("📂 Loading configuration files...")

        # Load domains.yaml
        with open(settings.DOMAINS_CONFIG, 'r', encoding='utf-8') as f:
            self._domains = yaml.safe_load(f)

        # Load modes.yaml
        with open(settings.MODES_CONFIG, 'r', encoding='utf-8') as f:
            self._modes = yaml.safe_load(f)

        self._last_reload = datetime.now()

        logger.info(
            f"✅ Configurations loaded successfully at {self._last_reload.isoformat()}"
        )

    def reload(self):
        """Force reload configurations (useful for development)"""
        logger.info("🔄 Force reloading configurations...")
        self._domains = None
        self._modes = None
        self._load_configs()

    def get_domain_config(self, domain_key: str) -> Optional[Dict]:
        """
        Get configuration for a specific domain

        Args:
            domain_key: Domain identifier (e.g., 'backend')

        Returns:
            Domain configuration dict, or None if not found
        """
        for category in ['engineering', 'research']:
            if category in self.domains and domain_key in self.domains[category]:
                return self.domains[category][domain_key]
        return None

    def get_mode_config(self, mode_key: str) -> Optional[Dict]:
        """
        Get configuration for a specific mode

        Args:
            mode_key: Mode identifier (e.g., 'job')

        Returns:
            Mode configuration dict, or None if not found
        """
        return self.modes.get(mode_key)


# Global singleton instance
config_manager = ConfigManager()
