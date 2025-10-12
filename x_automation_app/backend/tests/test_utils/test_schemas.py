"""Tests for Pydantic schemas."""
import pytest
from pydantic import ValidationError
from backend.app.utils.schemas import (
    Trend, TweetSearched, TweetAuthor, ValidationResult, ValidationAction,
    ValidationData, UserConfigSchema, OpinionAnalysisOutput, WriterOutput,
    QAOutput, GeneratedImage, UserDetails
)


class TestTrend:
    """Tests for Trend schema."""

    def test_trend_with_all_fields(self):
        """Test Trend model with all fields."""
        trend = Trend(
            name="Python",
            rank=1,
            tweet_count="10.5K posts"
        )
        assert trend.name == "Python"
        assert trend.rank == 1
        assert trend.tweet_count == "10.5K posts"

    def test_trend_with_required_field_only(self):
        """Test Trend model with only required field."""
        trend = Trend(name="Python")
        assert trend.name == "Python"
        assert trend.rank is None
        assert trend.tweet_count is None

    def test_trend_serialization(self):
        """Test Trend model serialization."""
        trend = Trend(name="FastAPI", rank=5, tweet_count="2K posts")
        data = trend.model_dump()
        assert data["name"] == "FastAPI"
        assert data["rank"] == 5


class TestTweetAuthor:
    """Tests for TweetAuthor schema."""

    def test_tweet_author(self):
        """Test TweetAuthor model."""
        author = TweetAuthor(
            userName="testuser",
            name="Test User"
        )
        assert author.userName == "testuser"
        assert author.name == "Test User"

    def test_tweet_author_validation_error(self):
        """Test TweetAuthor validation with missing required fields."""
        with pytest.raises(ValidationError):
            TweetAuthor(userName="testuser")  # Missing 'name'


class TestTweetSearched:
    """Tests for TweetSearched schema."""

    def test_tweet_searched_full(self):
        """Test TweetSearched model with all fields."""
        author = TweetAuthor(userName="user1", name="User One")
        tweet = TweetSearched(
            text="Test tweet content",
            retweetCount=10,
            replyCount=5,
            likeCount=20,
            viewCount=100,
            createdAt="2025-01-01T12:00:00Z",
            author=author
        )
        assert tweet.text == "Test tweet content"
        assert tweet.retweetCount == 10
        assert tweet.author.userName == "user1"

    def test_tweet_searched_serialization(self):
        """Test TweetSearched serialization."""
        author = TweetAuthor(userName="user1", name="User One")
        tweet = TweetSearched(
            text="Test tweet",
            retweetCount=5,
            replyCount=2,
            likeCount=10,
            viewCount=50,
            createdAt="2025-01-01",
            author=author
        )
        data = tweet.model_dump()
        assert "text" in data
        assert "author" in data
        assert data["author"]["userName"] == "user1"


class TestValidationAction:
    """Tests for ValidationAction enum."""

    def test_validation_action_values(self):
        """Test ValidationAction enum values."""
        assert ValidationAction.APPROVE == "approve"
        assert ValidationAction.REJECT == "reject"
        assert ValidationAction.EDIT == "edit"

    def test_validation_action_from_string(self):
        """Test creating ValidationAction from string."""
        action = ValidationAction("approve")
        assert action == ValidationAction.APPROVE


class TestValidationResult:
    """Tests for ValidationResult schema."""

    def test_validation_result_approve(self):
        """Test ValidationResult with approve action."""
        result = ValidationResult(action=ValidationAction.APPROVE)
        assert result.action == ValidationAction.APPROVE
        assert result.data is None

    def test_validation_result_reject_with_feedback(self):
        """Test ValidationResult with reject action and feedback."""
        result = ValidationResult(
            action=ValidationAction.REJECT,
            data=ValidationData(feedback="Please improve this")
        )
        assert result.action == ValidationAction.REJECT
        assert result.data.feedback == "Please improve this"

    def test_validation_result_edit_with_extra_data(self):
        """Test ValidationResult with edit action and extra data."""
        result = ValidationResult(
            action=ValidationAction.EDIT,
            data=ValidationData(
                extra_data={"final_content": "Updated content"}
            )
        )
        assert result.action == ValidationAction.EDIT
        assert result.data.extra_data["final_content"] == "Updated content"

    def test_validation_result_serialization(self):
        """Test ValidationResult serialization."""
        result = ValidationResult(
            action=ValidationAction.APPROVE,
            data=ValidationData(feedback="Looks good")
        )
        data = result.model_dump()
        assert data["action"] == "approve"
        assert data["data"]["feedback"] == "Looks good"


