import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
    GEMINI_RESEARCH_MODEL=os.getenv("GEMINI_RESEARCH_MODEL", "gemini-2.5-flash")
    GEMINI_IMAGE_MODEL=os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
    GEMINI_MODEL=os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL=os.getenv("OPENROUTER_MODEL", "openai/gpt-5-mini")

    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    OPENAI_IMAGE_MODEL=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

    X_API_KEY=os.getenv("X_API_KEY")
    USER_PROXY=os.getenv("USER_PROXY")

    USER_EMAIL=os.getenv("USER_EMAIL")
    USER_NAME=os.getenv("USER_NAME")
    USER_PASSWORD=os.getenv("USER_PASSWORD")
    USER_TOTP_SECRET=os.getenv("USER_TOTP_SECRET")

    TEST_USER_EMAIL=os.getenv("TEST_USER_EMAIL")
    TEST_USER_NAME=os.getenv("TEST_USER_NAME", "autoxtest")
    TEST_USER_PASSWORD=os.getenv("TEST_USER_PASSWORD")
    TEST_USER_TOTP_SECRET=os.getenv("TEST_USER_TOTP_SECRET")
    TEST_USER_PROXY=os.getenv("TEST_USER_PROXY")

    DEMO_TOKEN=os.getenv("DEMO_TOKEN")

    AWS_ACCESS_KEY_ID=os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY=os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION=os.getenv("AWS_DEFAULT_REGION", "eu-west-3")
    BUCKET_NAME=os.getenv("BUCKET_NAME", "x-automation-agent")

    LANGSMITH_TRACING=os.getenv("LANGSMITH_TRACING", "false")
    LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT", "x-automation-agent")

    TRENDS_COUNT=os.getenv("TRENDS_COUNT", 30)
    TRENDS_WOEID=os.getenv("TRENDS_WOEID", 23424819)
    MAX_TWEETS_TO_RETRIEVE=os.getenv("MAX_TWEETS_TO_RETRIEVE", 15)
    TWEETS_LANGUAGE=os.getenv("TWEETS_LANGUAGE", "english")
    CONTENT_LANGUAGE=os.getenv("CONTENT_LANGUAGE", "english")



settings = Settings() 