import time
import streamlit as st

class Telemetry:
    @staticmethod
    def log(category, event_name, value=0.0, metadata=None):
        """Universal logger using a Local Import to break the circular loop."""
        from database import execute_query 
        
        user = st.session_state.get('user_email', 'ANONYMOUS')
        execute_query(
            "INSERT INTO system_metrics (user_email, category, event_name, value, metadata) VALUES (%s, %s, %s, %s, %s)",
            (user, category, event_name, value, metadata if metadata else {})
        )

    @staticmethod
    def track_latency(event_name):
        class LatencyTracker:
            def __enter__(self):
                self.start = time.time()
                return self
            def __exit__(self, type, value, traceback):
                duration = time.time() - self.start
                Telemetry.log('PERFORMANCE', event_name, value=duration)
        return LatencyTracker()
