import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
