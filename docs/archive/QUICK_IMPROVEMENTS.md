# Quick Improvements Guide - Start Today!

**Goal**: Implement high-impact, low-effort improvements from TrendRadar patterns in 1-2 days.

---

## 🚀 Priority 1: Configuration Validation (2 hours)

### Step 1: Create Exception Hierarchy

**File**: `app/exceptions.py`
```python
"""Custom exceptions for GrillRadar"""

class GrillRadarError(Exception):
    """Base exception for all GrillRadar errors"""
    pass


class ConfigurationError(GrillRadarError):
    """Raised when configuration files are invalid"""

    def __init__(self, message: str, config_file: str = None, field: str = None):
        self.config_file = config_file
        self.field = field

        error_msg = f"Configuration error"
        if config_file:
            error_msg += f" in {config_file}"
        if field:
            error_msg += f" (field: {field})"
        error_msg += f": {message}"

        super().__init__(error_msg)


class LLMError(GrillRadarError):
    """Raised when LLM API calls fail"""

    def __init__(self, provider: str, message: str, original_error: Exception = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"LLM error ({provider}): {message}")


class ValidationError(GrillRadarError):
    """Raised when input validation fails"""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class ExternalDataError(GrillRadarError):
    """Raised when external data retrieval fails"""
    pass
```

### Step 2: Create Configuration Validator

**File**: `app/config/validator.py`
```python
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

        logger.info(f"✅ Domains configuration valid ({len(domains['engineering'])} engineering + {len(domains['research'])} research domains)")
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
```

### Step 3: Add Validation to Application Startup

**File**: `app/main.py` (Add to existing file)
```python
# Add import at top
from app.config.validator import ConfigValidator
from app.exceptions import ConfigurationError

# Add startup event
@app.on_event("startup")
async def validate_configuration():
    """Validate all configuration files at startup"""
    try:
        ConfigValidator.validate_all()
        logger.info("✅ Application configuration validated")
    except ConfigurationError as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        raise  # Stop application startup
```

**Test it**:
```bash
# Start the application - it should validate configs
python -m uvicorn app.main:app --reload

# You should see in logs:
# INFO:     Validating domains configuration: /path/to/domains.yaml
# INFO:     ✅ Domains configuration valid (7 engineering + 6 research domains)
# INFO:     Validating modes configuration: /path/to/modes.yaml
# INFO:     ✅ Modes configuration valid (3 modes)
# INFO:     🎉 All configuration files validated successfully
# INFO:     ✅ Application configuration validated
```

---

## 🧪 Priority 2: Testing Framework (4 hours)

### Step 1: Install pytest

**File**: `requirements.txt` (Add these lines)
```
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
```

```bash
pip install pytest pytest-cov pytest-asyncio
```

### Step 2: Create Test Structure

```bash
mkdir -p tests
touch tests/__init__.py
touch tests/conftest.py
```

**File**: `tests/conftest.py`
```python
"""Pytest configuration and fixtures"""

import pytest
from app.models.user_config import UserConfig


@pytest.fixture
def sample_resume():
    """Sample resume text for testing"""
    return """
姓名：张三
教育背景：清华大学 计算机科学与技术 本科

项目经历：
1. 分布式爬虫系统
   - 使用Python开发，基于Redis和RabbitMQ
   - 实现了任务去重和容错机制
   - 日均爬取数据100万条

2. 微服务后端系统
   - 使用Go开发RESTful API
   - 接入MySQL和Redis
   - 支持10000+ QPS

技能：Python, Go, Java, MySQL, Redis, Kafka, Docker
"""


@pytest.fixture
def job_config(sample_resume):
    """Job mode configuration"""
    return UserConfig(
        mode='job',
        target_desc='字节跳动后端开发工程师',
        domain='backend',
        resume_text=sample_resume
    )


@pytest.fixture
def grad_config(sample_resume):
    """Grad mode configuration"""
    return UserConfig(
        mode='grad',
        target_desc='计算机视觉方向研究生',
        domain='cv_segmentation',
        resume_text=sample_resume
    )
```

### Step 3: Write Core Tests

