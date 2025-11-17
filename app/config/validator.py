"""Configuration validation at application startup"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any
from app.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration files for correctness"""

    @staticmethod
    def validate_domains_config(domains_path: str) -> bool:
        """
        Validate domains.yaml structure and required fields

        Args:
            domains_path: Path to domains.yaml

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        logger.info(f"Validating domains configuration: {domains_path}")

        # Load YAML
        try:
            with open(domains_path, 'r', encoding='utf-8') as f:
                domains = yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load YAML: {e}",
                config_file="domains.yaml"
            )

        # Check top-level categories
        required_categories = ['engineering', 'research']
        for category in required_categories:
            if category not in domains:
                raise ConfigurationError(
                    f"Missing required category: {category}",
                    config_file="domains.yaml"
                )

        # Validate each domain
        required_domain_fields = ['display_name', 'description', 'keywords']

        for category in required_categories:
            category_domains = domains[category]

            if not isinstance(category_domains, dict):
                raise ConfigurationError(
                    f"Category '{category}' must be a dictionary",
                    config_file="domains.yaml",
                    field=category
                )

            for domain_key, domain_data in category_domains.items():
                # Check required fields
                for field in required_domain_fields:
                    if field not in domain_data:
                        raise ConfigurationError(
                            f"Domain '{domain_key}' missing required field: {field}",
                            config_file="domains.yaml",
                            field=f"{category}.{domain_key}.{field}"
                        )

                # Validate field types
                if not isinstance(domain_data['display_name'], str):
                    raise ConfigurationError(
                        f"Domain '{domain_key}' display_name must be a string",
                        config_file="domains.yaml",
                        field=f"{category}.{domain_key}.display_name"
                    )

                if not isinstance(domain_data['description'], str):
                    raise ConfigurationError(
                        f"Domain '{domain_key}' description must be a string",
                        config_file="domains.yaml",
                        field=f"{category}.{domain_key}.description"
                    )

                if not isinstance(domain_data['keywords'], list):
                    raise ConfigurationError(
                        f"Domain '{domain_key}' keywords must be a list",
                        config_file="domains.yaml",
                        field=f"{category}.{domain_key}.keywords"
                    )

                if len(domain_data['keywords']) < 3:
                    raise ConfigurationError(
                        f"Domain '{domain_key}' must have at least 3 keywords",
                        config_file="domains.yaml",
                        field=f"{category}.{domain_key}.keywords"
                    )

        logger.info(
            f"✅ Domains configuration valid "
            f"({len(domains['engineering'])} engineering + "
            f"{len(domains['research'])} research domains)"
        )
        return True

    @staticmethod
    def validate_modes_config(modes_path: str) -> bool:
        """
        Validate modes.yaml structure

        Args:
            modes_path: Path to modes.yaml

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        logger.info(f"Validating modes configuration: {modes_path}")

        # Load YAML
        try:
            with open(modes_path, 'r', encoding='utf-8') as f:
                modes = yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load YAML: {e}",
                config_file="modes.yaml"
            )

        # Check required modes
        required_modes = ['job', 'grad', 'mixed']
        for mode in required_modes:
            if mode not in modes:
                raise ConfigurationError(
                    f"Missing required mode: {mode}",
                    config_file="modes.yaml"
                )

        # Validate each mode
        for mode_key, mode_data in modes.items():
            # Check required fields
            if 'description' not in mode_data:
                raise ConfigurationError(
                    f"Mode '{mode_key}' missing 'description' field",
                    config_file="modes.yaml",
                    field=f"{mode_key}.description"
                )

            if 'roles' not in mode_data:
                raise ConfigurationError(
                    f"Mode '{mode_key}' missing 'roles' field",
                    config_file="modes.yaml",
                    field=f"{mode_key}.roles"
                )

            # Validate role weights
            roles = mode_data['roles']
            if not isinstance(roles, dict):
                raise ConfigurationError(
                    f"Mode '{mode_key}' roles must be a dictionary",
                    config_file="modes.yaml",
                    field=f"{mode_key}.roles"
                )

            # Check weights sum to ~1.0
            total_weight = sum(roles.values())
            if not (0.95 <= total_weight <= 1.05):
                raise ConfigurationError(
                    f"Mode '{mode_key}' role weights sum to {total_weight}, should be ~1.0",
                    config_file="modes.yaml",
                    field=f"{mode_key}.roles"
                )

        logger.info(f"✅ Modes configuration valid ({len(modes)} modes)")
        return True

    @staticmethod
    def validate_all() -> bool:
        """
        Validate all configuration files

        Returns:
            True if all valid

        Raises:
            ConfigurationError: If any validation fails
        """
        from app.config.settings import settings

        ConfigValidator.validate_domains_config(settings.DOMAINS_CONFIG)
        ConfigValidator.validate_modes_config(settings.MODES_CONFIG)

        logger.info("🎉 All configuration files validated successfully")
        return True
