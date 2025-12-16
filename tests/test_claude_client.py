"""Tests for Claude client utilities"""
import pytest
from src.utils.claude_client import (
    validate_api_key,
    ClaudeClientError,
    add_to_chat_history,
    build_system_prompt,
)


class TestAPIKeyValidation:
    """Test API key validation"""

    def test_validate_api_key_valid(self):
        """Test valid API key"""
        assert validate_api_key("sk-ant-api03-test-key") is True

    def test_validate_api_key_empty(self):
        """Test empty API key"""
        with pytest.raises(ClaudeClientError, match="no puede estar vacío"):
            validate_api_key("")

    def test_validate_api_key_invalid_prefix(self):
        """Test API key with invalid prefix"""
        with pytest.raises(ClaudeClientError, match="debe comenzar con"):
            validate_api_key("invalid-key-format")

    def test_validate_api_key_none(self):
        """Test None API key"""
        with pytest.raises(ClaudeClientError):
            validate_api_key(None)


class TestChatHistory:
    """Test chat history management"""

    def test_add_to_chat_history_empty(self):
        """Test adding to empty chat history"""
        history = []
        updated = add_to_chat_history(
            history,
            "Hello",
            "Hola chamo"
        )

        assert len(updated) == 2
        assert updated[0]["role"] == "user"
        assert updated[0]["content"] == "Hello"
        assert updated[1]["role"] == "assistant"
        assert updated[1]["content"] == "Hola chamo"

    def test_add_to_chat_history_existing(self):
        """Test adding to existing chat history"""
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"}
        ]

        updated = add_to_chat_history(
            history,
            "Second message",
            "Second response"
        )

        assert len(updated) == 4
        assert updated[2]["role"] == "user"
        assert updated[3]["role"] == "assistant"

    def test_add_to_chat_history_immutable(self):
        """Test that original history is not modified"""
        history = []
        updated = add_to_chat_history(history, "Test", "Response")

        assert len(history) == 0
        assert len(updated) == 2


class TestSystemPrompt:
    """Test system prompt building"""

    def test_build_system_prompt(self):
        """Test building system prompt with context"""
        portfolio_summary = "Portfolio: 3 holdings, $10,000 total"
        risk_profile = "Conservador"

        prompt = build_system_prompt(portfolio_summary, risk_profile)

        assert "Conservador" in prompt
        assert "Portfolio: 3 holdings" in prompt
        assert "venezolano" in prompt.lower()

    def test_build_system_prompt_no_risk_profile(self):
        """Test building system prompt without risk profile"""
        portfolio_summary = "Empty portfolio"
        risk_profile = ""

        prompt = build_system_prompt(portfolio_summary, risk_profile)

        assert "No definido" in prompt

    def test_build_system_prompt_custom_risk(self):
        """Test building system prompt with custom risk profile"""
        portfolio_summary = "Portfolio summary"
        risk_profile = "Personalizado: Moderate growth with capital preservation"

        prompt = build_system_prompt(portfolio_summary, risk_profile)

        assert "Personalizado" in prompt
        assert "Moderate growth" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
