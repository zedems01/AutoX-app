import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Settings:

    # LLM Provider API Keys
    # GEMINI (Mandatory for news and context web deep research, and defined as fallback for agents inference)
    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    # OPENAI (Mainly used for agents inference)
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY")

    # twitterapi.io API Credentials
    X_API_KEY=os.getenv("X_API_KEY")   # from twitterapi.io
    USER_PROXY=os.getenv("USER_PROXY")
    # proxy example: http://username:password@ip:port
    # You can get proxy from: https://www.webshare.io/?referral_code=s5x49lhr7ck7

    # X Credentials
    USER_EMAIL=os.getenv("USER_EMAIL")
    USER_PASSWORD=os.getenv("USER_PASSWORD")

    # AWS S3 Settings for Image Storage (mandatory before posting on X)
    AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION=os.getenv("AWS_DEFAULT_REGION")
    BUCKET_NAME=os.getenv("BUCKET_NAME")

    # LangSmith API Keys for LLMs tracing (Optional)
    LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING", "false")   # set to true to allow tracing
    LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT", "x-automation-agent")

    # Some default settings (Optional, as we first check for them in the graph state)
    # LLMs
    GEMINI_BASE_MODEL=os.getenv("GEMINI_BASE_MODEL", "gemini-2.0-flash")
    GEMINI_REASONING_MODEL=os.getenv("GEMINI_REASONING_MODEL", "gemini-2.5-flash-lite-preview-06-17") # for reflection during deep research
    OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o")
    ANTHROPIC_MODEL=os.getenv("ANTHROPIC_MODEL")

    # Trend Fetching Settings (Optional)
    TRENDS_COUNT=os.getenv("TRENDS_COUNT", 30)
    TRENDS_WOEID=os.getenv("TRENDS_WOEID", 23424819)

    # Tweet Search Settings (Optional)
    MAX_TWEETS_TO_RETRIEVE=os.getenv("MAX_TWEETS_TO_RETRIEVE", 30)
    TWEETS_LANGUAGE=os.getenv("TWEETS_LANGUAGE", "english")

    # Content Language
    CONTENT_LANGUAGE=os.getenv("CONTENT_LANGUAGE", "english")



settings = Settings() 