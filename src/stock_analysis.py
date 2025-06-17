import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from utils import search_bar_selector, plot_area_chart

def stock_analysis_page():
    st.title(" Stock Analysis")

    # --- Stock selection ---
    selected = search_bar_selector(key="stock_analysis_search")

    if not selected:
        st.info("🔍 Use the search bar above to select a stock or mutual fund.")
        return

    symbol = selected.get('Yahoo_Ticker') or selected.get('Symbol')
    company_name = selected.get('Company') or ""

    st.markdown(f"### {symbol} - {company_name}")

    # --- Time period options ---
    duration_map = {
        '1W': '5d',
        '1M': '1mo',
        '6M': '6mo',
        '1Y': '1y',
        '5Y': '5y',
        'ALL': 'max'
    }

    selected_duration_label = st.radio(
        " Select Time Duration:",
        list(duration_map.keys()), horizontal=True, key="analysis_duration"
    )
    period = duration_map[selected_duration_label]

    # --- Fetch historical data ---
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
        return

    if hist.empty or "Close" not in hist.columns:
        st.warning("⚠️ No historical data available for this stock.")
        return

    if hist.index.tz is not None:
        hist.index = hist.index.tz_localize(None)

    hist.reset_index(inplace=True)
    hist.rename(columns={"Date": "Date", "Close": "Close Price"}, inplace=True)

    # --- Plot chart ---
    fig = plot_area_chart(
        df=hist,
        x_col="Date",
        y_col="Close Price",
        title=f" {symbol} Price Trend",
        y_label="Price (₹)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Recent price table ---
    st.markdown("###  Recent Price Table")
    hist_display = hist[["Date", "Close Price"]].copy()
    hist_display["Date"] = hist_display["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(
        hist_display.tail(10).sort_values("Date", ascending=False),
        use_container_width=True
    )
