"""Portfolio management tab with CRUD operations"""
import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from typing import Optional

from src.utils.portfolio import (
    create_holding,
    update_holding,
    export_portfolio_csv,
    import_portfolio_csv,
    get_current_price,
    ValidationError,
)
from src.config import AssetType, SUCCESS_MESSAGES, ERROR_MESSAGES

logger = logging.getLogger(__name__)


def render_portfolio_tab() -> None:
    """Render the portfolio management tab with full CRUD operations."""
    st.header("Gestión del Portafolio")

    # Import/Export section at the top
    _render_import_export_section()

    st.divider()

    # Add new holding
    _render_add_holding_section()

    st.divider()

    # Display and manage existing portfolio
    if st.session_state.portfolio:
        _render_portfolio_display()
        st.divider()
        _render_edit_section()
        st.divider()
        _render_remove_section()
    else:
        st.info("👆 Agrega tu primer holding o importa un portafolio CSV para empezar!")


def _render_import_export_section() -> None:
    """Render CSV import/export section."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 Importar Portafolio")
        uploaded_file = st.file_uploader(
            "Sube un archivo CSV",
            type="csv",
            help="El CSV debe tener las columnas: symbol, name, type, quantity, avg_price"
        )

        if uploaded_file is not None:
            try:
                csv_content = uploaded_file.read().decode('utf-8')
                imported_holdings = import_portfolio_csv(csv_content)

                # Ask for confirmation
                st.warning(
                    f"Se encontraron {len(imported_holdings)} holdings. "
                    "¿Deseas reemplazar o agregar al portafolio actual?"
                )

                col_replace, col_append = st.columns(2)

                with col_replace:
                    if st.button("🔄 Reemplazar", key="import_replace"):
                        st.session_state.portfolio = imported_holdings
                        st.success(SUCCESS_MESSAGES["portfolio_imported"].format(len(imported_holdings)))
                        st.rerun()

                with col_append:
                    if st.button("➕ Agregar", key="import_append"):
                        st.session_state.portfolio.extend(imported_holdings)
                        st.success(f"✓ {len(imported_holdings)} holdings agregados!")
                        st.rerun()

            except ValidationError as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"CSV import validation error: {str(e)}")
            except Exception as e:
                st.error(ERROR_MESSAGES["csv_import_error"])
                logger.error(f"Unexpected CSV import error: {str(e)}")

    with col2:
        st.subheader("📤 Exportar Portafolio")
        if st.session_state.portfolio:
            csv = export_portfolio_csv(st.session_state.portfolio)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Agrega holdings primero para exportar.")


def _render_add_holding_section() -> None:
    """Render section for adding new holdings."""
    with st.expander("➕ Agregar Nueva Posición", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            symbol = st.text_input("Símbolo/Ticker", placeholder="ej. VTI, AAPL, AGG", key="add_symbol")
            asset_type = st.selectbox("Tipo de Activo", AssetType.get_all_values(), key="add_type")

        with col2:
            name = st.text_input("Nombre", placeholder="ej. Vanguard Total Stock Market", key="add_name")
            quantity = st.number_input("Cantidad/Acciones", min_value=0.0, step=0.01, key="add_quantity")

        with col3:
            avg_price = st.number_input("Precio Promedio ($)", min_value=0.0, step=0.01, key="add_price")

            # Option to fetch current price
            if symbol and st.button("🔍 Obtener Precio Actual", key="fetch_price"):
                with st.spinner(f"Buscando precio de {symbol}..."):
                    current_price = get_current_price(symbol.upper())
                    if current_price:
                        st.session_state.fetched_price = current_price
                        st.success(f"Precio actual: ${current_price:.2f}")
                    else:
                        st.warning(ERROR_MESSAGES["price_fetch_error"])

            # Use fetched price if available
            if hasattr(st.session_state, 'fetched_price') and st.session_state.fetched_price:
                if st.button("✓ Usar Precio Actual", key="use_fetched_price"):
                    st.session_state.add_price_value = st.session_state.fetched_price
                    st.rerun()

        notes = st.text_input("Notas (opcional)", placeholder="Info adicional", key="add_notes")

        if st.button("➕ Agregar Holding", type="primary"):
            try:
                # Use fetched price if set
                final_price = st.session_state.get('add_price_value', avg_price)

                holding = create_holding(
                    symbol=symbol,
                    name=name,
                    asset_type=asset_type,
                    quantity=quantity,
                    avg_price=final_price if final_price > 0 else avg_price,
                    notes=notes
                )

                st.session_state.portfolio.append(holding)
                st.success(SUCCESS_MESSAGES["holding_added"].format(symbol.upper()))

                # Clear fetched price
                if hasattr(st.session_state, 'fetched_price'):
                    del st.session_state.fetched_price

                st.rerun()

            except ValidationError as e:
                st.error(f"Error de validación: {str(e)}")
            except Exception as e:
                st.error(f"Error al agregar holding: {str(e)}")
                logger.error(f"Error adding holding: {str(e)}")


def _render_portfolio_display() -> None:
    """Display current portfolio with metrics and charts."""
    df = pd.DataFrame(st.session_state.portfolio)

    # Calculate values
    df['Total Value'] = df['quantity'] * df['avg_price']

    # Option to show current prices
    show_current = st.checkbox("📊 Mostrar precios actuales", value=False, key="show_current_prices")

    if show_current:
        with st.spinner("Obteniendo precios actuales..."):
            current_prices = []
            for holding in st.session_state.portfolio:
                price = get_current_price(holding['symbol'])
                current_prices.append(price if price else holding['avg_price'])

            df['Current Price'] = current_prices
            df['Current Value'] = df['quantity'] * df['Current Price']
            df['Gain/Loss'] = df['Current Value'] - df['Total Value']
            df['Gain/Loss %'] = ((df['Current Price'] / df['avg_price'] - 1) * 100).round(2)

            # Display with current prices
            display_cols = ['symbol', 'name', 'type', 'quantity', 'avg_price', 'Current Price', 'Current Value', 'Gain/Loss', 'Gain/Loss %', 'notes']
        else:
            display_cols = ['symbol', 'name', 'type', 'quantity', 'avg_price', 'Total Value', 'notes']

    st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True
    )

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Holdings", len(df))

    with col2:
        total_value = df['Current Value'].sum() if show_current and 'Current Value' in df else df['Total Value'].sum()
        st.metric("Valor del Portafolio", f"${total_value:,.2f}")

    with col3:
        st.metric("ETFs", len(df[df['type'] == 'ETF']))

    with col4:
        st.metric("Acciones", len(df[df['type'] == 'Stock']))

    # Asset allocation
    if 'type' in df.columns:
        st.subheader("Asignación de Activos")

        # Calculate allocation by value
        allocation = df.groupby('type')['Total Value'].sum()

        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            st.bar_chart(allocation)

        with col_table:
            allocation_df = allocation.reset_index()
            allocation_df.columns = ['Tipo', 'Valor Total']
            total = allocation_df['Valor Total'].sum()
            allocation_df['Porcentaje'] = (allocation_df['Valor Total'] / total * 100).round(2)
            st.dataframe(allocation_df, hide_index=True)


def _render_edit_section() -> None:
    """Render section for editing existing holdings."""
    st.subheader("✏️ Editar Holding")

    if st.session_state.portfolio:
        # Select holding to edit
        holding_options = [
            f"{h['symbol']} - {h['name']}"
            for h in st.session_state.portfolio
        ]

        selected_idx = st.selectbox(
            "Selecciona holding para editar:",
            options=range(len(st.session_state.portfolio)),
            format_func=lambda x: holding_options[x],
            key="edit_select"
        )

        selected_holding = st.session_state.portfolio[selected_idx]

        # Edit form
        col1, col2 = st.columns(2)

        with col1:
            new_quantity = st.number_input(
                "Nueva Cantidad",
                min_value=0.0,
                value=float(selected_holding['quantity']),
                step=0.01,
                key="edit_quantity"
            )

        with col2:
            new_price = st.number_input(
                "Nuevo Precio Promedio ($)",
                min_value=0.0,
                value=float(selected_holding['avg_price']),
                step=0.01,
                key="edit_price"
            )

        new_notes = st.text_input(
            "Notas",
            value=selected_holding.get('notes', ''),
            key="edit_notes"
        )

        if st.button("💾 Guardar Cambios", type="primary", key="save_edit"):
            try:
                updated = update_holding(
                    holding=selected_holding,
                    quantity=new_quantity,
                    avg_price=new_price,
                    notes=new_notes
                )

                st.session_state.portfolio[selected_idx] = updated
                st.success(SUCCESS_MESSAGES["holding_updated"].format(selected_holding['symbol']))
                st.rerun()

            except ValidationError as e:
                st.error(f"Error de validación: {str(e)}")
            except Exception as e:
                st.error(f"Error al actualizar holding: {str(e)}")
                logger.error(f"Error updating holding: {str(e)}")


def _render_remove_section() -> None:
    """Render section for removing holdings with confirmation."""
    st.subheader("🗑️ Eliminar Holding")

    if st.session_state.portfolio:
        holding_options = [
            f"{h['symbol']} - {h['name']}"
            for h in st.session_state.portfolio
        ]

        selected_idx = st.selectbox(
            "Selecciona holding para eliminar:",
            options=range(len(st.session_state.portfolio)),
            format_func=lambda x: holding_options[x],
            key="remove_select"
        )

        selected_holding = st.session_state.portfolio[selected_idx]

        # Confirmation checkbox
        confirm = st.checkbox(
            f"⚠️ Confirmo que quiero eliminar {selected_holding['symbol']}",
            key="remove_confirm"
        )

        if st.button("🗑️ Eliminar Holding", disabled=not confirm, key="remove_button"):
            removed = st.session_state.portfolio.pop(selected_idx)
            st.success(SUCCESS_MESSAGES["holding_removed"].format(removed['symbol']))
            st.rerun()
