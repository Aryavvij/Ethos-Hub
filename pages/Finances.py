import streamlit as st
from database import execute_query, fetch_query
from datetime import datetime

# --- SAFETY GATE ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

st.title("💰 Finances & Debt")
user = st.session_state.user_email
period = datetime.now().strftime("%B %Y")

# --- BUDGET SECTION ---
st.header(f"Budget: {period}")
with st.expander("➕ Add Expense Category"):
    # We use 'cat' for the variable, but save it into the 'category' column
    cat = st.text_input("Category (e.g., Rent, Food)")
    plan = st.number_input("Planned Budget", min_value=0.0)
    actual = st.number_input("Actual Spent", min_value=0.0)
    
    if st.button("Save Category"):
        if cat:
            execute_query("""
                INSERT INTO finances (user_email, category, plan, actual, period) 
                VALUES (%s, %s, %s, %s, %s)
            """, (user, cat, plan, actual, period))
            st.success(f"Added {cat}")
            st.rerun()

# This is where the error was happening - now it matches the new SQL table
budget_data = fetch_query("""
    SELECT id, category, plan, actual 
    FROM finances 
    WHERE user_email=%s AND period=%s
""", (user, period))

if budget_data:
    # Calculate totals for a summary
    st.table([
        {"Category": r[1], "Planned": r[2], "Actual": r[3], "Remaining": r[2]-r[3]} 
        for r in budget_data
    ])
else:
    st.info("No budget entries for this month yet.")

st.markdown("---")

# --- DEBT SECTION ---
st.header("💸 Debt Tracking")
with st.expander("➕ Log New Debt"):
    person = st.text_input("Who do you owe?")
    amount = st.number_input("Amount (Rs)", min_value=0.0)
    reason = st.text_input("Reason/Note")
    
    if st.button("Log Debt"):
        if person and amount > 0:
            execute_query("""
                INSERT INTO debt (user_email, person, amount, reason) 
                VALUES (%s, %s, %s, %s)
            """, (user, person, amount, reason))
            st.success(f"Logged debt to {person}")
            st.rerun()

debt_data = fetch_query("SELECT id, person, amount, reason FROM debt WHERE user_email=%s", (user,))
if debt_data:
    for did, p, amt, r in debt_data:
        c1, c2, c3 = st.columns([0.4, 0.4, 0.2])
        c1.write(f"**{p}**")
        c2.write(f"Rs {amt:,.2f} ({r})")
        if c3.button("Settled", key=f"d_{did}"):
            execute_query("DELETE FROM debt WHERE id=%s", (did,))
            st.rerun()
