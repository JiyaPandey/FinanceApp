# main.py
import streamlit as st
from stock_analysis import stock_analysis_page
from portfolio import portfolio_tracker_page
import pandas as pd
from utils import search_stock

st.set_page_config(page_title="Finance Dashboard", layout="wide")

tabs = st.tabs(["Stock Analysis", "Portfolio Tracker"])

with tabs[0]:
    stock_analysis_page()

with tabs[1]:
    portfolio_tracker_page()


# Load your tickers DataFrame (e.g., from CSV or fetched NSE + S&P500 list)
#tickers_df = pd.read_csv("tickers_list.csv")  # Make sure this CSV has 'Symbol' and 'Name' columns

#selected_symbol = search_stock(tickers_df)

#if selected_symbol:
    #st.write(f"Selected ticker symbol: {selected_symbol}")
    # Use selected_symbol with yfinance or any other logic...
