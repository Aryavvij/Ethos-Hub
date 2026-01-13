import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime

st.set_page_config(layout="wide", page_title="Finances")

# --- SAFETY GATE ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
period = datetime.now().strftime("%B %Y")

st.title(f"💰 Financial Hub: {period}")

# 1. THE BIG EDITABLE TABLE (Expenses)
st.subheader("Monthly Budget (Click rows to edit)")

raw_budget = fetch_query("SELECT category, plan, actual FROM finances WHERE user_email=%s AND period=%s", (user, period))
budget_df = pd.DataFrame(raw_budget, columns=["Category", "Planned", "Actual"])

if budget_df.empty:
    budget_df = pd.DataFrame([{"Category": "Food", "Planned": 0.0, "Actual": 0.0}])

edited_df = st.data_editor(budget_df, num_rows="dynamic", use_container_width=True, key="budget_editor")

if st.button("💾 Save Budget Changes", use_container_width=True):
    execute_query("DELETE FROM finances WHERE user_email=%s AND period=%s", (user, period))
    for _, row in edited_df.iterrows():
        if row["Category"]:
            execute_query("INSERT INTO finances (user_email, category, plan, actual, period) VALUES (%s, %s, %s, %s, %s)",
                          (user, row["Category"], row["Planned"], row["Actual"], period))
    st.success("Budget Saved!")
    st.rerun()

st.markdown("---")

# 2. PIE CHART & DEBT (Side by Side)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Spending Distribution")
    if not edited_df.empty and edited_df["Actual"].sum() > 0:
        fig = px.pie(edited_df, values='Actual', names='Category', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Enter spending data to see the chart.")

with col2:
    st.subheader("💸 Debt Tracking (9:1 View)")
    raw_debt = fetch_query("SELECT person, amount, reason FROM debt WHERE user_email=%s", (user,))
    debt_df = pd.DataFrame(raw_debt, columns=["Person", "Amount", "Reason"])
    
    if debt_df.empty:
        debt_df = pd.DataFrame([{"Person": "Friend", "Amount": 0.0, "Reason": "Note"}])

    edited_debt = st.data_editor(debt_debt_df if not debt_df.empty else debt_df, num_rows="dynamic", use_container_width=True, key="debt_editor")
    
    if st.button("💾 Sync Debt Data", use_container_width=True):
        execute_query("DELETE FROM debt WHERE user_email=%s", (user,))
        for _, row in edited_debt.iterrows():
            if row["Person"]:
                execute_query("INSERT INTO debt (user_email, person, amount, reason) VALUES (%s, %s, %s, %s)",
                              (user, row["Person"], row["Amount"], row["Reason"]))
        st.success("Debts Synced!")
        st.rerun()
