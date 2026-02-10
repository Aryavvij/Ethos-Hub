from database import fetch_query, execute_query
from pydantic import BaseModel
from datetime import datetime as dt
from typing import List
import streamlit as st 

class FocusSession(BaseModel):
    task_name: str
    duration_mins: int

class FinanceSummary(BaseModel):
    remaining_budget: float = 0.0
    net_debt: float = 0.0

class FocusService:
    @staticmethod
    @st.cache_data(ttl=600) 
    def get_daily_logs(user_email: str, date) -> List[FocusSession]:
        query = "SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date=%s"
        raw_data = fetch_query(query, (user_email, date))
        return [FocusSession(task_name=row[0], duration_mins=row[1]) for row in raw_data]

class FinanceService:
    @staticmethod
    @st.cache_data(ttl=300) 
    def get_dashboard_metrics(user_email: str, period: str) -> FinanceSummary:
        budget_res = fetch_query("SELECT SUM(plan - actual) FROM finances WHERE user_email=%s AND period=%s", (user_email, period))
        debt_res = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user_email,))
        
        return FinanceSummary(
            remaining_budget=budget_res[0][0] if budget_res and budget_res[0][0] else 0.0,
            net_debt=debt_res[0][0] if debt_res and debt_res[0][0] else 0.0
        )
