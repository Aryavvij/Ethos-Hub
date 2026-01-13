import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from database import execute_query, fetch_query

# --- 1. AUTHENTICATION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in on the Home page to access this system.")
    st.stop() 

st.set_page_config(layout="wide", page_title="Habit Tracker")

# Load Global Styles
try:
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.title("📊 Monthly Habit Tracker")

# --- 2. DATE & SELECTION ---
user = st.session_state.user_email
today = datetime.now()

c1, c2 = st.columns(2)
with c1:
    month_name = st.selectbox("Select Month", list(calendar.month_name)[1:], index=today.month-1)
with c2:
    year = st.selectbox("Select Year", [2025, 2026, 2027, 2028, 2029, 2030], index=1)

month_num = list(calendar.month_name).index(month_name)
num_days = calendar.monthrange(year, month_num)[1]
days_list = [str(i) for i in range(1, num_days + 1)]

# --- 3. DATA PREPARATION ---

# First, fetch all unique habits this user has ever created
habit_names_query = "SELECT DISTINCT habit_name FROM habits WHERE user_email=%s"
db_habit_names = fetch_query(habit_names_query, (user,))
found_habits = [row[0] for row in db_habit_names]

# Combine with your standard defaults
default_habits = ["Wake up 05:00 ⏰", "Gym 💪", "Reading 📖"]
# Use a set to remove duplicates, then convert back to list
all_habits = list(set(default_habits + found_habits))

# Fetch the actual completion data for the selected month
db_data = fetch_query("""
    SELECT habit_name, EXTRACT(DAY FROM log_date)::int, status 
    FROM habits 
    WHERE user_email=%s 
    AND EXTRACT(MONTH FROM log_date)=%s 
    AND EXTRACT(YEAR FROM log_date)=%s
""", (user, month_num, year))

# Initialize the DataFrame with False for all days
habit_df = pd.DataFrame(False, index=all_habits, columns=days_list)

# Fill the DataFrame with the status from Supabase
for h_name, d_num, stat in db_data:
    if h_name in habit_df.index and str(d_num) in habit_df.columns:
        habit_df.at[h_name, str(d_num)] = bool(stat)

# --- 4. THE DATA EDITOR (GRID) ---
st.info("💡 **Tip**: Add a new habit by typing in the empty row at the bottom. Scroll right to see all days.")

# The data editor allows for interactive ticking and adding rows
edited_df = st.data_editor(
    habit_df, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={d: st.column_config.CheckboxColumn(required=True) for d in days_list}
)

# --- 5. SAVE TO CLOUD ---
if st.button("☁️ Sync to Supabase"):
    with st.spinner("Saving your progress..."):
        try:
            for h_name in edited_df.index:
                for d_str in edited_df.columns:
                    status = edited_df.loc[h_name, d_str]
                    # Format as YYYY-MM-DD for PostgreSQL
                    formatted_date = f"{year}-{month_num:02d}-{int(d_str):02d}"
                    
                    # UPSERT Logic: Ensures no duplicates and fixes the Conflict error
                    execute_query("""
                        INSERT INTO habits (user_email, habit_name, log_date, status) 
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (user_email, habit_name, log_date) 
                        DO UPDATE SET status = EXCLUDED.status
                    """, (user, h_name, formatted_date, bool(status)))
            
            st.success("All habits successfully synced!")
            st.rerun()
        except Exception as e:
            st.error(f"Error during sync: {e}")

# --- 6. ANALYTICS ---
st.markdown("---")
st.subheader("Monthly Consistency Score")

if not edited_df.empty:
    m_cols = st.columns(4)
    for i, habit in enumerate(edited_df.index):
        # Calculate success rate based on ticks vs total days in month
        completed_days = edited_df.loc[habit].sum()
        score = (completed_days / num_days) * 100
        
        with m_cols[i % 4]:
            st.metric(label=str(habit), value=f"{score:.1f}%", delta=f"{int(completed_days)} days")

st.markdown('</div>', unsafe_allow_html=True)
