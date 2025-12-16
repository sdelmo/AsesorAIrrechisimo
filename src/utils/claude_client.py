"""Claude AI client wrapper with error handling and logging"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import anthropic

from src.config import (
    CLAUDE_MODEL,
    MAX_TOKENS,
    CHAT_HISTORY_LIMIT,
    API_KEY_PREFIX,
    ERROR_MESSAGES,
    SYSTEM_PROMPT_PATH,
)

logger = logging.getLogger(__name__)


class ClaudeClientError(Exception):
    """Custom exception for Claude client errors"""
    pass


def validate_api_key(api_key: str) -> bool:
    """
    Validate Anthropic API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid format

    Raises:
        ClaudeClientError: If key is invalid
    """
    if not api_key:
        raise ClaudeClientError("API key no puede estar vacío.")

    if not api_key.startswith(API_KEY_PREFIX):
        raise ClaudeClientError(
            f"API key debe comenzar con '{API_KEY_PREFIX}'. "
            "Verifica tu clave en https://console.anthropic.com/"
        )

    return True


def load_system_prompt() -> str:
    """
    Load system prompt from file.

    Returns:
        System prompt template string

    Raises:
        ClaudeClientError: If prompt file cannot be loaded
    """
    try:
        with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"System prompt file not found: {SYSTEM_PROMPT_PATH}")
        raise ClaudeClientError("No se pudo cargar la personalidad del asesor.")
    except Exception as e:
        logger.error(f"Error loading system prompt: {str(e)}")
        raise ClaudeClientError("Error al cargar la configuración del asesor.")


def build_system_prompt(portfolio_summary: str, risk_profile: str) -> str:
    """
    Build system prompt with current context.

    Args:
        portfolio_summary: Portfolio summary text
        risk_profile: User's risk profile

    Returns:
        Formatted system prompt
    """
    template = load_system_prompt()

    return template.format(
        risk_profile=risk_profile if risk_profile else "No definido todavía chamo",
        portfolio_summary=portfolio_summary,
        current_date=datetime.now().strftime('%Y-%m-%d')
    )


def initialize_client(api_key: str) -> anthropic.Anthropic:
    """
    Initialize Claude client with validated API key.

    Args:
        api_key: Anthropic API key

    Returns:
        Anthropic client instance

    Raises:
        ClaudeClientError: If validation or initialization fails
    """
    try:
        validate_api_key(api_key)
        return anthropic.Anthropic(api_key=api_key)
    except anthropic.APIError as e:
        logger.error(f"API error during client initialization: {str(e)}")
        raise ClaudeClientError("Error al inicializar cliente de Claude.")
    except Exception as e:
        logger.error(f"Unexpected error during client initialization: {str(e)}")
        raise ClaudeClientError("Error inesperado al configurar Claude.")


def chat_with_claude(
    user_message: str,
    client: anthropic.Anthropic,
    portfolio_summary: str,
    risk_profile: str,
    chat_history: List[Dict[str, str]]
) -> str:
    """
    Send message to Claude and get response with web search capability.

    Args:
        user_message: User's message
        client: Anthropic client instance
        portfolio_summary: Current portfolio summary
        risk_profile: User's risk profile
        chat_history: Conversation history

    Returns:
        Claude's response text

    Raises:
        ClaudeClientError: If API call fails
    """
    try:
        # Build system prompt with current context
        system_prompt = build_system_prompt(portfolio_summary, risk_profile)

        # Prepare messages with chat history
        messages = []

        # Add recent chat history (last N messages for context)
        for msg in chat_history[-CHAT_HISTORY_LIMIT:]:
            messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call Claude API with web search tool
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search"
                }
            ],
            messages=messages
        )

        # Handle tool use (web search) with loop protection
        max_iterations = 10
        iteration = 0

        while response.stop_reason == "tool_use" and iteration < max_iterations:
            iteration += 1

            # Extract tool use
            tool_use = next(
                (block for block in response.content if block.type == "tool_use"),
                None
            )

            if not tool_use:
                break

            # Add assistant's response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Add tool result
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": "Search completed"
                }]
            })

            # Get next response
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=messages
            )

        # Extract text response
        assistant_message = ""
        for block in response.content:
            if hasattr(block, 'text'):
                assistant_message += block.text

        if not assistant_message:
            logger.warning("Received empty response from Claude")
            return "Lo siento chamo, no pude generar una respuesta. Intenta de nuevo."

        return assistant_message

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {str(e)}")
        # Sanitize error message to avoid leaking sensitive info
        if "invalid_api_key" in str(e).lower():
            raise ClaudeClientError("API key inválida. Verifica tu clave en la barra lateral.")
        elif "rate_limit" in str(e).lower():
            raise ClaudeClientError("Límite de uso excedido. Espera un momento e intenta de nuevo.")
        else:
            raise ClaudeClientError(ERROR_MESSAGES["api_generic"])

    except Exception as e:
        logger.error(f"Unexpected error in chat_with_claude: {str(e)}")
        raise ClaudeClientError(ERROR_MESSAGES["api_generic"])


def add_to_chat_history(
    chat_history: List[Dict[str, str]],
    user_message: str,
    assistant_message: str
) -> List[Dict[str, str]]:
    """
    Add messages to chat history.

    Args:
        chat_history: Existing chat history
        user_message: User's message
        assistant_message: Assistant's response

    Returns:
        Updated chat history
    """
    updated_history = chat_history.copy()
    updated_history.append({"role": "user", "content": user_message})
    updated_history.append({"role": "assistant", "content": assistant_message})
    return updated_history
