"""Tests for state management."""
import pytest
from backend.app.agents.state import OverallState
from backend.app.utils.schemas import Trend, UserConfigSchema, UserDetails


class TestOverallState:
    """Tests for OverallState."""

    def test_state_initialization_with_all_required_fields(self, mock_user_details, mock_user_config):
        """Test OverallState initialization with all required fields."""
        state = OverallState(
            is_autonomous_mode=False,
            output_destination="DOWNLOAD",
            has_user_provided_topic=False,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="professional",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="workflow_started",
            session="test_session",
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
        
        assert state["is_autonomous_mode"] is False
        assert state["output_destination"] == "DOWNLOAD"
        assert state["current_step"] == "workflow_started"
        assert state["max_research_loops"] == 3
        assert state["research_loop_count"] == 0

    def test_state_with_autonomous_mode_enabled(self, mock_user_details, mock_user_config):
        """Test state initialization with autonomous mode enabled."""
        state = OverallState(
            is_autonomous_mode=True,
            output_destination="PUBLISH_X",
            has_user_provided_topic=False,
            x_content_type="THREAD",
            content_length="LONG",
            brand_voice="casual",
            target_audience="general",
            user_config=mock_user_config,
            current_step="trend_harvester",
            session="test_session",
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
        
        assert state["is_autonomous_mode"] is True
        assert state["output_destination"] == "PUBLISH_X"
        assert state["next_human_input_step"] is None

    def test_state_with_autonomous_mode_disabled(self, mock_user_details, mock_user_config):
        """Test state initialization with autonomous mode disabled (manual mode)."""
        state = OverallState(
            is_autonomous_mode=False,
            output_destination="DOWNLOAD",
            has_user_provided_topic=False,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="professional",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="workflow_started",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step="await_topic_selection",
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
        
        assert state["is_autonomous_mode"] is False
        assert state["next_human_input_step"] == "await_topic_selection"

    def test_state_with_user_provided_topic(self, mock_user_details, mock_user_config):
        """Test state with user-provided topic."""
        state = OverallState(
            is_autonomous_mode=False,
            output_destination="DOWNLOAD",
            has_user_provided_topic=True,
            user_provided_topic="Python 3.13 Features",
            x_content_type="TWEET",
            content_length="MEDIUM",
            brand_voice="educational",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="tweet_searcher",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step=None,
            messages=[],
            trending_topics=None,
            selected_topic=None,
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
        
        assert state["has_user_provided_topic"] is True
        assert state["user_provided_topic"] == "Python 3.13 Features"
        assert state["trending_topics"] is None

    def test_state_with_trending_topics(self, mock_user_details, mock_user_config, mock_trends):
        """Test state with trending topics."""
        state = OverallState(
            is_autonomous_mode=False,
            output_destination="DOWNLOAD",
            has_user_provided_topic=False,
            user_provided_topic=None,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="casual",
            target_audience="general",
            user_config=mock_user_config,
            current_step="trend_harvester",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step=None,
            messages=[],
            trending_topics=mock_trends,
            selected_topic=None,
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
        
        assert state["has_user_provided_topic"] is False
        assert state["trending_topics"] is not None
        assert len(state["trending_topics"]) == 3

    def test_state_with_selected_topic(self, mock_user_details, mock_user_config, mock_trends):
        """Test state with selected topic."""
        selected = mock_trends[0]
        
        state = OverallState(
            is_autonomous_mode=True,
            output_destination="PUBLISH_X",
            has_user_provided_topic=False,
            user_provided_topic=None,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="professional",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="tweet_searcher",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step=None,
            messages=[],
            trending_topics=mock_trends,
            selected_topic=selected,
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
        
        assert state["selected_topic"] is not None
        assert state["selected_topic"].name == "Python"

    def test_state_with_content_data(self, mock_user_details, mock_user_config):
        """Test state with content generation data."""
        state = OverallState(
            is_autonomous_mode=False,
            output_destination="DOWNLOAD",
            has_user_provided_topic=False,
            user_provided_topic=None,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="professional",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="quality_assurer",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step=None,
            messages=[],
            trending_topics=None,
            selected_topic=None,
            tweet_search_results=None,
            opinion_summary="Public is excited about new features",
            overall_sentiment="Positive",
            topic_from_opinion_analysis="Python 3.13",
            final_deep_research_report="Detailed research report",
            search_query=[],
            web_research_result=[],
            sources_gathered=[],
            initial_search_query_count=0,
            max_research_loops=3,
            research_loop_count=2,
            content_draft="Draft tweet content",
            image_prompts=["Python logo", "Code snippet"],
            final_content="Final tweet content",
            final_image_prompts=["Python logo"],
            generated_images=None,
            publication_id=None,
            validation_result=None,
            error_message=None,
        )
        
        assert state["opinion_summary"] == "Public is excited about new features"
        assert state["overall_sentiment"] == "Positive"
        assert state["content_draft"] == "Draft tweet content"
        assert state["final_content"] == "Final tweet content"
        assert len(state["image_prompts"]) == 2
        assert state["research_loop_count"] == 2

    def test_state_with_error(self, mock_user_details, mock_user_config):
        """Test state with error message."""
        state = OverallState(
            is_autonomous_mode=False,
            output_destination="DOWNLOAD",
            has_user_provided_topic=False,
            user_provided_topic=None,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="professional",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="error",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step=None,
            messages=[],
            trending_topics=None,
            selected_topic=None,
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
            error_message="An error occurred during processing",
        )
        
        assert state["current_step"] == "error"
        assert state["error_message"] == "An error occurred during processing"

    def test_state_research_loop_tracking(self, mock_user_details, mock_user_config):
        """Test state tracks research loop count."""
        state = OverallState(
            is_autonomous_mode=True,
            output_destination="DOWNLOAD",
            has_user_provided_topic=False,
            user_provided_topic=None,
            x_content_type="TWEET",
            content_length="SHORT",
            brand_voice="professional",
            target_audience="developers",
            user_config=mock_user_config,
            current_step="reflection",
            session="test_session",
            user_details=mock_user_details,
            proxy="http://proxy.example.com:8080",
            next_human_input_step=None,
            messages=[],
            trending_topics=None,
            selected_topic=None,
            tweet_search_results=None,
            opinion_summary=None,
            overall_sentiment=None,
            topic_from_opinion_analysis=None,
            final_deep_research_report=None,
            search_query=["query1", "query2"],
            web_research_result=[],
            sources_gathered=[],
            initial_search_query_count=2,
            max_research_loops=3,
            research_loop_count=1,
            content_draft=None,
            image_prompts=None,
            final_content=None,
            final_image_prompts=None,
            generated_images=None,
            publication_id=None,
            validation_result=None,
            error_message=None,
        )
        
        assert state["research_loop_count"] == 1
        assert state["max_research_loops"] == 3
        assert state["initial_search_query_count"] == 2
        assert len(state["search_query"]) == 2

