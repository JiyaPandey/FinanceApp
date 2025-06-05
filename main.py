# main.py
import streamlit as st
from stock_analysis import stock_analysis_page
from portfolio import portfolio_tracker_page
import pandas as pd
from utils import *

st.set_page_config(page_title="Finance App", layout="wide")

tabs = st.tabs(["Stock Analysis", "Portfolio"])

with tabs[0]:
    stock_analysis_page()

with tabs[1]:
    portfolio_tracker_page()


