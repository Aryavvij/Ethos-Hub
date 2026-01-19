import streamlit as st
import hashlib
from datetime import datetime, timedelta  
from database import execute_query, fetch_query

# 1. SET WIDE MODE
st.set_page_config(layout="wide", page_title="Ethos Hub")

# --- AUTH UTILS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AUTHENTICATION UI ---
if not st.session_state.logged_in:
    st.title("Ethos System Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            res = fetch_query("SELECT password FROM users WHERE email=%s", (email,))
            if res and res[0][0] == make_hashes(password):
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun() 
            else:
                st.error("Incorrect Email or Password")
    
    with tab2:
        st.subheader("Create New Account")
        new_email = st.text_input("New Email", key="signup_email")
        new_pass = st.text_input("New Password", type='password', key="signup_pass")
        if st.button("Sign Up"):
            hashed_pass = make_hashes(new_pass)
            try:
                execute_query("INSERT INTO users (email, password) VALUES (%s, %s)", (new_email, hashed_pass))
                st.success("Account created! Go to Login tab.")
            except:
                st.error("Email already exists.")
    st.stop() 

# --- HOME DASHBOARD ---
user = st.session_state.user_email
st.sidebar.success(f"User: {user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("ETHOS HUB")

# 1. STRATEGIC SEMESTER GOALS
st.markdown("### 🎯 Strategic Semester Goals")
res = fetch_query("SELECT academic, health, personal FROM semester_goals WHERE user_email=%s", (user,))
g_acad, g_health, g_pers = res[0] if res else ("", "", "")

g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold; margin-bottom:5px;">Academic</p>', unsafe_allow_html=True)
        new_acad = st.text_area("A", value=g_acad, height=100, label_visibility="collapsed", key="ac")
with g2:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold; margin-bottom:5px;">Health</p>', unsafe_allow_html=True)
        new_health = st.text_area("H", value=g_health, height=100, label_visibility="collapsed", key="he")
with g3:
    with st.container(border=True):
        st.markdown('<p style="color:#76b372; font-weight:bold; margin-bottom:5px;">Others</p>', unsafe_allow_html=True)
        new_pers = st.text_area("O", value=g_pers, height=100, label_visibility="collapsed", key="ot")

if st.button("Update Goals", use_container_width=True):
    execute_query("""
        INSERT INTO semester_goals (user_email, academic, health, personal) 
        VALUES (%s,%s,%s,%s) 
        ON CONFLICT (user_email) 
        DO UPDATE SET academic=EXCLUDED.academic, health=EXCLUDED.health, personal=EXCLUDED.personal
    """, (user, new_acad, new_health, new_pers))
    st.success("Goals updated!")

st.markdown("---")

# --- 2. THE 4-BOX INTEGRATED COMMAND CENTER ---
st.markdown("### ⚡ Today's System Briefing")

t_date = datetime.now().date()
d_name = t_date.strftime("%A")
d_idx = t_date.weekday()
w_start = t_date - timedelta(days=d_idx)

b1, b2, b3, b4 = st.columns(4)

# BOX 1: DAILY TASKS
with b1:
    with st.container(border=True):
        st.markdown('**📋 Daily Tasks**')
        tasks = fetch_query("SELECT task_name, is_done FROM weekly_planner WHERE user_email=%s AND day_index=%s AND week_start=%s", (user, d_idx, w_start))
        if tasks:
            for tname, tdone in tasks:
                color = "#76b372" if tdone else "#ff4b4b"
                st.markdown(f"<span style='color:{color};'>{'●' if tdone else '○'}</span> {tname}", unsafe_allow_html=True)
        else:
            st.caption("No tasks for today.")

# BOX 2: PERFORMANCE & UPCOMING EVENTS (UPDATED)
with b2:
    with st.container(border=True):
        st.markdown('**🛡️ Intelligence & Events**')
        # Training Split
        split_res = fetch_query("SELECT split_title FROM training_splits WHERE user_email=%s AND day_name=%s", (user, d_name))
        split_name = split_res[0][0].upper() if split_res and split_res[0][0] else "REST DAY"
        st.markdown(f"<p style='margin:0; font-size:12px; color:gray;'>TRAINING</p><p style='color:#76b372; font-weight:bold; margin-bottom:10px;'>{split_name}</p>", unsafe_allow_html=True)
        
        # UPCOMING EVENTS LOGIC
        st.markdown("<p style='margin:0; font-size:12px; color:gray;'>CALENDAR HORIZON</p>", unsafe_allow_html=True)
        # Fetch 3 events starting from today onwards
        events = fetch_query("""
            SELECT description, event_date 
            FROM events 
            WHERE user_email=%s AND event_date >= %s 
            ORDER BY event_date ASC 
            LIMIT 3
        """, (user, t_date))
        
        if events:
            for desc, edate in events:
                date_str = edate.strftime("%b %d")
                st.markdown(f"**{date_str}**: {desc}")
        else:
            st.caption("No upcoming events.")

# BOX 3: STRATEGY & INTELLECT
with b3:
    with st.container(border=True):
        st.markdown('**🧠 Strategy & Intellect**')
        upcoming = fetch_query("SELECT task_description, progress FROM future_tasks WHERE user_email=%s AND progress < 100 ORDER BY progress DESC LIMIT 1", (user,))
        if upcoming:
            st.markdown(f"<p style='margin:0; font-size:12px; color:gray;'>BLUEPRINT FOCUS</p><p style='font-weight:bold; margin-bottom:10px;'>{upcoming[0][0].upper()} ({upcoming[0][1]}%)</p>", unsafe_allow_html=True)
        else:
            st.info("Strategy Map Clear")
        
        focus_res = fetch_query("SELECT SUM(duration_mins) FROM focus_sessions WHERE user_email=%s AND session_date = CURRENT_DATE", (user,))
        mins = focus_res[0][0] if focus_res and focus_res[0][0] else 0
        st.metric("Focus Today", f"{mins}m")

# BOX 4: ACADEMIC TIMETABLE
with b4:
    with st.container(border=True):
        st.markdown('**🎓 Today\'s Classes**')
        classes = fetch_query("""
            SELECT start_time, subject, location 
            FROM timetable 
            WHERE user_email=%s AND day_name=%s 
            ORDER BY start_time ASC
        """, (user, d_name))
        
        if classes:
            for ctime, csub, cloc_raw in classes:
                try:
                    time_part, loc = cloc_raw.split('|')
                    start_str, end_str = time_part.split('-')
                    display_start = datetime.strptime(start_str, "%H:%M").strftime("%I:%M %p")
                    display_end = datetime.strptime(end_str, "%H:%M").strftime("%I:%M %p")
                    full_time = f"{display_start} - {display_end}"
                except:
                    full_time = ctime.strftime('%I:%M %p')
                
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.03); padding:8px; border-radius:5px; margin-bottom:8px; border-left:3px solid #76b372;">
                        <span style="color:#76b372; font-size:10px; font-weight:bold;">{full_time}</span><br>
                        <span style="font-size:12px; font-weight:bold;">{csub.upper()}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No classes scheduled today.")

# 3. FINANCIAL OVERVIEW
st.markdown("### 💰 Financial Status")
f1, f2 = st.columns(2)
period = t_date.strftime("%B %Y")

with f1:
    with st.container(border=True):
        budget_calc = fetch_query("SELECT SUM(COALESCE(plan, 0) - COALESCE(actual, 0)) FROM finances WHERE user_email=%s AND period=%s", (user, period))
        rem = budget_calc[0][0] if budget_calc and budget_calc[0][0] is not None else 0
        st.markdown(f"<p style='color:gray;margin:0;'>Remaining Budget ({period})</p><h2 style='color:#76b372;margin:0;'>₹ {rem:,.2f}</h2>", unsafe_allow_html=True)

with f2:
    with st.container(border=True):
        debt_calc = fetch_query("SELECT SUM(COALESCE(amount, 0) - COALESCE(paid_out, 0)) FROM debt WHERE user_email=%s", (user,))
        net_debt = debt_calc[0][0] if debt_calc and debt_calc[0][0] is not None else 0
        st.markdown(f"<p style='color:gray;margin:0;'>Total Net Debt</p><h2 style='color:#ff4b4b;margin:0;'>₹ {net_debt:,.2f}</h2>", unsafe_allow_html=True)
