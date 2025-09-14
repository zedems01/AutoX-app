import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    GEMINI_RESEARCH_MODEL=os.getenv("GEMINI_RESEARCH_MODEL", "gemini-2.5-flash-lite")
    # GEMINI_RESEARCH_MODEL=os.getenv("GEMINI_RESEARCH_MODEL", "gemini-2.5-flash")
    GEMINI_IMAGE_MODEL=os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image-preview")
    GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL=os.getenv("OPENROUTER_MODEL", "openai/gpt-5")

    X_API_KEY=os.getenv("X_API_KEY")
    USER_PROXY=os.getenv("USER_PROXY")

    USER_EMAIL=os.getenv("USER_EMAIL")
    USER_NAME=os.getenv("USER_NAME")
    USER_PASSWORD=os.getenv("USER_PASSWORD")
    USER_TOTP_SECRET=os.getenv("USER_TOTP_SECRET")

    AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION=os.getenv("AWS_DEFAULT_REGION")
    BUCKET_NAME=os.getenv("BUCKET_NAME")

    LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING", "false")
    LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT", "x-automation-agent")

    TRENDS_COUNT=os.getenv("TRENDS_COUNT", 30)
    TRENDS_WOEID=os.getenv("TRENDS_WOEID", 23424819)
    MAX_TWEETS_TO_RETRIEVE=os.getenv("MAX_TWEETS_TO_RETRIEVE", 30)
    TWEETS_LANGUAGE=os.getenv("TWEETS_LANGUAGE", "english")
    CONTENT_LANGUAGE=os.getenv("CONTENT_LANGUAGE", "english")



settings = Settings() 