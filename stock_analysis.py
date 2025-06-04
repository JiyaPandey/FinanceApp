# stock_analysis.py

import streamlit as st
import yfinance as yf
import pandas as pd
from utils import plot_area_chart
from utils import search_bar_selector, load_stock_data


def stock_analysis_page():
    duration_map = {
        '1W': '5d',
        '1M': '1mo',
        '6M': '6mo',
        '1Y': '1y',
        '5Y': '5y',
        'ALL': 'max'
    }

    st.title("Stock / Mutual Fund Analysis")

    selected_entry = search_bar_selector()
    if not selected_entry:
        st.info("Please search and select a stock or mutual fund to begin.")
        return

    yahoo_symbol = selected_entry.get("Yahoo_Ticker")
    display_name = f"{selected_entry.get('Symbol')} - {selected_entry.get('Company')}"

    selected_duration_label = st.radio("Select Time Duration:", list(duration_map.keys()), horizontal=True)
    period = duration_map[selected_duration_label]

    ticker = yf.Ticker(yahoo_symbol)
    data = ticker.history(period=period)

    st.markdown("### Current Price")
    if not data.empty:
        data.reset_index(inplace=True)
        current_price = ticker.info.get("currentPrice", None) or data["Close"].iloc[-1]
        change = data["Close"].iloc[-1] - data["Close"].iloc[0]
        percent_change = (change / data["Close"].iloc[0]) * 100
        change_color = "green" if change >= 0 else "red"

        st.markdown(
            f"<h3 style='color:{change_color};'>{current_price:.2f} "
            f"{change:+.2f} ({percent_change:+.2f}%) past {selected_duration_label}</h3>",
            unsafe_allow_html=True
        )

        fig = plot_area_chart(
            df=data,
            x_col="Date",
            y_col="Close",
            title=f"{display_name} - Closing Prices ({selected_duration_label})",
            y_label="Price",
            line_color=change_color,
            fill_color='rgba(0, 255, 0, 0.2)' if change >= 0 else 'rgba(255, 0, 0, 0.2)'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data found for the selected duration.")
