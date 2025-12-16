"""Chat interface tab for conversing with the AI advisor"""
import streamlit as st
import logging
from typing import Optional
import anthropic

from src.utils.claude_client import chat_with_claude, ClaudeClientError, add_to_chat_history
from src.utils.portfolio import get_portfolio_summary
from src.config import ERROR_MESSAGES

logger = logging.getLogger(__name__)


def render_chat_tab(client: Optional[anthropic.Anthropic], api_key: str) -> None:
    """
    Render the chat interface tab.

    Args:
        client: Anthropic client instance (or None if not initialized)
        api_key: API key string
    """
    st.header("Habla con tu Asesor Financiero Venezolano")

    # Display chat history
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**Tú:** {message['content']}")
            else:
                st.markdown(f"**El Venezolano:** {message['content']}")

    # Chat input
    if api_key and client:
        user_input = st.chat_input("Pregunta sobre tu portafolio, tendencias del mercado, o pide análisis...")

        if user_input:
            try:
                with st.spinner("El venezolano está pensando..."):
                    # Get current context
                    portfolio_summary = get_portfolio_summary(st.session_state.portfolio)
                    risk_profile = st.session_state.risk_profile or "No definido"

                    # Get response from Claude
                    response = chat_with_claude(
                        user_message=user_input,
                        client=client,
                        portfolio_summary=portfolio_summary,
                        risk_profile=risk_profile,
                        chat_history=st.session_state.chat_history
                    )

                    # Update chat history
                    st.session_state.chat_history = add_to_chat_history(
                        st.session_state.chat_history,
                        user_input,
                        response
                    )

                    st.rerun()

            except ClaudeClientError as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Chat error: {str(e)}")
            except Exception as e:
                st.error(ERROR_MESSAGES["api_generic"])
                logger.error(f"Unexpected chat error: {str(e)}")
    else:
        st.info("👈 Por favor ingresa tu API key en la barra lateral para empezar a hablar")

    # Suggested prompts
    st.subheader("💡 Preguntas Sugeridas")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Analiza la diversidad de mi portafolio", key="btn_diversity"):
            if api_key and client:
                _handle_quick_question(
                    "Por favor analiza la diversidad de mi portafolio y sugiere mejoras.",
                    client
                )

        if st.button("📊 Investiga una posición específica", key="btn_research"):
            if api_key:
                st.session_state.chat_history = add_to_chat_history(
                    st.session_state.chat_history,
                    "",
                    "¿Cuál holding quieres que investigue, chamo? Dame el símbolo."
                )
                st.rerun()

    with col2:
        if st.button("💰 Dame sugerencias de rebalanceo", key="btn_rebalance"):
            if api_key and client:
                _handle_quick_question(
                    "Basado en mi perfil de riesgo y portafolio actual, ¿qué rebalanceo sugieres?",
                    client
                )

        if st.button("🌍 ¿Cómo está el mercado hoy?", key="btn_market"):
            if api_key and client:
                _handle_quick_question(
                    "¿Cuál es la perspectiva del mercado hoy? ¿Alguna noticia importante que afecte mis holdings?",
                    client
                )


def _handle_quick_question(question: str, client: anthropic.Anthropic) -> None:
    """
    Handle quick question button clicks.

    Args:
        question: Question to ask
        client: Anthropic client instance
    """
    try:
        portfolio_summary = get_portfolio_summary(st.session_state.portfolio)
        risk_profile = st.session_state.risk_profile or "No definido"

        response = chat_with_claude(
            user_message=question,
            client=client,
            portfolio_summary=portfolio_summary,
            risk_profile=risk_profile,
            chat_history=st.session_state.chat_history
        )

        st.session_state.chat_history = add_to_chat_history(
            st.session_state.chat_history,
            question,
            response
        )

        st.rerun()

    except ClaudeClientError as e:
        st.error(f"Error: {str(e)}")
        logger.error(f"Quick question error: {str(e)}")
    except Exception as e:
        st.error(ERROR_MESSAGES["api_generic"])
        logger.error(f"Unexpected quick question error: {str(e)}")
