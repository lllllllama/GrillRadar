"""Tests for LLM client"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.core.llm_client import LLMClient
from app.config.settings import settings


class TestLLMClientInitialization:
    @patch('app.core.llm_client.Anthropic')
    def test_init_anthropic_with_defaults(self, mock_anthropic):
        """Test initializing with Anthropic provider using defaults"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")

            assert client.provider == "anthropic"
            assert client.model == settings.DEFAULT_MODEL
            assert client.temperature == settings.LLM_TEMPERATURE
            assert client.max_tokens == settings.LLM_MAX_TOKENS
            mock_anthropic.assert_called_once()

    @patch('app.core.llm_client.Anthropic')
    def test_init_anthropic_with_custom_params(self, mock_anthropic):
        """Test initializing with custom parameters"""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(
                provider="anthropic",
                model="claude-3-opus-20240229",
                temperature=0.5,
                max_tokens=2000
            )

            assert client.model == "claude-3-opus-20240229"
            assert client.temperature == 0.5
            assert client.max_tokens == 2000

    @patch('app.core.llm_client.Anthropic')
    def test_init_anthropic_with_base_url(self, mock_anthropic):
        """Test initializing with custom base URL"""
        with patch.dict('os.environ', {
            'ANTHROPIC_API_KEY': 'test-key',
            'ANTHROPIC_BASE_URL': 'https://custom.api.com'
        }):
            with patch.object(settings, 'ANTHROPIC_BASE_URL', 'https://custom.api.com'):
                client = LLMClient(provider="anthropic")

                # Verify base_url was passed to Anthropic
                call_kwargs = mock_anthropic.call_args[1]
                assert 'base_url' in call_kwargs
                assert call_kwargs['base_url'] == 'https://custom.api.com'

    @patch('app.core.llm_client.Anthropic')
    def test_init_anthropic_missing_api_key(self, mock_anthropic):
        """Test that missing API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with patch.object(settings, 'ANTHROPIC_API_KEY', None):
                with patch.object(settings, 'ANTHROPIC_AUTH_TOKEN', None):
                    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN not set"):
                        LLMClient(provider="anthropic")

    @patch('app.core.llm_client.OpenAI')
    def test_init_openai(self, mock_openai):
        """Test initializing with OpenAI provider"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch.object(settings, 'OPENAI_API_KEY', 'test-key'):
                client = LLMClient(provider="openai")

                assert client.provider == "openai"
                mock_openai.assert_called_once_with(api_key='test-key')

    @patch('app.core.llm_client.OpenAI')
    def test_init_openai_missing_api_key(self, mock_openai):
        """Test that missing OpenAI API key raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with patch.object(settings, 'OPENAI_API_KEY', None):
                with pytest.raises(ValueError, match="OPENAI_API_KEY not set"):
                    LLMClient(provider="openai")

    def test_init_unsupported_provider(self):
        """Test that unsupported provider raises error"""
        with pytest.raises(ValueError, match="Unsupported LLM provider: invalid"):
            LLMClient(provider="invalid")


class TestLLMClientAnthropicCalls:
    @patch('app.core.llm_client.Anthropic')
    def test_call_with_user_message(self, mock_anthropic):
        """Test calling Anthropic with system and user messages"""
        # Setup mock
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")
            result = client.call("System prompt", "User message")

            assert result == "Test response"
            mock_client.messages.create.assert_called_once()

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs['system'] == "System prompt"
            assert call_kwargs['messages'][0]['role'] == 'user'
            assert call_kwargs['messages'][0]['content'] == "User message"

    @patch('app.core.llm_client.Anthropic')
    def test_call_without_user_message(self, mock_anthropic):
        """Test calling Anthropic with only system prompt"""
        # Setup mock
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")
            result = client.call("System prompt")

            assert result == "Test response"

            # When no user message, system prompt becomes user message
            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs['system'] == "You are a helpful AI assistant."
            assert call_kwargs['messages'][0]['role'] == 'user'
            assert call_kwargs['messages'][0]['content'] == "System prompt"

    @patch('app.core.llm_client.Anthropic')
    def test_call_uses_custom_params(self, mock_anthropic):
        """Test that call uses custom temperature and max_tokens"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(
                provider="anthropic",
                model="claude-3-opus-20240229",
                temperature=0.3,
                max_tokens=1500
            )
            client.call("Test")

            call_kwargs = mock_client.messages.create.call_args[1]
            assert call_kwargs['model'] == "claude-3-opus-20240229"
            assert call_kwargs['temperature'] == 0.3
            assert call_kwargs['max_tokens'] == 1500


