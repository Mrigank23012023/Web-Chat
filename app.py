import streamlit as st
import sys
import traceback

st.title("🔍 Debug Mode - Checking Configuration")

try:
    st.write("✅ Streamlit loaded successfully")
    
    st.subheader("1. Checking Secrets")
    if hasattr(st, 'secrets'):
        st.write("✅ st.secrets is available")
        if 'GROQ_API_KEY' in st.secrets:
            st.write(f"✅ GROQ_API_KEY found (length: {len(st.secrets['GROQ_API_KEY'])})")
        else:
            st.error("❌ GROQ_API_KEY not in secrets")
            
        if 'PINECONE_API_KEY' in st.secrets:
            st.write(f"✅ PINECONE_API_KEY found (length: {len(st.secrets['PINECONE_API_KEY'])})")
        else:
            st.error("❌ PINECONE_API_KEY not in secrets")
    else:
        st.error("❌ st.secrets not available")
    
    st.subheader("2. Testing Imports")
    try:
        import logging
        st.write("✅ logging imported")
    except Exception as e:
        st.error(f"❌ logging: {e}")
    
    try:
        from config import Config
        st.write("✅ config.Config imported")
        st.write(f"  - GROQ_API_KEY: {'Set' if Config.GROQ_API_KEY else 'Missing'}")
        st.write(f"  - PINECONE_API_KEY: {'Set' if Config.PINECONE_API_KEY else 'Missing'}")
    except Exception as e:
        st.error(f"❌ config: {e}")
        st.code(traceback.format_exc())
    
    try:
        from frontend.ui import UI
        st.write("✅ frontend.ui imported")
    except Exception as e:
        st.error(f"❌ frontend.ui: {e}")
        st.code(traceback.format_exc())
    
    try:
        from backend.auth import Auth
        st.write("✅ backend.auth imported")
    except Exception as e:
        st.error(f"❌ backend.auth: {e}")
        st.code(traceback.format_exc())
        
    st.success("🎉 All imports successful! The app should work.")
    st.info("Replace this debug app.py with the real version once you confirm everything works.")
    
except Exception as e:
    st.error(f"Fatal error: {e}")
    st.code(traceback.format_exc())


