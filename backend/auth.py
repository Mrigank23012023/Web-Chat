import streamlit as st
import time

class Auth:
    """Handles user authentication and session management."""

    @staticmethod
    def check_login():
        """Checks if the user is logged in."""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        return st.session_state.authenticated

    @staticmethod
    def login(username, password):
        """
        Simulates a login process.
        For Phase 2, we accept any non-empty credentials or specific ones.
        """
        time.sleep(1) # Simulate network delay
        
        # Mock validation
        if username and password:
            st.session_state.authenticated = True
            st.session_state.username = username
            return True
        return False

    @staticmethod
    def logout():
        """Logs out the user and clears session state."""
        st.session_state.clear()
        st.rerun()
