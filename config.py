import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration for the application."""
    
    # Example: API Keys (to be filled later)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Add other configuration constants here
    CHROMA_DB_PATH = "chroma_db"
    
    @classmethod
    def validate(cls):
        """Validate critical configuration."""
        # if not cls.OPENAI_API_KEY:
        #     raise ValueError("OPENAI_API_KEY environment variable is missing.")
        pass

# Validate on import
Config.validate()
