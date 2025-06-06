# main.py
import streamlit as st
from stock_analysis import stock_analysis_page
from portfolio import portfolio_tracker_page
from expense_tracker import expense_tracker_page 
from utils import *
import pandas as pd


st.set_page_config(page_title="Finance App", layout="wide")

# ✅ Add third tab label
tabs = st.tabs(["Stock Analysis", "Portfolio", "Expense Tracker"])

with tabs[0]:
    stock_analysis_page()

with tabs[1]:
    portfolio_tracker_page()

with tabs[2]:
    expense_tracker_page()  
