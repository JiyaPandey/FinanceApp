import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30 * 1000, key="auto-refresh")

# Stocks to choose from
available_stocks = {
    "Motilal Oswal Midcap": "0P00012ALS.BO",
    "Facebook (Meta)": "META",
    "Netflix": "NFLX"
}

# Time period mappings
duration_map = {
    '1W': '5d',
    '1M': '1mo',
    '6M': '6mo',
    '1Y': '1y',
    '5Y': '5y',
    'ALL': 'max'
}

st.title("Stock Price Analysis & Portfolio Tracker")
tab1, tab2 = st.tabs(["Stock Analysis", "Portfolio"])

# --------------- TAB 1: STOCK ANALYSIS ------------------
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_stock = st.selectbox("Select Stock:", list(available_stocks.keys()))
    with col2:
        selected_duration_label = st.radio("Select Time Duration:", list(duration_map.keys()), horizontal=True)

    ticker_symbol = available_stocks[selected_stock]
    period = duration_map[selected_duration_label]
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=period)

    st.markdown("### Current Price")
    try:
        current_price = ticker.info.get("currentPrice", None)
        if data.empty:
            st.warning("No historical data found.")
        else:
            data.reset_index(inplace=True)
            latest_close = data["Close"].iloc[-1]
            first_close = data["Close"].iloc[0]
            change = latest_close - first_close
            percent_change = (change / first_close) * 100
            change_color = "green" if change >= 0 else "red"
            price_to_show = current_price if current_price else latest_close

            st.markdown(
                f"<h3 style='color:{change_color};'>{price_to_show:.2f} INR "
                f"{change:+.2f} ({percent_change:+.2f}%) past {selected_duration_label}</h3>",
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"Error fetching price: {e}")

    if not data.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data["Date"],
            y=data["Close"],
            fill='tozeroy',
            mode='lines',
            line=dict(color=change_color),
            fillcolor='rgba(0, 255, 0, 0.2)' if change >= 0 else 'rgba(255, 0, 0, 0.2)'
        ))
        fig.update_layout(
            title=f"{selected_stock} - Closing Prices ({selected_duration_label})",
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            template="plotly_dark",
            margin=dict(t=40, l=0, r=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

# --------------- TAB 2: PORTFOLIO TRACKER ------------------
with tab2:
    st.header("Portfolio Tracker")

    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = []

    with st.form("portfolio_form"):
        stock_choice = st.selectbox("Select Stock:", list(available_stocks.keys()))
        buy_date = st.date_input("Buy Date", value=datetime.today())
        units = st.number_input("Units Owned", min_value=0.0, step=0.001, format="%.5f")
        submitted = st.form_submit_button("Add to Portfolio")

        if submitted and units > 0:
            st.session_state['portfolio'].append({
                "stock": stock_choice,
                "symbol": available_stocks[stock_choice],
                "buy_date": buy_date,
                "units": units
            })
            st.success(f"✅ Added {units:.2f} units of {stock_choice} bought on {buy_date}")
            st.rerun()

    if st.session_state['portfolio']:
        st.markdown("### Portfolio Summary")

        # Create column headers
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])
        col1.markdown("**Stock**")
        col2.markdown("**Buy Date**")
        col3.markdown("**Units**")
        col4.markdown("**Symbol**")
        col5.markdown("**Delete**")

        for i, item in enumerate(st.session_state['portfolio']):
            col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])
            col1.write(item['stock'])
            col2.write(item['buy_date'].strftime("%Y-%m-%d"))
            col3.write(f"{item['units']:.4f}")
            col4.write(item['symbol'])
            if col5.button("🗑️", key=f"del_{i}"):
                st.session_state['portfolio'].pop(i)
                st.rerun()

        st.markdown("---")
        selected_duration_label = st.radio(
            "Select Time Duration:",
            list(duration_map.keys()), horizontal=True, key="portfolio_duration"
        )
        period = duration_map[selected_duration_label]

        # Create total portfolio value DataFrame
        total_value_df = pd.DataFrame()

        for item in st.session_state['portfolio']:
            ticker = yf.Ticker(item['symbol'])
            hist = ticker.history(period=period)

            if hist.empty or "Close" not in hist:
                continue

            # Fix timezone issue
            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)

            # Calculate value only from buy date onward
            buy_date_ts = pd.Timestamp(item['buy_date'])
            hist['Value'] = hist["Close"] * item['units']
            hist.loc[hist.index < buy_date_ts, 'Value'] = 0

            hist = hist[['Value']].copy()

            if total_value_df.empty:
                total_value_df = hist
            else:
                total_value_df = total_value_df.join(hist, how="outer", rsuffix='_dup')

        if not total_value_df.empty:
            total_value_df.fillna(0, inplace=True)
            total_value_df['Total Value'] = total_value_df.sum(axis=1)

            latest_value = total_value_df['Total Value'].iloc[-1]
            st.markdown(
                f"<h3> Total Portfolio Value Today: ₹{latest_value:,.2f}</h3>",
                unsafe_allow_html=True
            )

            # Plot portfolio value
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=total_value_df.index,
                y=total_value_df['Total Value'],
                fill='tozeroy',
                mode='lines+markers',
                name='Total Value',
                line=dict(color='lime', width=2)
            ))

            fig.update_layout(
                title="Overall Portfolio Value Over Time",
                xaxis_title="Date",
                yaxis_title="Value (₹)",
                template="plotly_dark",
                margin=dict(t=40, l=0, r=0, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid historical data found for the selected time range.")
