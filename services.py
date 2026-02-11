from database import fetch_query, execute_query
from pydantic import BaseModel
from datetime import datetime as dt
from typing import List, Tuple
import streamlit as st

# --- 1. SCHEMAS (Data Integrity) ---
class FocusSession(BaseModel):
    task_name: str
    duration_mins: int

class FinanceSummary(BaseModel):
    remaining_budget: float = 0.0
    net_debt: float = 0.0

# --- 2. FOCUS SERVICE ---
class FocusService:
    @staticmethod
    @st.cache_data(ttl=600)
    def get_daily_logs(user_email: str, date) -> List[FocusSession]:
        query = "SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date=%s"
        raw_data = fetch_query(query, (user_email, date))
        return [FocusSession(task_name=row[0], duration_mins=row[1]) for row in raw_data]

    @staticmethod
    @st.cache_data(ttl=600)
    def get_stats_overview(user_email: str) -> Tuple[int, int, float, float]:
        query = """
            WITH daily_totals AS (
                SELECT session_date, SUM(duration_mins) as total_mins
                FROM focus_sessions WHERE user_email = %s GROUP BY session_date
            )
            SELECT 
                (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions WHERE user_email = %s AND session_date = CURRENT_DATE),
                (SELECT COALESCE(AVG(total_mins), 0) FROM daily_totals),
                (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions WHERE user_email = %s AND session_date >= DATE_TRUNC('week', CURRENT_DATE)),
                (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions WHERE user_email = %s AND session_date >= DATE_TRUNC('month', CURRENT_DATE))
        """
        res = fetch_query(query, (user_email, user_email, user_email, user_email))
        return res[0] if res else (0, 0, 0, 0)

# --- 3. FINANCE SERVICE ---
class FinanceService:
    @staticmethod
    @st.cache_data(ttl=300)
    def get_dashboard_metrics(user_email: str, period: str) -> FinanceSummary:
        query = """
            SELECT 
                (SELECT COALESCE(SUM(plan), 0) FROM finances WHERE user_email=%s AND period=%s) - 
                (SELECT COALESCE(SUM(amount), 0) FROM expense_logs 
                 WHERE user_email=%s AND EXTRACT(MONTH FROM expense_date) = %s 
                 AND EXTRACT(YEAR FROM expense_date) = %s)
        """
        import calendar
        p_parts = period.split()
        m_num = list(calendar.month_name).index(p_parts[0])
        y_num = int(p_parts[1])
        
        res = fetch_query(query, (user_email, period, user_email, m_num, y_num))
        
        debt_res = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user_email,))
        
        return FinanceSummary(
            remaining_budget=res[0][0] if res and res[0][0] is not None else 0.0,
            net_debt=debt_res[0][0] if debt_res and debt_res[0][0] is not None else 0.0
        )

# --- 4. CACHE INVALIDATOR ---
def invalidate_user_caches():
    st.cache_data.clear()
