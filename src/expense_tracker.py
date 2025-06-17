import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

    return date_col, category_col, amount_col


def expense_tracker_page():
    st.title(" Expense Tracker")

    # Initialize month selector state
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = datetime.now().month

    with st.container():
        st.markdown("####  Select Month")
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️", use_container_width=True):
                st.session_state.selected_month = 12 if st.session_state.selected_month == 1 else st.session_state.selected_month - 1

        with col2:
            selected_month = st.session_state.selected_month
            month_name = calendar.month_name[selected_month]
            st.markdown(
                f"""
                <div style='
                    text-align: center;
                    padding: 10px 0;
                    border: 1px solid #444;
                    border-radius: 10px;
                    background-color: #111;
                    color: white;
                    font-weight: bold;
                    font-size: 20px;'>
                    {month_name}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            if st.button("➡️", use_container_width=True):
                st.session_state.selected_month = 1 if st.session_state.selected_month == 12 else st.session_state.selected_month + 1

    st.markdown("---")

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
            return

        # --- Graph Section ---
        graph_type = st.radio(" Select Graph Type", ["Bar Chart", "Line Chart"], horizontal=True)

        # Classify income/expense
        income_keywords = ["income", "salary", "credit"]
        df["Type"] = df[category_col].apply(lambda x: "Income" if any(k in str(x).lower() for k in income_keywords) else "Expense")

        summary = df.groupby(["Month", "Type"])[amount_col].sum().unstack(fill_value=0).reindex(range(1, 13), fill_value=0)
        months = [calendar.month_abbr[m] for m in range(1, 13)]

        fig = go.Figure()

        if graph_type == "Bar Chart":
            fig.add_trace(go.Bar(
                x=months,
                y=summary.get("Income", 0),
                name="Income",
                marker_color="#313536"  # Sky Blue
            ))
            fig.add_trace(go.Bar(
                x=months,
                y=summary.get("Expense", 0),
                name="Expense",
                marker_color="#07472A"  # Red
            ))
            fig.update_layout(barmode='group')
        else:
            fig.add_trace(go.Scatter(
                x=months,
                y=summary.get("Income", 0),
                mode='lines+markers',
                name="Income",
                line=dict(color='#1f77b4', width=3),
                marker=dict(color='white', line=dict(color='#1f77b4', width=2))
            ))
            fig.add_trace(go.Scatter(
                x=months,
                y=summary.get("Expense", 0),
                mode='lines+markers',
                name="Expense",
                line=dict(color='#d62728', width=3),
                marker=dict(color='white', line=dict(color='#d62728', width=2))
            ))

        fig.update_layout(
            title=" Monthly Income vs Expenses",
            xaxis_title="Month",
            yaxis_title="Amount (₹)",
            plot_bgcolor="#111111",
            paper_bgcolor="#111111",
            font=dict(color="#e0e0e0"),
            xaxis=dict(showgrid=True, gridcolor="#333"),
            yaxis=dict(showgrid=True, gridcolor="#333"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- Category Cards ---
        st.markdown("### 🧾 Category Breakdown")
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
                    <div style="padding: 15px; border-radius: 12px; background-color: #222;
                    border: 1px solid #444; box-shadow: 2px 2px 8px rgba(0,0,0,0.5);
                    text-align: center; min-height: 100px;">
                        <h5 style='margin: 0; color: #f0f0f0; font-size: 16px;'>{row["Category"]}</h5>
                        <p style='margin: 8px 0 4px; font-size: 20px; color: #4caf50; font-weight: bold;'>₹{row["Total"]:,.0f}</p>
                        <p style='margin: 0; color: #aaaaaa;'>{percent:.1f}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # --- Table View ---
        st.markdown("###  Expense Table")
        display_df = filtered_df[[date_col, category_col, amount_col]].copy()
        display_df.columns = ["Date/Time", "Category", "Amount"]
        display_df["Date/Time"] = pd.to_datetime(display_df["Date/Time"]).dt.strftime("%Y-%m-%d %H:%M")

        with st.expander(" View Monthly Expenses", expanded=True):
            st.dataframe(display_df, use_container_width=True, height=400)

        total = display_df["Amount"].sum()
        st.markdown(
            f"<h4 style='text-align:right; color:#4caf50;'> Total: ₹{total:,.2f}</h4>",
            unsafe_allow_html=True
        )
