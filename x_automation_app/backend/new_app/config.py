import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings:
    # X API Credentials
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    # TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID")
    # TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET")
    
    # Twitter API Credentials
    X_API_KEY = os.getenv("X_API_KEY")
    USER_EMAIL = os.getenv("USER_EMAIL")
    USER_PASSWORD = os.getenv("USER_PASSWORD")
    USER_PROXY = os.getenv("USER_PROXY")


    # LLM Provider API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Composio (for Notifications)
    COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")

    # AWS S3 Settings for Image Storage
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    # Trend fetching settings
    TRENDS_WOEID = int(os.getenv("TRENDS_WOEID", "1"))  # Default to 1 (Worldwide)
    TRENDS_COUNT = int(os.getenv("TRENDS_COUNT", "30")) # Default to 30

settings = Settings() 