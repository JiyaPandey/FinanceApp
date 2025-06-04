import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from utils import search_bar_selector, load_stock_data
from utils import plot_area_chart


@st.cache_data
def load_stock_data():
    return pd.read_csv("combined_stocks_yahoo.csv")

# utils.py
import streamlit as st
import pandas as pd

@st.cache_data
def load_stock_data():
    return pd.read_csv("combined_stocks_yahoo.csv")

def search_bar_selector(key="search"):
    df = load_stock_data()
    df['Display'] = df['Symbol'].astype(str) + " - " + df['Company'].astype(str)

    query = st.text_input("Search Stock / Mutual Fund:", key=key)

    if not query:
        return None

    # Case-insensitive partial match
    filtered_df = df[df['Display'].str.contains(query, case=False, na=False)]

    if filtered_df.empty:
        st.warning("No matching stock or mutual fund found.")
        return None

    selected_display = st.selectbox(
        "Select from matched results:",
        options=filtered_df['Display'].tolist(),
        key=key + "_select"
    )

    selected_row = filtered_df[filtered_df['Display'] == selected_display]
    if not selected_row.empty:
        return selected_row.iloc[0].to_dict()
    return None



def portfolio_tracker_page():
    duration_map = {
        '1W': '5d',
        '1M': '1mo',
        '6M': '6mo',
        '1Y': '1y',
        '5Y': '5y',
        'ALL': 'max'
    }

    st.title("📊 Portfolio Tracker")

    if 'portfolio' not in st.session_state:
        st.session_state['portfolio'] = []

    # ---- Add new stock to portfolio form ----
    with st.form("portfolio_form"):
        selected = search_bar_selector(key="portfolio_search")

        buy_date = st.date_input("📅 Buy Date", value=datetime.today())
        units = st.number_input("📦 Units Owned", min_value=0.0, step=0.001, format="%.5f")

        submitted = st.form_submit_button("➕ Add to Portfolio")

        if submitted:
            if selected and units > 0:
                st.session_state['portfolio'].append({
                    "stock": selected['Display'],
                    "symbol": selected['Yahoo_Ticker'],
                    "buy_date": buy_date,
                    "units": units
                })
                st.success(f"✅ Added {units:.2f} units of {selected['Display']} bought on {buy_date}")
                st.rerun()
            else:
                st.error("Please select a valid stock and enter units > 0.")

    # ---- Portfolio display ----
    if st.session_state['portfolio']:
        st.markdown("### 💼 Portfolio Summary")

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
            "⏳ Select Time Duration:",
            list(duration_map.keys()), horizontal=True, key="portfolio_duration"
        )
        period = duration_map[selected_duration_label]

        total_value_df = pd.DataFrame()

        for item in st.session_state['portfolio']:
            ticker = yf.Ticker(item['symbol'])
            hist = ticker.history(period=period)

            if hist.empty or "Close" not in hist:
                st.warning(f"No data found for {item['stock']} ({item['symbol']})")
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
                total_value_df = total_value_df.join(hist, how="outer", rsuffix=f"_{item['symbol']}")

        if not total_value_df.empty:
            total_value_df.fillna(0, inplace=True)
            total_value_df['Total Value'] = total_value_df.sum(axis=1)
            latest_value = total_value_df['Total Value'].iloc[-1]

            st.markdown(f"<h3>📈 Total Portfolio Value Today: ₹{latest_value:,.2f}</h3>", unsafe_allow_html=True)

            total_value_df = total_value_df.reset_index()
            total_value_df.rename(columns={"index": "Date"}, inplace=True)

            fig = plot_area_chart(
                df=total_value_df,
                x_col='Date',
                y_col='Total Value',
                title="📉 Overall Portfolio Value Over Time",
                y_label="Value (₹)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ No valid historical data found for the selected time range.")
    else:
        st.info("📝 Your portfolio is empty. Use the form above to add stocks or mutual funds.")
