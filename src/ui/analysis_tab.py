"""Quick analysis tab with AI-powered portfolio insights"""
import streamlit as st
import logging
from typing import Optional
import anthropic

from src.utils.claude_client import chat_with_claude, ClaudeClientError, add_to_chat_history
from src.utils.portfolio import get_portfolio_summary
from src.config import ERROR_MESSAGES

logger = logging.getLogger(__name__)


def render_analysis_tab(client: Optional[anthropic.Anthropic], api_key: str) -> None:
    """
    Render the quick analysis tab with one-click analysis buttons.

    Args:
        client: Anthropic client instance (or None if not initialized)
        api_key: API key string
    """
    st.header("Análisis Rápido")

    if not api_key:
        st.warning("👈 Por favor ingresa tu API key en la barra lateral")
        return

    if not st.session_state.portfolio:
        st.info("👈 Agrega holdings en la pestaña de Gestión del Portafolio primero")
        return

    st.markdown("""
    Haz clic en cualquier botón para obtener análisis instantáneo de tu portafolio con IA.
    Los resultados se agregarán al historial de chat.
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 Evaluación de Riesgo", use_container_width=True, key="analysis_risk"):
            _run_analysis(
                "Por favor provee una evaluación comprehensiva del riesgo de mi portafolio. "
                "Considera diversificación, asignación de activos, y alineación con mi perfil de riesgo.",
                "### 🎯 Evaluación de Riesgo",
                client
            )

        if st.button("📊 Análisis de Sectores", use_container_width=True, key="analysis_sectors"):
            _run_analysis(
                "Analiza la exposición sectorial en mi portafolio. "
                "¿En qué sectores estoy sobreponderado o subponderado?",
                "### 📊 Análisis de Sectores",
                client
            )

        if st.button("💎 Mejores Performers", use_container_width=True, key="analysis_performers"):
            _run_analysis(
                "Investiga el rendimiento actual de mis holdings. "
                "¿Cuáles son los mejores performers recientemente?",
                "### 💎 Mejores Performers",
                client
            )

    with col2:
        if st.button("⚖️ ¿Necesito Rebalancear?", use_container_width=True, key="analysis_rebalance"):
            _run_analysis(
                "¿Mi portafolio necesita rebalanceo? "
                "Provee recomendaciones específicas basadas en mi perfil de riesgo.",
                "### ⚖️ Recomendaciones de Rebalanceo",
                client
            )

        if st.button("🔮 Perspectiva Futura", use_container_width=True, key="analysis_outlook"):
            _run_analysis(
                "¿Cuál es la perspectiva para mis holdings? "
                "Busca reportes recientes de analistas y tendencias del mercado para mis posiciones clave.",
                "### 🔮 Perspectiva Futura",
                client
            )

        if st.button("🚨 Alertas de Riesgo", use_container_width=True, key="analysis_warnings"):
            _run_analysis(
                "¿Hay red flags recientes o noticias preocupantes sobre mis holdings? "
                "Busca cualquier noticia negativa o advertencias.",
                "### 🚨 Alertas de Riesgo",
                client
            )

    # Display latest analysis result if available
    if 'latest_analysis' in st.session_state:
        st.divider()
        st.markdown(st.session_state.latest_analysis['title'])
        st.write(st.session_state.latest_analysis['content'])

        if st.button("✓ Resultado guardado en el chat", key="analysis_saved"):
            # Clear the display
            del st.session_state.latest_analysis
            st.rerun()


def _run_analysis(
    query: str,
    title: str,
    client: anthropic.Anthropic
) -> None:
    """
    Run analysis query and update chat history.

    Args:
        query: Analysis question to ask
        title: Title for the analysis section
        client: Anthropic client instance
    """
    try:
        with st.spinner("Analizando portafolio..."):
            # Get current context
            portfolio_summary = get_portfolio_summary(st.session_state.portfolio)
            risk_profile = st.session_state.risk_profile or "No definido"

            # Get response from Claude
            response = chat_with_claude(
                user_message=query,
                client=client,
                portfolio_summary=portfolio_summary,
                risk_profile=risk_profile,
                chat_history=st.session_state.chat_history
            )

            # Update chat history so it appears in the chat tab
            st.session_state.chat_history = add_to_chat_history(
                st.session_state.chat_history,
                query,
                response
            )

            # Store latest analysis for display
            st.session_state.latest_analysis = {
                'title': title,
                'content': response
            }

            st.rerun()

    except ClaudeClientError as e:
        st.error(f"Error: {str(e)}")
        logger.error(f"Analysis error: {str(e)}")
    except Exception as e:
        st.error(ERROR_MESSAGES["api_generic"])
        logger.error(f"Unexpected analysis error: {str(e)}")
