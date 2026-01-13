import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Finances")

# --- SAFETY GATE ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email
period = datetime.now().strftime("%B %Y")  # e.g., "January 2026"

st.title(f"💰 Financial Overview: {period}")

# --- 1. MAIN EXPENSE TABLE ---
st.subheader("Monthly Budget Breakdown")
with st.expander("➕ Add New Expense Category", expanded=False):
    c1, c2, c3 = st.columns(3)
    cat = c1.text_input("Category")
    plan = c2.number_input("Planned Amount", min_value=0.0)
    actual = c3.number_input("Actual Spent", min_value=0.0)
    if st.button("Add to Budget", use_container_width=True):
        execute_query("INSERT INTO finances (user_email, category, plan, actual, period) VALUES (%s, %s, %s, %s, %s)", (user, cat, plan, actual, period))
        st.rerun()

# Fetch data for the table
raw_data = fetch_query("SELECT id, category, plan, actual FROM finances WHERE user_email=%s AND period=%s", (user, period))

if raw_data:
    df = pd.DataFrame(raw_data, columns=["ID", "Category", "Planned", "Actual"])
    df["Remaining"] = df["Planned"] - df["Actual"]
    
    # Show the main table
    st.dataframe(df.drop(columns=["ID"]), use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- 2. PIE CHART & DEBT SIDE BY SIDE ---
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Expense Distribution")
        fig = px.pie(df, values='Actual', names='Category', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💸 Debt Tracking")
        with st.expander("➕ Log New Debt"):
            p = st.text_input("Owed to")
            a = st.number_input("Amount", min_value=0.0)
            r = st.text_input("Reason")
            if st.button("Save Debt", use_container_width=True):
                execute_query("INSERT INTO debt (user_email, person, amount, reason) VALUES (%s, %s, %s, %s)", (user, p, a, r))
                st.rerun()

        debts = fetch_query("SELECT id, person, amount, reason FROM debt WHERE user_email=%s", (user,))
        if debts:
            # We use a clean list/table for debts here
            debt_df = pd.DataFrame(debts, columns=["ID", "Person", "Amount", "Reason"])
            for index, row in debt_df.iterrows():
                with st.container(border=True):
                    dc1, dc2 = st.columns([0.8, 0.2])
                    dc1.markdown(f"**{row['Person']}**: Rs {row['Amount']:,.2f} <br><small>{row['Reason']}</small>", unsafe_allow_html=True)
                    if dc2.button("Settled", key=f"settle_{row['ID']}"):
                        execute_query("DELETE FROM debt WHERE id=%s", (row['ID'],))
                        st.rerun()
        else:
            st.info("No current debts.")
else:
    st.info("Start by adding your first expense category above.")
