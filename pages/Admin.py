import streamlit as st
import pandas as pd
import plotly.express as px
from database import fetch_query
from utils import render_sidebar
from services.observability import Telemetry

# --- AUTH GATE (STRICT ADMIN ONLY) ---
ADMIN_EMAIL = "aryavvij@gmail.com" 

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")
    st.stop()

if st.session_state.user_email != ADMIN_EMAIL:
    st.error("ACCESS DENIED: Insufficient Clearances.")
    Telemetry.log('SECURITY', 'Unauthorized_Admin_Access', 1.0)
    st.stop()

st.set_page_config(layout="wide", page_title="System Watch", page_icon="📡")

render_sidebar()

st.title("📡 System Observability")
st.caption("Real-time telemetry and performance monitoring")

# --- 1. KEY PERFORMANCE INDICATORS (KPIs) ---
stats = fetch_query("""
    SELECT 
        AVG(CASE WHEN category = 'PERFORMANCE' THEN value END) as avg_lat,
        COUNT(CASE WHEN category = 'ERROR' THEN 1 END) as err_count,
        COUNT(CASE WHEN category = 'AUTH' AND event_name = 'Login_Success' THEN 1 END) as logins
    FROM system_metrics 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
""", ())

s = stats[0] if stats else (0, 0, 0)
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric("Avg Latency", f"{s[0]*1000:.0f}ms" if s[0] else "0ms", delta="-12ms")
kpi2.metric("System Errors (24h)", s[1], delta="Critical" if s[1] > 5 else "Stable")
kpi3.metric("Active Sessions", s[2])

st.markdown("---")

# --- 2. PERFORMANCE TRACING (Latency over time) ---
st.subheader("Latency Distribution")
latency_data = fetch_query("""
    SELECT timestamp, event_name, value 
    FROM system_metrics 
    WHERE category = 'PERFORMANCE' 
    ORDER BY timestamp DESC LIMIT 100
""", ())

if latency_data:
    df_lat = pd.DataFrame(latency_data, columns=["Time", "Event", "Seconds"])
    fig_lat = px.line(df_lat, x="Time", y="Seconds", color="Event", 
                     template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_lat.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig_lat, use_container_width=True)
else:
    st.info("No performance data logged yet.")

# --- 3. SYSTEM LOGS (The Event Feed) ---
st.subheader("Event Feed")
log_data = fetch_query("""
    SELECT timestamp, category, event_name, user_email, metadata 
    FROM system_metrics 
    ORDER BY timestamp DESC LIMIT 50
""", ())

if log_data:
    df_logs = pd.DataFrame(log_data, columns=["Timestamp", "Category", "Event", "User", "Details"])
    def color_category(val):
        colors = {'ERROR': 'color: #ff4b4b', 'SECURITY': 'color: #ffaa00', 'AUTH': 'color: #76b372'}
        return colors.get(val, 'color: white')

    st.dataframe(
        df_logs.style.applymap(color_category, subset=['Category']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.caption("Listening for system events...")
