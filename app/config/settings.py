"""应用配置管理"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_AUTH_TOKEN: Optional[str] = None  # 支持自定义API token (如BigModel)
    ANTHROPIC_BASE_URL: Optional[str] = None     # 支持自定义base URL
    OPENAI_API_KEY: Optional[str] = None

    # LLM配置
    DEFAULT_LLM_PROVIDER: str = "anthropic"  # anthropic | openai
    DEFAULT_MODEL: str = "claude-sonnet-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 16000
    LLM_TIMEOUT: int = 120  # 秒

    # 应用配置
    APP_NAME: str = "GrillRadar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_RATE_LIMIT_REQUESTS: int = 30
    API_RATE_LIMIT_WINDOW: int = 60

    # Multi-Agent配置
    MULTI_AGENT_ENABLED: bool = True  # 启用多智能体模式
    GRILLRADAR_DEBUG_AGENTS: bool = False  # 调试模式：保存中间产物

    # 外部信息提供者配置
    EXTERNAL_INFO_PROVIDER: str = "mock"  # mock | local_dataset | multi_source_crawler

    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CONFIG_DIR: Path = Path(__file__).parent
    DOMAINS_CONFIG: Path = CONFIG_DIR / "domains.yaml"
    MODES_CONFIG: Path = CONFIG_DIR / "modes.yaml"
    DEBUG_DIR: Path = BASE_DIR / "debug"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()
