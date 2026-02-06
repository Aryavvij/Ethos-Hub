import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from database import execute_query, fetch_query
from datetime import datetime
from utils import render_sidebar

# --- CSS STYLING ---
st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #76b372 !important;
        border-color: #76b372 !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #5e8f5b !important;
        border-color: #5e8f5b !important;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="Finances", page_icon="💰")

# --- GATEKEEPER ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py") 
    st.stop()

render_sidebar()

# --- INITIALIZATION ---
user = st.session_state.user_email
today = datetime.now()
st.title("Financial Hub")

# --- PERIOD SELECTOR ---
c1, c2 = st.columns([2, 1])
with c1:
    month_names = list(calendar.month_name)[1:] 
    selected_month_name = st.selectbox("Select Month", month_names, index=today.month-1)
    month_num = month_names.index(selected_month_name) + 1
with c2:
    selected_year = st.selectbox("Select Year", [2025, 2026, 2027, 2028], index=1)

period = f"{selected_month_name} {selected_year}"

# --- 1. DYNAMIC BUDGET ENGINE ---
st.subheader(f"Budget Allocation: {period}")

raw_budget = fetch_query("""
    SELECT 
        f.category, 
        f.plan, 
        COALESCE(SUM(e.amount), 0) as actual_total
    FROM finances f
    LEFT JOIN expense_logs e ON f.category = e.category 
        AND f.user_email = e.user_email
        AND EXTRACT(MONTH FROM e.expense_date) = %s
        AND EXTRACT(YEAR FROM e.expense_date) = %s
    WHERE f.user_email = %s AND f.period = %s
    GROUP BY f.category, f.plan
""", (month_num, selected_year, user, period))

budget_df = pd.DataFrame(raw_budget, columns=["Category", "Planned", "Actual"])

if budget_df.empty:
    budget_df = pd.DataFrame([{"Category": "General", "Planned": 0.0, "Actual": 0.0}])

edited_df = st.data_editor(
    budget_df, 
    num_rows="dynamic", 
    use_container_width=True, 
    key="budget_editor",
    column_config={
        "Category": st.column_config.TextColumn("Category", help="e.g. Rent, Food, Travel"),
        "Planned": st.column_config.NumberColumn("Planned (₹)", min_value=0.0, format="%.2f"),
        "Actual": st.column_config.NumberColumn("Actual (Spent)", disabled=True, format="%.2f")
    }
)

if st.button("Save Budget Plan", use_container_width=True, type="primary"):
    execute_query("DELETE FROM finances WHERE user_email=%s AND period=%s", (user, period))
    for _, row in edited_df.iterrows():
        if row["Category"]:
            execute_query("INSERT INTO finances (user_email, category, plan, actual, period) VALUES (%s, %s, %s, %s, %s)",
                          (user, row["Category"], row["Planned"], 0.0, period))
    st.success(f"Budget Plan for {period} updated!")
    st.rerun()

st.markdown("---")

# --- 2. ANALYTICS & DEBT TRACKING ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Spending Distribution")
    if not edited_df.empty and edited_df["Actual"].sum() > 0:
        fig = px.pie(edited_df, values='Actual', names='Category', hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log expenses in the ledger below to see your distribution.")

with col2:
    st.subheader("Debt Tracking")
    raw_debt = fetch_query("SELECT id, category, amount, paid_out FROM debt WHERE user_email=%s", (user,))
    debt_df = pd.DataFrame(raw_debt, columns=["ID", "Category", "Debt Amount", "Paid Out"])
    
    if debt_df.empty:
        debt_df = pd.DataFrame([{"Category": "Student Loan", "Debt Amount": 0.0, "Paid Out": 0.0}])

    edited_debt = st.data_editor(debt_df.drop(columns=["ID"]), num_rows="dynamic", use_container_width=True, key="debt_editor")
    
    if st.button("Sync Debt Data", use_container_width=True):
        execute_query("DELETE FROM debt WHERE user_email=%s", (user,))
        for _, row in edited_debt.iterrows():
            if row["Category"]:
                execute_query("INSERT INTO debt (user_email, category, amount, paid_out) VALUES (%s, %s, %s, %s)",
                              (user, row["Category"], row["Debt Amount"], row["Paid Out"]))
        st.success("Debt ledger updated!")
        st.rerun()

st.markdown("---")

# --- 3. EXPENSE LEDGER (TRANSACTION LOG) ---
st.subheader("Expense Ledger")
with st.expander("➕ Log New Expense", expanded=True):
    categories = edited_df["Category"].unique().tolist()
    if not categories or categories == [""]:
        categories = ["General"]

    l1, l2, l3, l4 = st.columns([1, 1, 2, 1])
    exp_date = l1.date_input("Date", today)
    exp_amt = l2.number_input("Amount (₹)", min_value=0.0, step=10.0)
    exp_desc = l3.text_input("Description", placeholder="e.g. Mess Bill, Coffee")
    exp_cat = l4.selectbox("Category", options=categories)

    if st.button("SAVE TO LEDGER", use_container_width=True):
        if exp_desc and exp_amt > 0:
            execute_query("""
                INSERT INTO expense_logs (user_email, amount, category, description, expense_date) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user, exp_amt, exp_cat, exp_desc, exp_date))
            st.success("Expense added! Budget synced.")
            st.rerun()
        else:
            st.error("Please provide a description and amount.")

# --- LEDGER HISTORY ---
with st.expander("View Ledger History"):
    expense_history = fetch_query("""
        SELECT expense_date, amount, description, category 
        FROM expense_logs 
        WHERE user_email=%s 
        AND EXTRACT(MONTH FROM expense_date) = %s 
        AND EXTRACT(YEAR FROM expense_date) = %s
        ORDER BY expense_date DESC
    """, (user, month_num, selected_year))
    
    if expense_history:
        history_df = pd.DataFrame(expense_history, columns=["Date", "Amount", "Description", "Category"])
        history_df["Amount"] = history_df["Amount"].apply(lambda x: f"{x:,.2f}")
        
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.caption(f"No expenses logged for {period} yet.")
