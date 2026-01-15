import os
from dotenv import load_dotenv

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
    
    REQUEST_TIMEOUT = 10
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    
    MAX_PAGES_CRAWL = 5
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150
    
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    
    RETRIEVAL_TOP_K = 4
    
    GROQ_API_KEY = get_secret("GROQ_API_KEY")
    LLM_MODEL_NAME = "llama-3.3-70b-versatile"
    LLM_BASE_URL = "https://api.groq.com/openai/v1"
    LLM_TEMPERATURE = 0
    
    PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
    VECTOR_STORE_PROVIDER = "pinecone" # Enforced
    PINECONE_INDEX_NAME = "website-content"

    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
             print("⚠️ WARNING: GROQ_API_KEY is missing. RAG features will fail.")
        
        if not cls.PINECONE_API_KEY:
            print("⚠️ WARNING: PINECONE_API_KEY is missing. RAG features will fail.")
        pass

Config.validate()
