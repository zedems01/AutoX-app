"""Pytest fixtures and configuration for all tests."""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.agents.state import OverallState
from backend.app.utils.schemas import (
    Trend, TweetSearched, TweetAuthor, ValidationResult,
    ValidationAction, ValidationData, UserDetails, UserConfigSchema
)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_x_api_response():
    """Mock response from X API for successful login."""
    return {
        "login_cookies": "mock_session_cookie_12345",
        "message": "Login successful"
    }


@pytest.fixture
def mock_trends():
    """Mock trending topics data."""
    return [
        Trend(name="Python", rank=1, tweet_count="10.5K posts"),
        Trend(name="AI", rank=2, tweet_count="8.2K posts"),
        Trend(name="FastAPI", rank=3, tweet_count="5.1K posts"),
    ]


@pytest.fixture
def mock_tweet_author():
    """Mock tweet author data."""
    return TweetAuthor(
        userName="testuser",
        name="Test User",
    )


@pytest.fixture
def mock_tweets(mock_tweet_author):
    """Mock tweet search results."""
    return [
        TweetSearched(
            text="This is a test tweet about Python",
            retweetCount=10,
            replyCount=5,
            likeCount=20,
            viewCount=100,
            createdAt="2025-01-01T12:00:00Z",
            author=mock_tweet_author
        ),
        TweetSearched(
            text="Another tweet about AI and machine learning",
            retweetCount=15,
            replyCount=8,
            likeCount=30,
            viewCount=200,
            author=mock_tweet_author
        ),
    ]


@pytest.fixture
def mock_user_details():
    """Mock user details."""
    return UserDetails(
        user_name="testuser",
        email="test@example.com"
    )


@pytest.fixture
def mock_user_config():
    """Mock user configuration."""
    return UserConfigSchema(
        trends_count=10,
        trends_woeid=1,
        max_tweets_to_retrieve=50,
        tweets_language="en",
        content_language="en"
    )


@pytest.fixture
def initial_state(mock_user_details, mock_user_config):
    """Mock initial workflow state."""
    return OverallState(
        is_autonomous_mode=False,
        output_destination="DOWNLOAD",
        has_user_provided_topic=False,
        x_content_type="TWEET",
        content_length="SHORT",
        brand_voice="professional",
        target_audience="developers",
        user_config=mock_user_config,
        current_step="workflow_started",
        session="mock_session_12345",
        user_details=mock_user_details,
        proxy="http://proxy.example.com:8080",
        next_human_input_step=None,
        messages=[],
        trending_topics=None,
        selected_topic=None,
        user_provided_topic=None,
        tweet_search_results=None,
        opinion_summary=None,
        overall_sentiment=None,
        topic_from_opinion_analysis=None,
        final_deep_research_report=None,
        search_query=[],
        web_research_result=[],
        sources_gathered=[],
        initial_search_query_count=0,
        max_research_loops=3,
        research_loop_count=0,
        content_draft=None,
        image_prompts=None,
        final_content=None,
        final_image_prompts=None,
        generated_images=None,
        publication_id=None,
        validation_result=None,
        error_message=None,
    )


@pytest.fixture
def validation_approve():
    """Mock validation result with approve action."""
    return ValidationResult(
        action=ValidationAction.APPROVE,
        data=None
    )


@pytest.fixture
def validation_reject():
    """Mock validation result with reject action."""
    return ValidationResult(
        action=ValidationAction.REJECT,
        data=ValidationData(
            feedback="Please revise the content to be more engaging."
        )
    )


@pytest.fixture
def validation_edit_topic(mock_trends):
    """Mock validation result with edit action for topic selection."""
    return ValidationResult(
        action=ValidationAction.EDIT,
        data=ValidationData(
            extra_data={"selected_topic": mock_trends[1].model_dump()}
        )
    )


@pytest.fixture
def mock_graph_state(initial_state):
    """Mock graph state object."""
    mock_state = MagicMock()
    mock_state.values = initial_state
    return mock_state


@pytest.fixture
def mock_env_settings(monkeypatch):
    """Mock environment settings for demo login."""
    monkeypatch.setenv("DEMO_TOKEN", "test_demo_token_12345")
    monkeypatch.setenv("TEST_USER_NAME", "demo_user")
    monkeypatch.setenv("TEST_USER_EMAIL", "demo@example.com")
    monkeypatch.setenv("TEST_USER_PASSWORD", "demo_password")
    monkeypatch.setenv("TEST_USER_PROXY", "http://proxy.example.com:8080")
    monkeypatch.setenv("TEST_USER_TOTP_SECRET", "ABCD1234EFGH5678")
    
    # Reload settings after setting env vars
    from ..app.config import Settings
    return Settings()


@pytest.fixture
def mock_requests_post(mocker):
    """Mock requests.post for X API calls."""
    return mocker.patch("requests.post")


@pytest.fixture
def mock_requests_get(mocker):
    """Mock requests.get for X API calls."""
    return mocker.patch("requests.get")

