"""Portfolio management utilities with validation and pricing"""
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import yfinance as yf

from src.config import (
    TICKER_PATTERN,
    MAX_SYMBOL_LENGTH,
    MIN_QUANTITY,
    MIN_PRICE,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_ticker(symbol: str) -> bool:
    """
    Validate ticker symbol format.

    Args:
        symbol: Ticker symbol to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If ticker is invalid
    """
    if not symbol:
        raise ValidationError("El símbolo no puede estar vacío.")

    if len(symbol) > MAX_SYMBOL_LENGTH:
        raise ValidationError(f"El símbolo no puede tener más de {MAX_SYMBOL_LENGTH} caracteres.")

    if not re.match(TICKER_PATTERN, symbol):
        raise ValidationError(ERROR_MESSAGES["invalid_ticker"])

    return True


def validate_quantity(quantity: float) -> bool:
    """
    Validate quantity value.

    Args:
        quantity: Quantity to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If quantity is invalid
    """
    if quantity <= MIN_QUANTITY:
        raise ValidationError(ERROR_MESSAGES["invalid_quantity"])

    return True


def validate_price(price: float) -> bool:
    """
    Validate price value.

    Args:
        price: Price to validate

    Returns:
        True if valid

    Raises:
        ValidationError: If price is invalid
    """
    if price < MIN_PRICE:
        raise ValidationError(ERROR_MESSAGES["invalid_price"])

    return True


def get_current_price(symbol: str) -> Optional[float]:
    """
    Fetch current price for a ticker symbol using yfinance.

    Args:
        symbol: Ticker symbol

    Returns:
        Current price or None if fetch fails
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Try different price fields in order of preference
        price_fields = ['regularMarketPrice', 'currentPrice', 'previousClose', 'navPrice']

        for field in price_fields:
            if field in info and info[field] is not None:
                return float(info[field])

        logger.warning(f"No price found for {symbol}")
        return None

    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {str(e)}")
        return None


def calculate_portfolio_value(portfolio: List[Dict[str, Any]], use_current_price: bool = False) -> float:
    """
    Calculate total portfolio value.

    Args:
        portfolio: List of holdings
        use_current_price: Whether to fetch current prices

    Returns:
        Total portfolio value
    """
    total = 0.0

    for holding in portfolio:
        quantity = holding.get('quantity', 0)

        if use_current_price:
            current_price = get_current_price(holding.get('symbol', ''))
            price = current_price if current_price else holding.get('avg_price', 0)
        else:
            price = holding.get('avg_price', 0)

        total += quantity * price

    return total


def get_portfolio_summary(portfolio: List[Dict[str, Any]]) -> str:
    """
    Generate a text summary of the portfolio.

    Args:
        portfolio: List of holdings

    Returns:
        Formatted portfolio summary string
    """
    if not portfolio:
        return "Portfolio is empty."

    df = pd.DataFrame(portfolio)

    summary = "Current Portfolio:\n"
    summary += f"Total Holdings: {len(df)}\n\n"

    # Group by asset type
    if 'type' in df.columns:
        type_counts = df.groupby('type').size()
        summary += "Asset Distribution:\n"
        for asset_type, count in type_counts.items():
            summary += f"  - {asset_type}: {count} holdings\n"

    # List all holdings with current value
    summary += "\nDetailed Holdings:\n"
    for idx, holding in enumerate(df.to_dict('records'), 1):
        symbol = holding.get('symbol', 'N/A')
        name = holding.get('name', 'N/A')
        asset_type = holding.get('type', 'N/A')
        quantity = holding.get('quantity', 0)
        avg_price = holding.get('avg_price', 0)

        summary += f"{idx}. {symbol} - {name}\n"
        summary += f"   Type: {asset_type}, Quantity: {quantity}, "
        summary += f"Avg Price: ${avg_price:.2f}\n"

    return summary


def create_holding(
    symbol: str,
    name: str,
    asset_type: str,
    quantity: float,
    avg_price: float,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Create a validated holding dictionary.

    Args:
        symbol: Ticker symbol
        name: Asset name
        asset_type: Type of asset
        quantity: Number of shares/units
        avg_price: Average purchase price
        notes: Optional notes

    Returns:
        Holding dictionary

    Raises:
        ValidationError: If any validation fails
    """
    # Validate inputs
    validate_ticker(symbol)
    validate_quantity(quantity)
    validate_price(avg_price)

    return {
        "symbol": symbol.upper(),
        "name": name.strip(),
        "type": asset_type,
        "quantity": quantity,
        "avg_price": avg_price,
        "notes": notes.strip(),
        "added_date": datetime.now().strftime("%Y-%m-%d")
    }


def update_holding(
    holding: Dict[str, Any],
    quantity: Optional[float] = None,
    avg_price: Optional[float] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing holding with validation.

    Args:
        holding: Existing holding dictionary
        quantity: New quantity (optional)
        avg_price: New average price (optional)
        notes: New notes (optional)

    Returns:
        Updated holding dictionary

    Raises:
        ValidationError: If any validation fails
    """
    updated = holding.copy()

    if quantity is not None:
        validate_quantity(quantity)
        updated['quantity'] = quantity

    if avg_price is not None:
        validate_price(avg_price)
        updated['avg_price'] = avg_price

    if notes is not None:
        updated['notes'] = notes.strip()

    updated['updated_date'] = datetime.now().strftime("%Y-%m-%d")

    return updated


def export_portfolio_csv(portfolio: List[Dict[str, Any]]) -> str:
    """
    Export portfolio to CSV format.

    Args:
        portfolio: List of holdings

    Returns:
        CSV string
    """
    df = pd.DataFrame(portfolio)
    return df.to_csv(index=False)


def import_portfolio_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Import portfolio from CSV with validation.

    Args:
        csv_content: CSV file content as string

    Returns:
        List of validated holdings

    Raises:
        ValidationError: If CSV is invalid or validation fails
    """
    try:
        df = pd.read_csv(pd.io.common.StringIO(csv_content))

        # Validate required columns
        required_columns = ['symbol', 'name', 'type', 'quantity', 'avg_price']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValidationError(
                f"CSV falta columnas requeridas: {', '.join(missing_columns)}"
            )

        # Validate and create holdings
        holdings = []
        for idx, row in df.iterrows():
            try:
                holding = create_holding(
                    symbol=str(row['symbol']),
                    name=str(row['name']),
                    asset_type=str(row['type']),
                    quantity=float(row['quantity']),
                    avg_price=float(row['avg_price']),
                    notes=str(row.get('notes', ''))
                )
                holdings.append(holding)
            except (ValueError, ValidationError) as e:
                logger.warning(f"Skipping invalid row {idx + 1}: {str(e)}")
                continue

        if not holdings:
            raise ValidationError("No se encontraron holdings válidos en el CSV.")

        return holdings

    except pd.errors.EmptyDataError:
        raise ValidationError("El archivo CSV está vacío.")
    except pd.errors.ParserError as e:
        raise ValidationError(f"Error al parsear CSV: {str(e)}")
    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise ValidationError(ERROR_MESSAGES["csv_import_error"])


def get_asset_allocation(portfolio: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Calculate asset allocation by type and value.

    Args:
        portfolio: List of holdings

    Returns:
        DataFrame with asset type, total value, and percentage
    """
    if not portfolio:
        return pd.DataFrame(columns=['type', 'total_value', 'percentage'])

    df = pd.DataFrame(portfolio)
    df['total_value'] = df['quantity'] * df['avg_price']

    allocation = df.groupby('type')['total_value'].sum().reset_index()
    total_value = allocation['total_value'].sum()

    allocation['percentage'] = (allocation['total_value'] / total_value * 100).round(2)

    return allocation
