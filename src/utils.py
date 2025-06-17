import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_stock_data():
    """
    Loads stock and mutual fund data from CSV.
    """
    return pd.read_csv("data/combined_stocks_yahoo.csv")


def search_bar_selector(key="search"):
    """
    Autocomplete search bar using st.selectbox (native Streamlit behavior).
    Returns selected stock row as a dictionary or None.
    """
    df = load_stock_data()
    df['Display'] = df['Symbol'].astype(str) + " - " + df['Company'].astype(str)

    selected_display = st.selectbox("🔍 Search Stock / Mutual Fund:", df['Display'].tolist(), key=key)

    if selected_display:
        selected_row = df[df['Display'] == selected_display]
        if not selected_row.empty:
            return selected_row.iloc[0].to_dict()

    return None

def plot_area_chart(df, x_col, y_col, title, y_label, line_color='lime', fill_color='rgba(0, 255, 0, 0.2)'):
    """
    Plots a smooth area chart using Plotly.
    """
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
