import time
import streamlit as st
from database import execute_query

class Telemetry:
    @staticmethod
    def log(category, event_name, value=0.0, metadata=None):
        """Universal logger for the Ethos System."""
        user = st.session_state.get('user_email', 'ANONYMOUS')
        execute_query(
            "INSERT INTO system_metrics (user_email, category, event_name, value, metadata) VALUES (%s, %s, %s, %s, %s)",
            (user, category, event_name, value, metadata if metadata else {})
        )

    @staticmethod
    def track_latency(event_name):
        """Context manager to track how long a block of code takes to run."""
        class LatencyTracker:
            def __enter__(self):
                self.start = time.time()
                return self
            def __exit__(self, type, value, traceback):
                duration = time.time() - self.start
                Telemetry.log('PERFORMANCE', event_name, value=duration)
        return LatencyTracker()
