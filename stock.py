import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=30 * 1000, key="auto-refresh")

available_stocks = {
    "Motilal Oswal Midcap": "0P00012ALS.BO",
    "Facebook (Meta)": "META",
    "Netflix": "NFLX"
}

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

with tab2:
    st.header("Portfolio Tracker")

    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = []

    with st.form("portfolio_form"):
        stock_choice = st.selectbox("Select Stock:", list(available_stocks.keys()))
        buy_date = st.date_input("Buy Date", value=datetime.today())
        units = st.number_input("Units Owned", min_value=0.0, step=0.01, format="%.2f")

        submitted = st.form_submit_button("Add to Portfolio")

        if submitted:
            # If the stock is already in portfolio, add units & update buy date if earlier
            found = False
            for item in st.session_state['portfolio']:
                if item['stock'] == stock_choice:
                    item['units'] += units
                    if buy_date < item['buy_date']:
                        item['buy_date'] = buy_date
                    found = True
                    break
            if not found:
                st.session_state['portfolio'].append({
                    "stock": stock_choice,
                    "symbol": available_stocks[stock_choice],
                    "buy_date": buy_date,
                    "units": units
                })
            st.success(f"Added {units:.2f} units of {stock_choice} bought on {buy_date}")

    if st.session_state['portfolio']:
        st.markdown("### Portfolio Summary")

        min_buy_date = min([item['buy_date'] for item in st.session_state['portfolio']])
        start_date = min_buy_date.strftime("%Y-%m-%d")
        end_date = datetime.today().strftime("%Y-%m-%d")

        # Create empty DataFrame with all dates in range
        portfolio_value_df = pd.DataFrame()

        for item in st.session_state['portfolio']:
            ticker = yf.Ticker(item['symbol'])
            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                continue

            hist = hist[['Close']].copy()
            hist.rename(columns={'Close': item['stock']}, inplace=True)
            hist.index = pd.to_datetime(hist.index)

            # Multiply closing prices by units
            hist[item['stock']] = hist[item['stock']] * item['units']

            if portfolio_value_df.empty:
                portfolio_value_df = hist
            else:
                portfolio_value_df = portfolio_value_df.join(hist, how='outer')

        # Fill missing values with 0 (in case some stocks don't trade every day)
        portfolio_value_df.fillna(0, inplace=True)

        # Sum across stocks to get total portfolio value
        portfolio_value_df['Total Value'] = portfolio_value_df.sum(axis=1)

        # Calculate change & color for graph
        first_value = portfolio_value_df['Total Value'].iloc[0]
        last_value = portfolio_value_df['Total Value'].iloc[-1]
        change = last_value - first_value
        change_color = "green" if change >= 0 else "red"

        # Show portfolio total value today
        st.markdown(
            f"<h3>Total Portfolio Value Today: ₹{last_value:,.2f}</h3>",
            unsafe_allow_html=True
        )

        # Mountain chart of total portfolio value over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=portfolio_value_df.index,
            y=portfolio_value_df['Total Value'],
            fill='tozeroy',
            mode='lines',
            line=dict(color=change_color),
            fillcolor='rgba(0, 255, 0, 0.2)' if change >= 0 else 'rgba(255, 0, 0, 0.2)'
        ))
        fig.update_layout(
            title="Portfolio Total Value Over Time",
            xaxis_title="Date",
            yaxis_title="Value (₹)",
            template="plotly_dark",
            margin=dict(t=40, l=0, r=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