class TestUserConfigSchema:
    """Tests for UserConfigSchema."""

    def test_user_config_with_partial_data(self):
        """Test UserConfigSchema with partial data."""
        config = UserConfigSchema(
            trends_count=10,
            max_tweets_to_retrieve=50
        )
        assert config.trends_count == 10
        assert config.max_tweets_to_retrieve == 50
        assert config.gemini_model is None
        assert config.openrouter_model is None

    def test_user_config_with_all_fields(self):
        """Test UserConfigSchema with all fields."""
        config = UserConfigSchema(
            gemini_model="gemini-1.5-pro",
            openrouter_model="anthropic/claude-3-opus",
            trends_count=20,
            trends_woeid=1,
            max_tweets_to_retrieve=100,
            tweets_language="en",
            content_language="en"
        )
        assert config.gemini_model == "gemini-1.5-pro"
        assert config.trends_count == 20
        assert config.tweets_language == "en"

    def test_user_config_empty(self):
        """Test UserConfigSchema with no fields."""
        config = UserConfigSchema()
        assert config.trends_count is None
        assert config.trends_woeid is None


class TestOpinionAnalysisOutput:
    """Tests for OpinionAnalysisOutput schema."""

    def test_opinion_analysis_output(self):
        """Test OpinionAnalysisOutput model."""
        output = OpinionAnalysisOutput(
            opinion_summary="People are excited about Python 3.13",
            overall_sentiment="Positive",
            topic_from_opinion_analysis="Python 3.13 Release"
        )
        assert output.opinion_summary == "People are excited about Python 3.13"
        assert output.overall_sentiment == "Positive"
        assert output.topic_from_opinion_analysis == "Python 3.13 Release"

    def test_opinion_analysis_validation_error(self):
        """Test OpinionAnalysisOutput validation with missing fields."""
        with pytest.raises(ValidationError):
            OpinionAnalysisOutput(
                opinion_summary="Summary only"
                # Missing required fields
            )


class TestWriterOutput:
    """Tests for WriterOutput schema."""

    def test_writer_output(self):
        """Test WriterOutput model."""
        output = WriterOutput(
            content_draft="This is a great tweet about Python",
            image_prompts=["Python logo", "Code snippet"]
        )
        assert output.content_draft == "This is a great tweet about Python"
        assert len(output.image_prompts) == 2
        assert output.image_prompts[0] == "Python logo"

    def test_writer_output_with_empty_prompts(self):
        """Test WriterOutput with empty image prompts."""
        output = WriterOutput(
            content_draft="Tweet content",
            image_prompts=[]
        )
        assert output.content_draft == "Tweet content"
        assert output.image_prompts == []


class TestQAOutput:
    """Tests for QAOutput schema."""

    def test_qa_output(self):
        """Test QAOutput model."""
        output = QAOutput(
            final_content="Final polished tweet content",
            final_image_prompts=["Professional image prompt"]
        )
        assert output.final_content == "Final polished tweet content"
        assert len(output.final_image_prompts) == 1


class TestGeneratedImage:
    """Tests for GeneratedImage schema."""

    def test_generated_image(self):
        """Test GeneratedImage model."""
        image = GeneratedImage(
            is_generated=True,
            image_name="test_image.png",
            local_file_path="/tmp/images/test_image.png",
            s3_url="https://s3.amazonaws.com/bucket/test_image.png"
        )
        assert image.is_generated is True
        assert image.image_name == "test_image.png"
        assert image.local_file_path == "/tmp/images/test_image.png"
        assert image.s3_url == "https://s3.amazonaws.com/bucket/test_image.png"

    def test_generated_image_serialization(self):
        """Test GeneratedImage serialization."""
        image = GeneratedImage(
            is_generated=False,
            image_name="placeholder.png",
            local_file_path="/tmp/placeholder.png",
            s3_url="https://example.com/placeholder.png"
        )
        data = image.model_dump()
        assert data["is_generated"] is False
        assert "image_name" in data


class TestUserDetails:
    """Tests for UserDetails schema."""

    def test_user_details(self):
        """Test UserDetails model."""
        details = UserDetails(
            name="John Doe",
            username="johndoe"
        )
        assert details.name == "John Doe"
        assert details.username == "johndoe"

    def test_user_details_optional_fields(self):
        """Test UserDetails with optional fields."""
        details = UserDetails()
        assert details.name is None
        assert details.username is None

    def test_user_details_partial(self):
        """Test UserDetails with partial data."""
        details = UserDetails(username="testuser")
        assert details.username == "testuser"
        assert details.name is None

