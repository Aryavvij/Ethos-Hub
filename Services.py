from database import fetch_query, execute_query

class FocusService:
    @staticmethod
    def get_daily_logs(user_email, date):
        query = "SELECT task_name, duration_mins FROM focus_sessions WHERE user_email=%s AND session_date=%s"
        return fetch_query(query, (user_email, date))

class FinanceService:
    @staticmethod
    def get_net_liability(user_email):
        res = fetch_query("SELECT SUM(amount - paid_out) FROM debt WHERE user_email=%s", (user_email,))
        return res[0][0] if res and res[0][0] else 0
