"""LLM客户端封装"""
import json
import logging
import os
import time
from typing import Optional

# 重要：在导入anthropic之前先加载环境变量
# 因为anthropic库会在导入时读取环境变量ANTHROPIC_BASE_URL并设置默认值
from dotenv import load_dotenv
load_dotenv(override=True)

from anthropic import Anthropic
from openai import OpenAI
from app.config.settings import settings
from app.utils.json_sanitizer import safe_json_parse
from app.core.logging import get_logger, log_llm_call

logger = get_logger(__name__)


class LLMClient:
    """LLM调用客户端，支持Claude和OpenAI"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        request_id: Optional[str] = None,
        enable_json_repair: bool = True
    ):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or settings.DEFAULT_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.request_id = request_id or ""
        self.enable_json_repair = enable_json_repair

        # 初始化对应的客户端
        if self.provider == "anthropic":
            # 支持自定义API配置（如BigModel等兼容服务）
            api_key = settings.ANTHROPIC_AUTH_TOKEN or settings.ANTHROPIC_API_KEY
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not set in environment")

            # 构建客户端参数
            client_kwargs = {"api_key": api_key}
            if settings.ANTHROPIC_BASE_URL:
                client_kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
                logger.info(f"Using custom Anthropic base URL: {settings.ANTHROPIC_BASE_URL}")

            self.client = Anthropic(**client_kwargs)
        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def call(
        self,
        system_prompt: str,
        user_message: str = ""
    ) -> str:
        """
        调用LLM生成响应

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息（可选）

        Returns:
            LLM生成的文本响应
        """
        try:
            if self.provider == "anthropic":
                return self._call_anthropic(system_prompt, user_message)
            elif self.provider == "openai":
                return self._call_openai(system_prompt, user_message)
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise

    def _call_anthropic(self, system_prompt: str, user_message: str) -> str:
        """调用Claude API"""
        messages = []
        if user_message:
            messages.append({
                "role": "user",
                "content": user_message
            })
        else:
            # 如果没有用户消息，将system_prompt作为用户消息发送
            messages.append({
                "role": "user",
                "content": system_prompt
            })
            system_prompt = "You are a helpful AI assistant."

        # Time the API call
        start_time = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=messages
        )
        elapsed_time = time.time() - start_time

        response_text = response.content[0].text

        # Log LLM call metrics
        tokens_used = {
            'prompt_tokens': response.usage.input_tokens,
            'completion_tokens': response.usage.output_tokens
        }

        log_llm_call(
            logger=logger,
            request_id=self.request_id,
            provider=self.provider,
            model=self.model,
            prompt_length=len(system_prompt) + len(user_message),
            response_length=len(response_text),
            tokens_used=tokens_used,
            elapsed_time=elapsed_time
        )

        return response_text

    def _call_openai(self, system_prompt: str, user_message: str) -> str:
        """调用OpenAI API"""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        if user_message:
            messages.append({"role": "user", "content": user_message})

        # Time the API call
        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        elapsed_time = time.time() - start_time

        response_text = response.choices[0].message.content

        # Log LLM call metrics
        tokens_used = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens
        }

        log_llm_call(
            logger=logger,
            request_id=self.request_id,
            provider=self.provider,
            model=self.model,
            prompt_length=len(system_prompt) + len(user_message),
            response_length=len(response_text),
            tokens_used=tokens_used,
            elapsed_time=elapsed_time
        )

        return response_text

    def call_json(
        self,
        system_prompt: str,
        user_message: str = "",
        enable_repair: Optional[bool] = None
    ) -> dict:
        """
        调用LLM并解析JSON响应

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            enable_repair: 是否启用JSON修复（默认使用实例配置）

        Returns:
            解析后的JSON对象

        Raises:
            ValueError: JSON解析失败（在修复后仍失败）
        """
        response_text = self.call(system_prompt, user_message)

        # Determine whether to enable JSON repair
        use_repair = enable_repair if enable_repair is not None else self.enable_json_repair

        # Use safe_json_parse with automatic repair
        result = safe_json_parse(
            response_text,
            request_id=self.request_id,
            enable_llm_repair=use_repair,
            llm_client=self if use_repair else None,
            fallback_value=None
        )

        if result is None:
            # Parsing failed even after repair attempts
            logger.error(
                f"Failed to parse JSON after all repair attempts",
                extra={'request_id': self.request_id}
            )
            raise ValueError(f"LLM返回的不是有效的JSON格式，且修复失败")

        return result
