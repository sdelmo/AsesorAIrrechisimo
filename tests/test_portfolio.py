"""Tests for portfolio utilities"""
import pytest
import pandas as pd
from src.utils.portfolio import (
    validate_ticker,
    validate_quantity,
    validate_price,
    create_holding,
    update_holding,
    ValidationError,
    export_portfolio_csv,
    import_portfolio_csv,
    calculate_portfolio_value,
    get_asset_allocation,
)


class TestValidation:
    """Test validation functions"""

    def test_validate_ticker_valid(self):
        """Test valid ticker validation"""
        assert validate_ticker("AAPL") is True
        assert validate_ticker("VTI") is True
        assert validate_ticker("BRK.B") is True

    def test_validate_ticker_invalid_empty(self):
        """Test empty ticker validation"""
        with pytest.raises(ValidationError, match="no puede estar vacío"):
            validate_ticker("")

    def test_validate_ticker_invalid_too_long(self):
        """Test too long ticker validation"""
        with pytest.raises(ValidationError, match="no puede tener más de"):
            validate_ticker("VERYLONGTICKER")

    def test_validate_ticker_invalid_characters(self):
        """Test invalid characters in ticker"""
        with pytest.raises(ValidationError):
            validate_ticker("AAP@L")

    def test_validate_quantity_valid(self):
        """Test valid quantity validation"""
        assert validate_quantity(1.0) is True
        assert validate_quantity(100.5) is True

    def test_validate_quantity_invalid_zero(self):
        """Test zero quantity validation"""
        with pytest.raises(ValidationError):
            validate_quantity(0.0)

    def test_validate_quantity_invalid_negative(self):
        """Test negative quantity validation"""
        with pytest.raises(ValidationError):
            validate_quantity(-5.0)

    def test_validate_price_valid(self):
        """Test valid price validation"""
        assert validate_price(0.0) is True
        assert validate_price(150.25) is True

    def test_validate_price_invalid_negative(self):
        """Test negative price validation"""
        with pytest.raises(ValidationError):
            validate_price(-10.0)


class TestHoldingOperations:
    """Test holding create/update operations"""

    def test_create_holding_valid(self):
        """Test creating a valid holding"""
        holding = create_holding(
            symbol="AAPL",
            name="Apple Inc",
            asset_type="Stock",
            quantity=10.0,
            avg_price=150.0,
            notes="Tech stock"
        )

        assert holding["symbol"] == "AAPL"
        assert holding["name"] == "Apple Inc"
        assert holding["type"] == "Stock"
        assert holding["quantity"] == 10.0
        assert holding["avg_price"] == 150.0
        assert holding["notes"] == "Tech stock"
        assert "added_date" in holding

    def test_create_holding_uppercase_symbol(self):
        """Test that symbol is converted to uppercase"""
        holding = create_holding(
            symbol="aapl",
            name="Apple Inc",
            asset_type="Stock",
            quantity=10.0,
            avg_price=150.0
        )
        assert holding["symbol"] == "AAPL"

    def test_create_holding_invalid_symbol(self):
        """Test creating holding with invalid symbol"""
        with pytest.raises(ValidationError):
            create_holding(
                symbol="",
                name="Test",
                asset_type="Stock",
                quantity=10.0,
                avg_price=150.0
            )

    def test_create_holding_invalid_quantity(self):
        """Test creating holding with invalid quantity"""
        with pytest.raises(ValidationError):
            create_holding(
                symbol="AAPL",
                name="Apple Inc",
                asset_type="Stock",
                quantity=0.0,
                avg_price=150.0
            )

    def test_update_holding_quantity(self):
        """Test updating holding quantity"""
        original = {
            "symbol": "AAPL",
            "name": "Apple Inc",
            "type": "Stock",
            "quantity": 10.0,
            "avg_price": 150.0,
            "notes": ""
        }

        updated = update_holding(original, quantity=20.0)

        assert updated["quantity"] == 20.0
        assert updated["symbol"] == original["symbol"]
        assert "updated_date" in updated

    def test_update_holding_price(self):
        """Test updating holding price"""
        original = {
            "symbol": "AAPL",
            "quantity": 10.0,
            "avg_price": 150.0
        }

        updated = update_holding(original, avg_price=160.0)
        assert updated["avg_price"] == 160.0

    def test_update_holding_notes(self):
        """Test updating holding notes"""
        original = {
            "symbol": "AAPL",
            "quantity": 10.0,
            "avg_price": 150.0,
            "notes": "old note"
        }

        updated = update_holding(original, notes="new note")
        assert updated["notes"] == "new note"


