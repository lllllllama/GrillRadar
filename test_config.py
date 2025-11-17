#!/usr/bin/env python3
"""
测试配置加载
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings

print("=" * 60)
print("当前配置:")
print("=" * 60)
print(f"ANTHROPIC_API_KEY: {settings.ANTHROPIC_API_KEY}")
print(f"ANTHROPIC_AUTH_TOKEN: {settings.ANTHROPIC_AUTH_TOKEN}")
print(f"ANTHROPIC_BASE_URL: {settings.ANTHROPIC_BASE_URL}")
print(f"DEFAULT_LLM_PROVIDER: {settings.DEFAULT_LLM_PROVIDER}")
print(f"DEFAULT_MODEL: {settings.DEFAULT_MODEL}")
print("=" * 60)
