# portfolio.py
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from utils import plot_area_chart

def portfolio_tracker_page():
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

    st.title(" Portfolio Tracker")

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

        total_value_df = pd.DataFrame()

        for item in st.session_state['portfolio']:
            ticker = yf.Ticker(item['symbol'])
            hist = ticker.history(period=period)

            if hist.empty or "Close" not in hist:
                continue

            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)

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
            st.markdown(f"<h3>Total Portfolio Value Today: ₹{latest_value:,.2f}</h3>", unsafe_allow_html=True)

            total_value_df = total_value_df.reset_index()

            fig = plot_area_chart(
                df=total_value_df,
                x_col='Date',
                y_col='Total Value',
                title="Overall Portfolio Value Over Time",
                y_label="Value (₹)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid historical data found for the selected time range.")
