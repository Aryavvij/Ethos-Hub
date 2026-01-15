import streamlit as st
import pandas as pd
from database import execute_query, fetch_query
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Milestones")

# 2. SAFETY GATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page.")
    st.stop()

user = st.session_state.user_email

st.title("🏁 Milestone Map")
st.caption("Chronological Archive of Major Life Achievements")

# --- 3. THE TROPHY CASE (TOP METRICS) ---
raw_milestones = fetch_query(
    "SELECT achievement, category, achieved_date FROM milestones WHERE user_email=%s ORDER BY achieved_date DESC", 
    (user,)
)
df_m = pd.DataFrame(raw_milestones, columns=["Achievement", "Category", "Date"])

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total Milestones", len(df_m))
with m2:
    latest = df_m.iloc[0]["Achievement"] if not df_m.empty else "None"
    st.metric("Latest Win", latest)
with m3:
    if not df_m.empty:
        days_ago = (datetime.now().date() - df_m.iloc[0]["Date"]).days
        st.metric("Days Since Last Win", days_ago)

st.markdown("---")

# --- 4. THE LOGBOOK ---
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.subheader("📜 Achievement Log")
    st.info("Log your major wins below. Every time you finish a 'Blueprint' task, archive it here!")
    
    # Data Editor for logging
    if df_m.empty:
        df_m = pd.DataFrame([{"Achievement": "", "Category": "Personal", "Date": datetime.now().date()}])

    edited_m = st.data_editor(
        df_m,
        num_rows="dynamic",
        use_container_width=True,
        key="milestone_editor",
        column_config={
            "Category": st.column_config.SelectboxColumn(
                options=["Career", "Academic", "Fitness", "Financial", "Personal", "Travel"]
            ),
            "Date": st.column_config.DateColumn("Achieved Date")
        }
    )

    if st.button("💾 Archive Milestones", use_container_width=True, key="sync_milestones"):
        execute_query("DELETE FROM milestones WHERE user_email=%s", (user,))
        for _, row in edited_m.iterrows():
            if row["Achievement"]:
                execute_query(
                    "INSERT INTO milestones (user_email, achievement, category, achieved_date) VALUES (%s, %s, %s, %s)",
                    (user, row["Achievement"], row["Category"], row[ "Date"])
                )
        st.success("Milestones Archived!")
        st.rerun()

with col_right:
    st.subheader("🗓️ Timeline View")
    if not df_m.empty and df_m.iloc[0]["Achievement"] != "":
        # Stylish vertical timeline
        for _, row in df_m.sort_values("Date", ascending=False).iterrows():
            st.markdown(f"""
                <div style="border-left: 3px solid #76b372; padding-left: 15px; margin-bottom: 20px;">
                    <span style="color: #76b372; font-size: 12px; font-weight: bold;">{row['Date'].strftime('%b %Y')}</span><br>
                    <strong style="font-size: 16px;">{row['Achievement']}</strong><br>
                    <span style="color: gray; font-size: 13px;">🏷️ {row['Category']}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No milestones recorded yet. Time to win!")
