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

# --- 2. FOCUS SERVICE (Productivity Logic) ---
class FocusService:
    @staticmethod
    @st.cache_data(ttl=600)
    def get_daily_logs(user_email: str, date) -> List[FocusSession]:
        """Fetches all focus logs for a specific date."""
        query = "SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date=%s"
        raw_data = fetch_query(query, (user_email, date))
        return [FocusSession(task_name=row[0], duration_mins=row[1]) for row in raw_data]

    @staticmethod
    @st.cache_data(ttl=600)
    def get_stats_overview(user_email: str) -> Tuple[int, int, float, float]:
        """
        Calculates Today, Daily Avg, Weekly Total, and Monthly Total.
        Industry Standard: Multi-subquery CTE for single-trip data retrieval.
        """
        query = """
            WITH daily_totals AS (
                SELECT session_date, SUM(duration_mins) as total_mins
                FROM focus_sessions WHERE user_email = %s GROUP BY session_date
            )
            SELECT 
                (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions 
                 WHERE user_email = %s AND session_date = CURRENT_DATE) as today,
                (SELECT COALESCE(AVG(total_mins), 0) FROM daily_totals) as daily_avg,
                (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions 
                 WHERE user_email = %s AND session_date >= DATE_TRUNC('week', CURRENT_DATE)) as week_total,
                (SELECT COALESCE(SUM(duration_mins), 0) FROM focus_sessions 
                 WHERE user_email = %s AND session_date >= DATE_TRUNC('month', CURRENT_DATE)) as month_total
        """
        res = fetch_query(query, (user_email, user_email, user_email, user_email))
        return res[0] if res else (0, 0, 0, 0)

# --- 3. FINANCE SERVICE (Capital Logic) ---
class FinanceService:
    @staticmethod
    @st.cache_data(ttl=300)
    def get_dashboard_metrics(user_email: str, period: str) -> FinanceSummary:
        """Calculates budget remaining and total debt."""
        budget_res = fetch_query("SELECT SUM(plan - actual) FROM finances WHERE user_email=%s AND period=%s", (user_email, period))
        debt_res = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user_email,))
        
        return FinanceSummary(
            remaining_budget=budget_res[0][0] if budget_res and budget_res[0][0] else 0.0,
            net_debt=debt_res[0][0] if debt_res and debt_res[0][0] else 0.0
        )

# --- 4. CACHE UTILITY ---
def invalidate_user_caches():
    """
    Industry Concept: Cache Invalidation.
    Call this whenever a user ADDS or DELETES data to ensure the UI updates.
    """
    st.cache_data.clear()
