import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

def detect_columns(df):
    date_col, category_col, amount_col = None, None, None

    # Detect Date column
    for col in df.columns:
        try:
            parsed = pd.to_datetime(df[col], errors='coerce')
            if parsed.notnull().sum() > len(df) * 0.5:
                date_col = col
                break
        except Exception:
            continue

    # Detect Amount column (numeric)
    for col in df.columns:
        if col != date_col and pd.api.types.is_numeric_dtype(df[col]):
            amount_col = col
            break

    # Detect Category column (non-numeric, not date)
    for col in df.columns:
        if col not in [date_col, amount_col]:
            category_col = col
            break

    if not all([date_col, category_col, amount_col]):
        return None, None, None

    return date_col, category_col, amount_col


def expense_tracker_page():
    st.title(" Expense Tracker")

    # Initialize session state
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = datetime.now().month

    # --- Month Selection UI ---
    with st.container():
        st.markdown("####  Select Month")
        center_col = st.columns([1, 2, 1])

        with center_col[0]:
            prev = st.button("⬅️", use_container_width=True)

        with center_col[1]:
            selected_month = st.session_state.selected_month
            month_name = calendar.month_name[selected_month]
            st.markdown(
                f"""
                <div style='
                    text-align: center;
                    padding: 10px 0;
                    border: 1px solid #999;
                    border-radius: 10px;
                    background-color: #2c3e50;
                    color: white;
                    font-weight: bold;
                    font-size: 20px;
                    width: 100%;'>
                    {month_name}
                </div>
                """,
                unsafe_allow_html=True
            )

        with center_col[2]:
            nxt = st.button("➡️", use_container_width=True)

        if prev:
            st.session_state.selected_month = 12 if selected_month == 1 else selected_month - 1
        elif nxt:
            st.session_state.selected_month = 1 if selected_month == 12 else selected_month + 1

    st.markdown("---")

    # --- File Upload ---
    uploaded_file = st.file_uploader("📎 Upload CSV or Excel file (must include Date, Category, Amount)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"❌ Failed to read file: {e}")
            return

        date_col, category_col, amount_col = detect_columns(df)

        if not all([date_col, category_col, amount_col]):
            st.error("❌ Could not detect required columns (Date, Category, Amount). Try renaming them.")
            return

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])
        df["Month"] = df[date_col].dt.month

        current_month = st.session_state.selected_month
        filtered_df = df[df["Month"] == current_month]

        if filtered_df.empty:
            st.info(" No expenses found for this month.")
        else:
            display_df = filtered_df[[date_col, category_col, amount_col]].copy()
            display_df.columns = ["Date/Time", "Category", "Amount"]
            display_df["Date/Time"] = pd.to_datetime(display_df["Date/Time"]).dt.strftime("%Y-%m-%d %H:%M")

            # 💳 Category Cards
            st.markdown("###  Category Breakdown")
            category_summary = (
                filtered_df.groupby(category_col)[amount_col].sum()
                .reset_index()
                .rename(columns={category_col: "Category", amount_col: "Total"})
            )
            total_amount = category_summary["Total"].sum()
            cols = st.columns(len(category_summary))

            for idx, row in category_summary.iterrows():
                with cols[idx]:
                    percent = (row["Total"] / total_amount) * 100
                    st.markdown(
                        f"""
                        <div style="
                            padding: 15px;
                            border-radius: 12px;
                            background-color: #ffffff;
                            border: 1px solid #cccccc;
                            box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
                            text-align: center;
                            margin: 5px 0;
                            min-height: 100px;">
                            <h5 style='margin: 0; color: #333333; font-size: 16px;'>{row["Category"]}</h5>
                            <p style='margin: 8px 0 4px; font-size: 20px; color: #2e7d32; font-weight: bold;'>₹{row["Total"]:,.0f}</p>
                            <p style='margin: 0; color: #888888;'>{percent:.1f}%</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # 📋 Monthly Table
            with st.expander(" View Monthly Expenses", expanded=True):
                st.dataframe(display_df, use_container_width=True, height=400)

            total = display_df["Amount"].sum()
            st.markdown(
                f"<h4 style='text-align:right; color:green;'> Total: ₹{total:,.2f}</h4>",
                unsafe_allow_html=True
            )