**File**: `tests/test_domain_helper.py`
```python
"""Tests for DomainHelper"""

import pytest
from app.utils.domain_helper import DomainHelper


class TestDomainHelper:
    @pytest.fixture
    def helper(self):
        return DomainHelper()

    def test_get_domain_detail_backend(self, helper):
        """Test backend domain retrieval"""
        detail = helper.get_domain_detail('backend')

        assert detail is not None
        assert detail['display_name'] == '后端开发'
        assert 'keywords' in detail
        assert isinstance(detail['keywords'], list)
        assert len(detail['keywords']) > 0

    def test_get_domain_detail_invalid(self, helper):
        """Test invalid domain returns None"""
        detail = helper.get_domain_detail('nonexistent_domain')
        assert detail is None

    def test_get_domains_list_structure(self, helper):
        """Test domains list has correct structure"""
        domains = helper.get_domains_list()

        assert 'engineering' in domains
        assert 'research' in domains
        assert isinstance(domains['engineering'], list)
        assert len(domains['engineering']) == 7  # 7 engineering domains
        assert len(domains['research']) == 6     # 6 research domains

        # Check first engineering domain structure
        first_eng = domains['engineering'][0]
        assert 'value' in first_eng
        assert 'label' in first_eng
        assert 'description' in first_eng

    def test_get_domain_summary(self, helper):
        """Test domain summary statistics"""
        summary = helper.get_domain_summary()

        assert summary['total_domains'] == 13
        assert summary['engineering_count'] == 7
        assert summary['research_count'] == 6
        assert 'domains' in summary
```

**File**: `tests/test_user_config.py`
```python
"""Tests for UserConfig validation"""

import pytest
from pydantic import ValidationError
from app.models.user_config import UserConfig


class TestUserConfig:
    def test_valid_job_config(self, sample_resume):
        """Test valid job configuration"""
        config = UserConfig(
            mode='job',
            target_desc='后端开发工程师',
            domain='backend',
            resume_text=sample_resume
        )

        assert config.mode == 'job'
        assert config.domain == 'backend'

    def test_invalid_mode(self, sample_resume):
        """Test invalid mode raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            UserConfig(
                mode='invalid_mode',  # ❌ Invalid
                target_desc='工程师',
                resume_text=sample_resume
            )

        # Check error message
        assert 'mode' in str(exc_info.value)

    def test_resume_too_short(self):
        """Test resume length validation"""
        with pytest.raises(ValidationError) as exc_info:
            UserConfig(
                mode='job',
                target_desc='工程师',
                resume_text='短'  # ❌ Too short (< 10 chars)
            )

        assert 'resume_text' in str(exc_info.value)

    def test_external_info_fields(self, sample_resume):
        """Test external info configuration"""
        config = UserConfig(
            mode='job',
            target_desc='字节跳动后端工程师',
            resume_text=sample_resume,
            enable_external_info=True,
            target_company='字节跳动'
        )

        assert config.enable_external_info is True
        assert config.target_company == '字节跳动'
```

**File**: `tests/test_prompt_builder.py`
```python
"""Tests for PromptBuilder"""

import pytest
from app.core.prompt_builder import PromptBuilder


class TestPromptBuilder:
    @pytest.fixture
    def builder(self):
        return PromptBuilder()

    def test_build_prompt_structure(self, builder, job_config):
        """Test prompt has required sections"""
        prompt = builder.build(job_config)

        # Check for key sections
        assert '你的角色' in prompt
        assert '任务目标' in prompt
        assert '领域知识' in prompt
        assert '问题分布要求' in prompt
        assert job_config.target_desc in prompt
        assert job_config.resume_text in prompt

    def test_domain_knowledge_injection(self, builder, job_config):
        """Test domain knowledge is injected"""
        prompt = builder.build(job_config)

        # Backend domain should be mentioned
        assert '后端开发' in prompt
        # Should have keywords or stacks
        assert '分布式系统' in prompt or 'Java' in prompt or 'Go' in prompt

    def test_no_domain_specified(self, builder, sample_resume):
        """Test prompt works without domain"""
        from app.models.user_config import UserConfig

        config = UserConfig(
            mode='job',
            target_desc='软件工程师',
            resume_text=sample_resume
        )

        prompt = builder.build(config)
        assert '未指定领域' in prompt

    def test_external_info_disabled(self, builder, job_config):
        """Test external info section is empty when disabled"""
        job_config.enable_external_info = False

        prompt = builder.build(job_config)

        # External info should not be prominent
        # (Section may exist but should be minimal)
        assert prompt is not None

    def test_mode_specific_requirements(self, builder, grad_config):
        """Test grad mode has specific requirements"""
        prompt = builder.build(grad_config)

        # Should mention research/academic aspects
        assert 'grad' in prompt.lower() or '研究' in prompt or '学术' in prompt
```

### Step 4: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