class TestPortfolioCalculations:
    """Test portfolio calculation functions"""

    def test_calculate_portfolio_value(self):
        """Test portfolio value calculation"""
        portfolio = [
            {"symbol": "AAPL", "quantity": 10, "avg_price": 150.0},
            {"symbol": "VTI", "quantity": 5, "avg_price": 200.0}
        ]

        total = calculate_portfolio_value(portfolio)
        assert total == 2500.0  # (10 * 150) + (5 * 200)

    def test_calculate_portfolio_value_empty(self):
        """Test empty portfolio value"""
        assert calculate_portfolio_value([]) == 0.0

    def test_get_asset_allocation(self):
        """Test asset allocation calculation"""
        portfolio = [
            {"symbol": "AAPL", "type": "Stock", "quantity": 10, "avg_price": 100.0},
            {"symbol": "VTI", "type": "ETF", "quantity": 5, "avg_price": 200.0},
            {"symbol": "MSFT", "type": "Stock", "quantity": 5, "avg_price": 200.0}
        ]

        allocation = get_asset_allocation(portfolio)

        assert len(allocation) == 2  # Stock and ETF
        assert allocation[allocation['type'] == 'Stock']['total_value'].sum() == 2000.0
        assert allocation[allocation['type'] == 'ETF']['total_value'].sum() == 1000.0

    def test_get_asset_allocation_empty(self):
        """Test empty portfolio allocation"""
        allocation = get_asset_allocation([])
        assert len(allocation) == 0


class TestCSVOperations:
    """Test CSV import/export functions"""

    def test_export_portfolio_csv(self):
        """Test exporting portfolio to CSV"""
        portfolio = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc",
                "type": "Stock",
                "quantity": 10,
                "avg_price": 150.0,
                "notes": "Test"
            }
        ]

        csv_output = export_portfolio_csv(portfolio)

        assert "symbol" in csv_output
        assert "AAPL" in csv_output
        assert "Apple Inc" in csv_output

    def test_import_portfolio_csv_valid(self):
        """Test importing valid CSV"""
        csv_content = """symbol,name,type,quantity,avg_price,notes
AAPL,Apple Inc,Stock,10,150.0,Test note
VTI,Vanguard Total,ETF,5,200.0,"""

        holdings = import_portfolio_csv(csv_content)

        assert len(holdings) == 2
        assert holdings[0]["symbol"] == "AAPL"
        assert holdings[1]["symbol"] == "VTI"

    def test_import_portfolio_csv_missing_columns(self):
        """Test importing CSV with missing columns"""
        csv_content = """symbol,name
AAPL,Apple Inc"""

        with pytest.raises(ValidationError, match="columnas requeridas"):
            import_portfolio_csv(csv_content)

    def test_import_portfolio_csv_empty(self):
        """Test importing empty CSV"""
        with pytest.raises(ValidationError):
            import_portfolio_csv("")

    def test_import_portfolio_csv_invalid_data(self):
        """Test importing CSV with invalid data - should skip invalid rows"""
        csv_content = """symbol,name,type,quantity,avg_price
AAPL,Apple Inc,Stock,10,150.0
INVALID@,Bad Stock,Stock,-5,100.0
VTI,Vanguard Total,ETF,5,200.0"""

        holdings = import_portfolio_csv(csv_content)

        # Should import valid rows and skip invalid ones
        assert len(holdings) == 2
        assert holdings[0]["symbol"] == "AAPL"
        assert holdings[1]["symbol"] == "VTI"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
