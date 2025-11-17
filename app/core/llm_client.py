"""LLM客户端封装"""
import json
import logging
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI
from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM调用客户端，支持Claude和OpenAI"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or settings.DEFAULT_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS

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

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    def _call_openai(self, system_prompt: str, user_message: str) -> str:
        """调用OpenAI API"""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        if user_message:
            messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        return response.choices[0].message.content

    def call_json(
        self,
        system_prompt: str,
        user_message: str = ""
    ) -> dict:
        """
        调用LLM并解析JSON响应

        Args:
            system_prompt: 系统提示词
            user_message: 用户消息

        Returns:
            解析后的JSON对象

        Raises:
            json.JSONDecodeError: JSON解析失败
        """
        response_text = self.call(system_prompt, user_message)

        # 尝试提取JSON（处理可能的markdown代码块包裹）
        response_text = response_text.strip()

        # 移除可能的markdown代码块标记
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response_text[:500]}")
            raise ValueError(f"LLM返回的不是有效的JSON格式: {str(e)}")