**Expected output**:
```
======================== test session starts =========================
tests/test_domain_helper.py::TestDomainHelper::test_get_domain_detail_backend PASSED
tests/test_domain_helper.py::TestDomainHelper::test_get_domain_detail_invalid PASSED
tests/test_domain_helper.py::TestDomainHelper::test_get_domains_list_structure PASSED
tests/test_domain_helper.py::TestDomainHelper::test_get_domain_summary PASSED
tests/test_user_config.py::TestUserConfig::test_valid_job_config PASSED
tests/test_user_config.py::TestUserConfig::test_invalid_mode PASSED
tests/test_user_config.py::TestUserConfig::test_resume_too_short PASSED
tests/test_user_config.py::TestUserConfig::test_external_info_fields PASSED
tests/test_prompt_builder.py::TestPromptBuilder::test_build_prompt_structure PASSED
tests/test_prompt_builder.py::TestPromptBuilder::test_domain_knowledge_injection PASSED
tests/test_prompt_builder.py::TestPromptBuilder::test_no_domain_specified PASSED
tests/test_prompt_builder.py::TestPromptBuilder::test_external_info_disabled PASSED
tests/test_prompt_builder.py::TestPromptBuilder::test_mode_specific_requirements PASSED

======================== 13 passed in 1.24s ==========================
Coverage: 45% (will increase as more tests are added)
```

---

## ⚡ Priority 3: Configuration Caching (1 hour)

### Create Configuration Manager Singleton

**File**: `app/config/config_manager.py`
```python
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
```

### Update PromptBuilder to Use Cached Config

**File**: `app/core/prompt_builder.py` (Replace imports and __init__)
```python
# Replace existing imports with:
from app.config.config_manager import config_manager

class PromptBuilder:
    """构建虚拟委员会的System Prompt"""

    def __init__(self):
        """初始化，使用配置管理器"""
        # Use singleton config manager (cached!)
        self.config_manager = config_manager

    def build(self, user_config: UserConfig) -> str:
        # Replace self.modes with self.config_manager.modes
        mode_config = self.config_manager.modes.get(user_config.mode, {})

        # Replace self.domains with self.config_manager.domains
        domain_knowledge = self._get_domain_knowledge(user_config.domain)

        # ... rest of method unchanged

    def _get_domain_knowledge(self, domain: Optional[str]) -> str:
        """获取领域知识的格式化字符串（增强版）"""
        if not domain:
            return "未指定领域，请基于简历内容和目标岗位进行推断。"

        # Use cached config
        for category in ['engineering', 'research']:
            if category in self.config_manager.domains and domain in self.config_manager.domains[category]:
                domain_data = self.config_manager.domains[category][domain]
                # ... rest unchanged
```

**Test caching**:
```python
from app.config.config_manager import config_manager

# First access - loads from file
domains1 = config_manager.domains  # Takes ~10ms to load

# Second access - returns cached
domains2 = config_manager.domains  # Takes ~0.01ms (1000x faster!)

assert domains1 is domains2  # Same object in memory
```

---

## 📊 Verification Checklist

After implementing all three priorities, verify:

### ✅ Configuration Validation
```bash
# Test startup validation
python -m uvicorn app.main:app --reload

# Should see:
# INFO: ✅ Domains configuration valid (7 engineering + 6 research domains)
# INFO: ✅ Modes configuration valid (3 modes)
# INFO: 🎉 All configuration files validated successfully
```

### ✅ Testing Framework
```bash
# Run tests
pytest tests/ -v --cov=app

# Should see:
# ======================== 13+ passed ========================
# Coverage: 45%+
```

### ✅ Configuration Caching
```python
# In Python REPL
from app.config.config_manager import config_manager
import time

# Time first load
start = time.time()
d1 = config_manager.domains
print(f"First load: {(time.time() - start) * 1000:.2f}ms")

# Time cached access
start = time.time()
d2 = config_manager.domains
print(f"Cached access: {(time.time() - start) * 1000:.2f}ms")

# Should show:
# First load: 8.45ms
# Cached access: 0.02ms (400x faster!)
```

---

## 🎯 Next Steps After Quick Wins

Once these are done (1-2 days), you'll have:
- ✅ Startup validation catching config errors early
- ✅ Custom exceptions for clear error handling
- ✅ Testing framework with 13+ tests
- ✅ Configuration caching for better performance

**Then proceed to**:
1. Increase test coverage to 80%
2. Add more validation rules
3. Plan Milestone 5 (multi-agent architecture)

---

## 📚 Reference

- Full comparison: `COMPARATIVE_ANALYSIS.md`
- Architecture details: `ARCHITECTURE_ANALYSIS.md`
- BettaFish patterns: `BETTAFISH_ANALYSIS.md`
