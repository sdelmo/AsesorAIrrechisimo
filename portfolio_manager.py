"""
AsesorAIrrechisimo - AI-Powered Portfolio Manager
A Streamlit application with a Venezuelan AI financial advisor personality.
"""
import streamlit as st
import logging
from typing import Optional
import anthropic

# Configure logging
from src.config import LOG_LEVEL, LOG_FORMAT, APP_TITLE, APP_ICON, LAYOUT, RiskProfile

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Import utilities
from src.utils.claude_client import initialize_client, ClaudeClientError, validate_api_key
from src.utils.portfolio import get_portfolio_summary

# Import UI modules
from src.ui.chat_tab import render_chat_tab
from src.ui.portfolio_tab import render_portfolio_tab
from src.ui.analysis_tab import render_analysis_tab


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT
)


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'risk_profile' not in st.session_state:
        st.session_state.risk_profile = None

    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''


def render_sidebar() -> tuple[str, Optional[anthropic.Anthropic]]:
    """
    Render sidebar with configuration options.

    Returns:
        Tuple of (api_key, client) where client may be None if initialization fails
    """
    with st.sidebar:
        st.header("⚙️ Configuración")

        # API Key input
        api_key = st.text_input(
            "API Key de Anthropic",
            type="password",
            value=st.session_state.api_key,
            help="Ingresa tu API key de Anthropic. Consíguela en https://console.anthropic.com/"
        )

        client = None

        if api_key:
            try:
                # Validate and store API key
                validate_api_key(api_key)
                st.session_state.api_key = api_key

                # Initialize client
                client = initialize_client(api_key)
                st.success("✓ API Key configurada, vale")

            except ClaudeClientError as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"API key validation error: {str(e)}")
        else:
            st.warning("Por favor ingresa tu API key para usar al asesor venezolano")

        st.divider()

        # Risk profile selection
        st.header("🎯 Perfil de Riesgo")

        risk_options = RiskProfile.get_all_values()

        # Get current index safely
        current_risk = st.session_state.risk_profile or RiskProfile.CONSERVATIVE.value
        current_index = 0

        try:
            if current_risk in risk_options:
                current_index = risk_options.index(current_risk)
            elif current_risk and current_risk.startswith("Personalizado:"):
                current_index = risk_options.index(RiskProfile.CUSTOM.value)
        except (ValueError, AttributeError):
            current_index = 0

        risk_profile = st.selectbox(
            "Selecciona tu tolerancia al riesgo:",
            risk_options,
            index=current_index
        )

        # Custom risk profile
        if risk_profile == RiskProfile.CUSTOM.value:
            custom_risk = st.text_area(
                "Describe tus preferencias de riesgo:",
                help="Ej: 'Quiero ingresos estables con algo de crecimiento, cómodo con 20% en acciones'",
                value=st.session_state.risk_profile.replace("Personalizado: ", "")
                if st.session_state.risk_profile and st.session_state.risk_profile.startswith("Personalizado:")
                else ""
            )
            if custom_risk:
                st.session_state.risk_profile = f"Personalizado: {custom_risk}"
            else:
                st.session_state.risk_profile = RiskProfile.CUSTOM.value
        else:
            st.session_state.risk_profile = risk_profile

        st.divider()

        # Quick actions
        st.header("💼 Acciones Rápidas")

        if st.button("📋 Ver Resumen del Portafolio"):
            if st.session_state.portfolio:
                summary = get_portfolio_summary(st.session_state.portfolio)
                st.text_area("Resumen", summary, height=300)
            else:
                st.info("El portafolio está vacío.")

        if st.button("🔄 Limpiar Historial de Chat"):
            st.session_state.chat_history = []
            st.success("✓ Historial limpiado")
            st.rerun()

        # App info
        st.divider()
        st.caption("v2.0 - Refactored Edition")
        st.caption("Potenciado por Claude AI")

    return api_key, client


def main() -> None:
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()

    # Render title
    st.title(APP_TITLE)
    st.markdown("*Con la voz de un venezolano arrecho y Claude AI*")

    # Render sidebar and get client
    api_key, client = render_sidebar()

    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs([
        "💬 Habla con el Venezolano",
        "📊 Gestión del Portafolio",
        "📈 Análisis Rápido"
    ])

    with tab1:
        render_chat_tab(client, api_key)

    with tab2:
        render_portfolio_tab()

    with tab3:
        render_analysis_tab(client, api_key)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Potenciado por un Venezolano virtual arrecho y Claude AI</p>
        <p style='font-size: 0.8em;'>
            Esta herramienta provee información con fines educativos.
            Siempre consulta con un asesor financiero calificado antes de tomar decisiones de inversión.
            (Pero este venezolano sabe burda, vale)
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error("Error inesperado en la aplicación. Por favor recarga la página.")
