import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_stock_data():
    """
    Loads stock and mutual fund data from CSV.
    """
    return pd.read_csv("combined_stocks_yahoo.csv")

def search_bar_selector(key="search"):
    """
    Streamlit search bar that loads from combined_stocks_yahoo.csv and returns selected row.

    Args:
        key (str): Streamlit widget key to keep state unique if used in multiple places.

    Returns:
        dict: Selected row as a dictionary (Symbol, Company, Yahoo_Ticker, etc.), or None if not selected.
    """
    df = load_stock_data()
    df['Display'] = df['Symbol'].astype(str) + " - " + df['Company'].astype(str)

    selected_display = st.selectbox(
        "Search Stock / Mutual Fund:",
        options=df['Display'].tolist(),
        key=key
    )

    selected_row = df[df['Display'] == selected_display]
    if not selected_row.empty:
        return selected_row.iloc[0].to_dict()
    return None


def plot_area_chart(df, x_col, y_col, title, y_label, line_color='lime', fill_color='rgba(0, 255, 0, 0.2)'):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        fill='tozeroy',
        mode='lines+markers',
        line=dict(color=line_color, width=2),
        fillcolor=fill_color
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        template="plotly_dark",
        margin=dict(t=40, l=0, r=0, b=0)
    )
    return fig


def search_stock(tickers_df):
    """
    Show a search bar to filter stocks by symbol or name,
    then show a selectbox of matching stocks,
    returns selected stock symbol (string) or None if nothing selected.
    """
    search = st.text_input("Search for a stock (symbol or name):").lower().strip()
    
    if search:
        matches = tickers_df[
            tickers_df['Symbol'].str.lower().str.contains(search) |
            tickers_df['Name'].str.lower().str.contains(search)
        ]
    else:
        matches = tickers_df
    
    if matches.empty:
        st.warning("No matching stocks found.")
        return None

    options = matches['Symbol'] + " - " + matches['Name']
    selected = st.selectbox("Matching Stocks:", options)

    if selected:
        symbol = selected.split(" - ")[0]
        return symbol
    
    return None

