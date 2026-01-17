import streamlit as st
import pandas as pd
import plotly.express as px
from database import execute_query, fetch_query

st.set_page_config(layout="wide", page_title="Blueprint", page_icon="🗺️")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in.")
    st.stop()

user = st.session_state.user_email
st.title("🗺️ Strategic Blueprint")

# DATA ENGINE
raw_data = fetch_query("SELECT task_description, category, timeframe, priority, progress FROM future_tasks WHERE user_email=%s", (user,))
df = pd.DataFrame(raw_data, columns=["Description", "Category", "Timeframe", "Priority", "Progress"])
df['Status Bar'] = df['Progress']

# --- 3. TOP LEVEL OVERVIEW (Metrics) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Initiatives", len(df))
with m2:
    high_prio = len(df[df["Priority"].str.contains("High", na=False)]) if not df.empty else 0
    st.metric("High Priority", high_prio)
with m3:
    avg_prog = int(df["Progress"].mean()) if not df.empty else 0
    st.metric("Avg. Completion", f"{avg_prog}%")
with m4:
    ready = len(df[df["Progress"] >= 80]) if not df.empty else 0
    st.metric("Ready to Deploy", ready)

st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

# STRATEGY MAP
st.subheader("Strategic Resource Mapping")
if not df.empty:
    fig = px.sunburst(df, path=['Category', 'Priority', 'Description'], values='Progress', color='Category', color_discrete_sequence=px.colors.qualitative.Bold)
    # FIX: Restore bold separation lines
    fig.update_traces(marker_line_width=3, marker_line_color="#121212", insidetextorientation='radial')
    fig.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=550, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# MASTER TABLE
# --- 5. SYSTEM MASTER TABLE (INTERACTIVE PROGRESS) ---
st.subheader("System Master Table")

# Display logic
display_df = df if filter_choice == "All" else df[df["Timeframe"] == filter_choice]

# COLUMN CONFIGURATION
edited_df = st.data_editor(
    display_df,
    num_rows="dynamic",
    use_container_width=True,
    key="blueprint_editor",
    column_config={
        "Progress": st.column_config.ProgressColumn(
            "Strategic Progress",
            help="Drag the bar to update completion percentage",
            min_value=0,
            max_value=100,
            format="%d%%", # This shows the % inside/alongside the bar
            step=1,
        ),
        "Category": st.column_config.SelectboxColumn(options=["Career", "Financial", "Academic", "Hobby", "Travel", "Personal"]),
        "Priority": st.column_config.SelectboxColumn(options=["High", "Medium", "Low"]),
        "Timeframe": st.column_config.SelectboxColumn(options=time_options[1:])
    }
)
