import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_secret(key, default=None):
    import sys
    value = os.getenv(key, default)
    if 'streamlit' in sys.modules:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and key in st.secrets:
                value = st.secrets[key]
        except:
            pass
    return value

class Config:
    """Central configuration for the application."""
    
    CHROMA_DB_PATH = "chroma_db"
    
    REQUEST_TIMEOUT = 10
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    
    MAX_PAGES_CRAWL = 5
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    
    RETRIEVAL_TOP_K = 4
    
    # LLM Config (Groq)
    GROQ_API_KEY = get_secret("GROQ_API_KEY")
    LLM_MODEL_NAME = "llama-3.3-70b-versatile"
    LLM_BASE_URL = "https://api.groq.com/openai/v1"
    LLM_TEMPERATURE = 0
    
    # Pinecone/Vector Store Config
    PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
    # Default to 'chroma' if not set
    VECTOR_STORE_PROVIDER = get_secret("VECTOR_STORE_PROVIDER", "chroma").lower()
    PINECONE_INDEX_NAME = "website-content"

    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        if not cls.GROQ_API_KEY:
             print("⚠️ WARNING: GROQ_API_KEY is missing. RAG features will fail.")
        
        if cls.VECTOR_STORE_PROVIDER == "pinecone" and not cls.PINECONE_API_KEY:
            print("⚠️ WARNING: PINECONE_API_KEY is missing but provider is set to 'pinecone'. RAG features will fail.")
        pass

# Validate on import
Config.validate()