class TestLLMClientOpenAICalls:
    @patch('app.core.llm_client.OpenAI')
    def test_call_with_user_message(self, mock_openai):
        """Test calling OpenAI with system and user messages"""
        # Setup mock
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch.object(settings, 'OPENAI_API_KEY', 'test-key'):
                client = LLMClient(provider="openai")
                result = client.call("System prompt", "User message")

                assert result == "Test response"

                call_kwargs = mock_client.chat.completions.create.call_args[1]
                assert call_kwargs['messages'][0]['role'] == 'system'
                assert call_kwargs['messages'][0]['content'] == "System prompt"
                assert call_kwargs['messages'][1]['role'] == 'user'
                assert call_kwargs['messages'][1]['content'] == "User message"

    @patch('app.core.llm_client.OpenAI')
    def test_call_without_user_message(self, mock_openai):
        """Test calling OpenAI with only system prompt"""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch.object(settings, 'OPENAI_API_KEY', 'test-key'):
                client = LLMClient(provider="openai")
                result = client.call("System prompt")

                # OpenAI should have system message even without user message
                call_kwargs = mock_client.chat.completions.create.call_args[1]
                assert len(call_kwargs['messages']) == 1
                assert call_kwargs['messages'][0]['role'] == 'system'


class TestLLMClientJSONParsing:
    @patch('app.core.llm_client.Anthropic')
    def test_call_json_with_plain_json(self, mock_anthropic):
        """Test parsing plain JSON response"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        json_data = {"key": "value", "number": 42}
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps(json_data))]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")
            result = client.call_json("System prompt")

            assert result == json_data

    @patch('app.core.llm_client.Anthropic')
    def test_call_json_with_markdown_code_block(self, mock_anthropic):
        """Test parsing JSON wrapped in markdown code block"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        json_data = {"key": "value"}
        wrapped_response = f"```json\n{json.dumps(json_data)}\n```"

        mock_response = Mock()
        mock_response.content = [Mock(text=wrapped_response)]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")
            result = client.call_json("System prompt")

            assert result == json_data

    @patch('app.core.llm_client.Anthropic')
    def test_call_json_with_plain_code_block(self, mock_anthropic):
        """Test parsing JSON wrapped in plain code block"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        json_data = {"key": "value"}
        wrapped_response = f"```\n{json.dumps(json_data)}\n```"

        mock_response = Mock()
        mock_response.content = [Mock(text=wrapped_response)]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")
            result = client.call_json("System prompt")

            assert result == json_data

    @patch('app.core.llm_client.Anthropic')
    def test_call_json_with_whitespace(self, mock_anthropic):
        """Test parsing JSON with extra whitespace"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        json_data = {"key": "value"}
        response_with_whitespace = f"\n\n  {json.dumps(json_data)}  \n\n"

        mock_response = Mock()
        mock_response.content = [Mock(text=response_with_whitespace)]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")
            result = client.call_json("System prompt")

            assert result == json_data

    @patch('app.core.llm_client.Anthropic')
    def test_call_json_with_invalid_json(self, mock_anthropic):
        """Test that invalid JSON raises ValueError"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock(text="This is not JSON")]
        mock_client.messages.create.return_value = mock_response

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")

            with pytest.raises(ValueError, match="LLM返回的不是有效的JSON格式"):
                client.call_json("System prompt")


class TestLLMClientErrorHandling:
    @patch('app.core.llm_client.Anthropic')
    def test_call_api_error(self, mock_anthropic):
        """Test that API errors are propagated"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Simulate API error
        mock_client.messages.create.side_effect = Exception("API Error")

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")

            with pytest.raises(Exception, match="API Error"):
                client.call("Test")

    @patch('app.core.llm_client.Anthropic')
    def test_call_json_api_error(self, mock_anthropic):
        """Test that API errors in call_json are propagated"""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_client.messages.create.side_effect = Exception("Connection failed")

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            client = LLMClient(provider="anthropic")

            with pytest.raises(Exception, match="Connection failed"):
                client.call_json("Test")
