"""Configuration constants and enums for AsesorAIrrechisimo"""
from enum import Enum
from typing import List


class RiskProfile(Enum):
    """Risk profile options for portfolio management"""
    CONSERVATIVE = "Conservador"
    MODERATE = "Moderado"
    AGGRESSIVE = "Agresivo"
    CUSTOM = "Personalizado"

    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all risk profile values as a list"""
        return [profile.value for profile in cls]


class AssetType(Enum):
    """Asset type classifications"""
    ETF = "ETF"
    STOCK = "Stock"
    BOND = "Bond"
    MUTUAL_FUND = "Mutual Fund"

    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all asset types as a list"""
        return [asset.value for asset in cls]


# Claude API Configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
CHAT_HISTORY_LIMIT = 10

# API Key Validation
API_KEY_PREFIX = "sk-ant-"

# UI Configuration
CHAT_CONTAINER_HEIGHT = 400
APP_TITLE = "AsesorAIrrechisimo"
APP_ICON = "📊"
LAYOUT = "wide"

# File paths
SYSTEM_PROMPT_PATH = "prompts/advisor_personality.txt"

# Portfolio Configuration
MAX_SYMBOL_LENGTH = 10
MIN_QUANTITY = 0.0
MIN_PRICE = 0.0

# Validation patterns
TICKER_PATTERN = r'^[A-Za-z0-9.\-]+$'  # Allow alphanumeric, dots, and hyphens

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Error messages
ERROR_MESSAGES = {
    "api_generic": "Error al comunicarse con Claude API. Por favor intenta de nuevo.",
    "invalid_ticker": "Símbolo inválido. Solo se permiten letras, números, puntos y guiones.",
    "invalid_quantity": "La cantidad debe ser mayor que 0.",
    "invalid_price": "El precio debe ser mayor o igual a 0.",
    "no_api_key": "Por favor ingresa tu API key en la barra lateral.",
    "empty_portfolio": "El portafolio está vacío. Agrega holdings primero.",
    "csv_import_error": "Error al importar CSV. Verifica que el archivo tenga el formato correcto.",
    "price_fetch_error": "No se pudo obtener el precio actual. Usando precio promedio.",
}

# Success messages
SUCCESS_MESSAGES = {
    "holding_added": "✓ {} agregado al portafolio!",
    "holding_removed": "✓ {} eliminado del portafolio",
    "holding_updated": "✓ {} actualizado exitosamente",
    "portfolio_imported": "✓ Portafolio importado exitosamente ({} holdings)",
}
