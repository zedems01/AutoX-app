import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings:
    # X API Credentials
    X_API_KEY = os.getenv("X_API_KEY")
    X_API_SECRET_KEY = os.getenv("X_API_SECRET_KEY")
    X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")
    X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

    # LLM Provider API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Composio (for Notifications)
    COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")

settings = Settings() 