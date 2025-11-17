"""应用配置管理"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
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

    # 路径配置
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CONFIG_DIR: Path = Path(__file__).parent
    DOMAINS_CONFIG: Path = CONFIG_DIR / "domains.yaml"
    MODES_CONFIG: Path = CONFIG_DIR / "modes.yaml"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()
