import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from database import execute_query, fetch_query
from datetime import datetime
from utils import render_sidebar

# --- PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Finances")

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
with c2:
    selected_year = st.selectbox("Select Year", [2025, 2026, 2027, 2028], index=1)

period = f"{selected_month_name} {selected_year}"

# --- BUDGET MANAGEMENT ---
st.subheader(f"Budget for {period}")
raw_budget = fetch_query("SELECT category, plan, actual FROM finances WHERE user_email=%s AND period=%s", (user, period))
budget_df = pd.DataFrame(raw_budget, columns=["Category", "Planned", "Actual"])

if budget_df.empty:
    budget_df = pd.DataFrame([{"Category": "", "Planned": 0.0, "Actual": 0.0}])

edited_df = st.data_editor(budget_df, num_rows="dynamic", use_container_width=True, key="budget_editor")

if st.button("Save Budget Changes", use_container_width=True):
    execute_query("DELETE FROM finances WHERE user_email=%s AND period=%s", (user, period))
    for _, row in edited_df.iterrows():
        if row["Category"]:
            execute_query("INSERT INTO finances (user_email, category, plan, actual, period) VALUES (%s, %s, %s, %s, %s)",
                          (user, row["Category"], row["Planned"], row["Actual"], period))
    st.success(f"Budget Saved!")
    st.rerun()

st.markdown("---")

# --- ANALYTICS & DEBT TRACKING ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Spending Distribution")
    if not edited_df.empty and edited_df["Actual"].sum() > 0:
        fig = px.pie(edited_df, values='Actual', names='Category', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Input spending data to see chart.")

with col2:
    st.subheader("Debt Tracking")
    raw_debt = fetch_query("SELECT category, amount, paid_out FROM debt WHERE user_email=%s", (user,))
    debt_df = pd.DataFrame(raw_debt, columns=["Category", "Debt Amount", "Paid Out"])
    
    if debt_df.empty:
        debt_df = pd.DataFrame([{"Category": "", "Debt Amount": 0.0, "Paid Out": 0.0}])

    edited_debt = st.data_editor(debt_df, num_rows="dynamic", use_container_width=True, key="debt_editor")
    
    if st.button("Sync Debt Data", use_container_width=True):
        execute_query("DELETE FROM debt WHERE user_email=%s", (user,))
        for _, row in edited_debt.iterrows():
            if row["Category"]:
                execute_query("INSERT INTO debt (user_email, category, amount, paid_out) VALUES (%s, %s, %s, %s)",
                              (user, row["Category"], row["Debt Amount"], row["Paid Out"]))
        st.success("Debts Synced!")
        st.rerun()
