import streamlit as st
from backend.validator import Validator
import os

class UI:
    """Handles frontend UI components and state management."""
    
    @staticmethod
    def load_css():
        """Loads custom CSS."""
        css_file = "frontend/style.css"
        if os.path.exists(css_file):
            with open(css_file) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    @staticmethod
    def init_state():
        """Initialize session state variables if they don't exist."""
        if "indexed" not in st.session_state:
            st.session_state.indexed = False
        if "vectorstore" not in st.session_state:
            st.session_state.vectorstore = None
        if "memory" not in st.session_state:
            st.session_state.memory = None
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

    @staticmethod
    def render_login(auth_handler):
        """Renders the login screen with a centered form."""
        # Using columns to center the login form comfortably
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(
                """
                <div style='background-color: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);'>
                    <h1 style='text-align: center; margin-bottom: 0.5rem; font-size: 2rem;'>🔐 Agentic Access</h1>
                    <p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Please verify your identity to continue.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            with st.form("login_form", clear_on_submit=True):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                st.markdown("div", unsafe_allow_html=True) # Spacer
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)
                
                if submitted:
                    if auth_handler.login(username, password):
                        st.success("Authentication successful.")
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided.")
            
            st.markdown(
                """
                <div style='margin-top: 1rem; text-align: center; font-size: 0.85rem; color: #94a3b8;'>
                    Demo Access: <strong>admin</strong> / <strong>password</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

    @staticmethod
    def render_sidebar(auth_handler):
        """Renders the sidebar with session controls."""
        with st.sidebar:
            st.markdown("### ⚙️ Workspace")
            if st.session_state.get("username"):
                st.caption(f"Logged in as {st.session_state.username}")
            
            st.divider()
            
            if st.button("New Chat / Clear", use_container_width=True, type="secondary"):
                st.session_state.messages = []
                st.rerun()
                
            st.divider()
            
            if st.button("Sign Out", type="secondary", use_container_width=True):
                auth_handler.logout()

    @staticmethod
    def render_header():
        """Renders the application header."""
        st.markdown("# 🧠 Knowledge Agent")
        st.markdown(
            """
            <p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>
                Empower your research. Index any website URL to extract insights and chat with its content instantly.
            </p>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_input_section():
        """
        Renders the URL input and Index button.
        Returns the URL if indexing is triggered, else None.
        """
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                # Use session state key to persist input
                url = st.text_input("Target Website URL", placeholder="https://example.com/docs", key="url_input", label_visibility="collapsed")
            
            with col2:
                if st.button("Index Content", type="primary", use_container_width=True):
                    if not url:
                        st.warning("Please provide a valid URL.")
                        return None
                    
                    with st.spinner("Verifying accessibility..."):
                        validation_result = Validator.validate_gateway(url)
                    
                    if not validation_result["valid"]:
                        st.error(validation_result["error"])
                        return None
                    
                    return url
            
            # Show active indexed status with a cleaner look
            if st.session_state.get("indexed") and st.session_state.get("current_url"):
                st.markdown(
                    f"""
                    <div style='background-color: #f1f5f9; padding: 0.75rem 1rem; border-radius: 8px; border-left: 4px solid var(--highlight-green); margin-top: 1rem; display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='color: var(--highlight-green);'>●</span>
                        <span style='font-weight: 500; font-size: 0.9rem; color: #334155;'>Active Context: {st.session_state.current_url}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        return None

    @staticmethod
    def render_chat_interface():
        """Renders the chat history and input area."""
        st.divider()
        
        # Display chat history
        for message in st.session_state.messages:
            role = message["role"]
            avatar = "👤" if role == "user" else "🤖"
            with st.chat_message(role, avatar=avatar):
                st.markdown(message["content"])

        # Chat Input
        if st.session_state.indexed:
            if prompt := st.chat_input("Ask a specific question about the content..."):
                # Add user message to history
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)
                
                # Placeholder for bot response (mock)
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown("Processing query...")
                    
                st.session_state.messages.append({"role": "assistant", "content": "Processing query..."})
        else:
            st.info("👋 Please index a website above to begin the session.")
            st.chat_input("Waiting for content indexing...", disabled=True)
