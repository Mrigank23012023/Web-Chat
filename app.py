import streamlit as st
from config import Config

def main():
    """Main entry point for the Streamlit application."""
    st.set_page_config(page_title="AI Website Chatbot", page_icon="🤖")
    st.title("AI Website Chatbot")
    st.write("Welcome! Please configure the application.")

if __name__ == "__main__":
    main()
