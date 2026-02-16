import streamlit as st
import pandas as pd
import plotly.express as px
from database import fetch_query
from utils import render_sidebar
from services.observability import Telemetry

# --- 1. CONFIGURATION & AUTH GATE ---
st.set_page_config(layout="wide", page_title="System Watch", page_icon="📡")
ADMIN_EMAIL = "aryavvij@gmail.com" 

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Home.py")
    st.stop()
is_admin_email = st.session_state.get('user_email') == ADMIN_EMAIL
is_admin_role = st.session_state.get('role') == 'admin'

if not (is_admin_email or is_admin_role):
    Telemetry.log('SECURITY', 'Unauthorized_Admin_Access', metadata={'user': st.session_state.get('user_email')})
    st.error("RESTRICTED AREA: Administrators Only.")
    st.stop()

render_sidebar()

# --- 2. HEADER ---
st.title("🌐 System Health Observability")
st.caption("Real-time telemetry and performance monitoring across the ETHOS ecosystem.")

# --- 3. GLOBAL SYSTEM HEALTH MAP ---
health_data = fetch_query("""
    SELECT metadata->>'page' as page_name, 
           COUNT(CASE WHEN category = 'ERROR' THEN 1 END) as crash_count
    FROM system_metrics 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
    AND metadata->>'page' IS NOT NULL
    GROUP BY page_name
""", ())

if health_data:
    h_cols = st.columns(min(len(health_data), 4))
    for idx, (p_name, p_crashes) in enumerate(health_data):
        col_idx = idx % 4
        status = "🔴 CRITICAL" if p_crashes > 0 else "🟢 STABLE"
        h_cols[col_idx].metric(p_name.upper(), status, delta=f"{p_crashes} failures", delta_color="inverse")
else:
    st.info("Waiting for page telemetry...")

st.markdown("---")

# --- 4. KEY PERFORMANCE INDICATORS (KPIs) ---
stats = fetch_query("""
    SELECT 
        AVG(CASE WHEN category = 'PERFORMANCE' THEN value END) as avg_lat,
        COUNT(CASE WHEN category = 'ERROR' THEN 1 END) as err_count,
        COUNT(CASE WHEN category = 'SECURITY' THEN 1 END) as sec_alerts,
        COUNT(CASE WHEN category = 'AUTH' AND event_name = 'Login_Success' THEN 1 END) as logins
    FROM system_metrics 
    WHERE timestamp >= NOW() - INTERVAL '24 hours'
""", ())

s = stats[0] if stats else (0, 0, 0, 0)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Avg Latency", f"{s[0]*1000:.0f}ms" if s[0] else "0ms", delta="Target <200ms")
kpi2.metric("System Errors (24h)", s[1], delta="Critical" if s[1] > 0 else "Clean", delta_color="inverse")
kpi3.metric("Security Alerts", s[2], delta="Threats Blocked" if s[2] > 0 else "Secure", delta_color="inverse")
kpi4.metric("Active Sessions", s[3])

# --- 5. PERFORMANCE TRACING ---
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
    fig_lat.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), 
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_lat, use_container_width=True)
else:
    st.info("No performance data logged yet.")

# --- 6. SYSTEM LOGS (The Event Feed) ---
st.subheader("Live Event Feed")
log_data = fetch_query("""
    SELECT timestamp, category, event_name, user_email, metadata 
    FROM system_metrics 
    ORDER BY timestamp DESC LIMIT 50
""", ())

if log_data:
    df_logs = pd.DataFrame(log_data, columns=["Timestamp", "Category", "Event", "User", "Details"])
    
    def color_category(val):
        colors = {
            'ERROR': 'background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b;', 
            'SECURITY': 'background-color: rgba(255, 170, 0, 0.1); color: #ffaa00;', 
            'AUTH': 'background-color: rgba(118, 179, 114, 0.1); color: #76b372;'
        }
        return colors.get(val, 'color: white')

    st.dataframe(
        df_logs.style.applymap(color_category, subset=['Category']),
        use_container_width=True,
        hide_index=True
    )
else:
    st.caption("Listening for system heartbeats...")
