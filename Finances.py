import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query, get_db_connection

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

st.set_page_config(layout="wide")

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Semester Financial Tracker")
user = st.session_state.user_email

c1, c2 = st.columns(2)
with c1:
    month = st.selectbox("Select Month", ["August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July"])
with c2:
    year = st.selectbox("Select Year", [2025, 2026, 2027, 2028, 2029, 2030])
period = f"{month} {year}"

# --- MONTHLY BUDGET ---
st.subheader(f"Monthly Budget: {period}")

raw_data = fetch_query("SELECT source, plan, actual FROM finances WHERE period=%s AND user_email=%s", (period, user))
df_m = pd.DataFrame(raw_data, columns=['source', 'plan', 'actual']) if raw_data else pd.DataFrame([{"source": "Rent", "plan": 0.0, "actual": 0.0}])

edited_m = st.data_editor(df_m, num_rows="dynamic", use_container_width=True, key="m_table")

if st.button("Save Monthly Budget"):
    execute_query("DELETE FROM finances WHERE period=%s AND user_email=%s", (period, user))
    for _, row in edited_m.iterrows():
        execute_query("INSERT INTO finances (user_email, period, source, plan, actual) VALUES (%s, %s, %s, %s, %s)",
                      (user, period, row['source'], float(row['plan']), float(row['actual'])))
    st.success("Budget saved to Supabase.")

st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Expenses Distribution")
    if not edited_m.empty and edited_m['actual'].astype(float).sum() > 0:
        fig = px.pie(edited_m, values='actual', names='source', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log actual expenses to see charts.")

with col_right:
    st.subheader("Permanent Debt Tracker")
    debt_data = fetch_query("SELECT source, debt, paid_out FROM debts WHERE user_email=%s", (user,))
    df_d = pd.DataFrame(debt_data, columns=['source', 'debt', 'paid_out']) if debt_data else pd.DataFrame([{"source": "Loan", "debt": 0.0, "paid_out": 0.0}])
    
    edited_d = st.data_editor(df_d, num_rows="dynamic", use_container_width=True, key="d_table")
    
    if st.button("Update Permanent Debt"):
        execute_query("DELETE FROM debts WHERE user_email=%s", (user,))
        for _, row in edited_d.iterrows():
            execute_query("INSERT INTO debts (user_email, source, debt, paid_out) VALUES (%s, %s, %s, %s)",
                          (user, row['source'], float(row['debt']), float(row['paid_out'])))
        st.success("Debts updated.")