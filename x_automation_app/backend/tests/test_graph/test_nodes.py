"""Tests for simple graph nodes."""
import pytest
from backend.app.agents.graph import (
    await_topic_selection, await_content_validation,
    await_image_validation, auto_select_topic
)


class TestAwaitTopicSelection:
    """Tests for await_topic_selection node."""

    def test_await_topic_selection_sets_correct_state(self, initial_state):
        """Test that await_topic_selection sets the correct human input step."""
        result = await_topic_selection(initial_state)
        
        assert result["next_human_input_step"] == "await_topic_selection"

    def test_await_topic_selection_returns_dict(self, initial_state):
        """Test that await_topic_selection returns a dictionary."""
        result = await_topic_selection(initial_state)
        
        assert isinstance(result, dict)
        assert "next_human_input_step" in result


class TestAwaitContentValidation:
    """Tests for await_content_validation node."""

    def test_await_content_validation_sets_correct_state(self, initial_state):
        """Test that await_content_validation sets the correct human input step."""
        result = await_content_validation(initial_state)
        
        assert result["next_human_input_step"] == "await_content_validation"

    def test_await_content_validation_returns_dict(self, initial_state):
        """Test that await_content_validation returns a dictionary."""
        result = await_content_validation(initial_state)
        
        assert isinstance(result, dict)
        assert "next_human_input_step" in result


class TestAwaitImageValidation:
    """Tests for await_image_validation node."""

    def test_await_image_validation_sets_correct_state(self, initial_state):
        """Test that await_image_validation sets the correct human input step."""
        result = await_image_validation(initial_state)
        
        assert result["next_human_input_step"] == "await_image_validation"

    def test_await_image_validation_returns_dict(self, initial_state):
        """Test that await_image_validation returns a dictionary."""
        result = await_image_validation(initial_state)
        
        assert isinstance(result, dict)
        assert "next_human_input_step" in result


class TestAutoSelectTopic:
    """Tests for auto_select_topic node."""

    def test_auto_select_topic_selects_first_trend(self, initial_state, mock_trends):
        """Test that auto_select_topic selects the first trending topic."""
        state = initial_state.copy()
        state["trending_topics"] = mock_trends
        
        result = auto_select_topic(state)
        
        assert "selected_topic" in result
        assert result["selected_topic"].name == mock_trends[0].name
        assert result["selected_topic"].rank == mock_trends[0].rank

    def test_auto_select_topic_with_empty_trends(self, initial_state):
        """Test auto_select_topic when no trends are available."""
        state = initial_state.copy()
        state["trending_topics"] = []
        
        result = auto_select_topic(state)
        
        # Should return empty dict or handle gracefully
        assert result == {}

    def test_auto_select_topic_with_none_trends(self, initial_state):
        """Test auto_select_topic when trending_topics is None."""
        state = initial_state.copy()
        state["trending_topics"] = None
        
        result = auto_select_topic(state)
        
        assert result == {}

    def test_auto_select_topic_returns_dict(self, initial_state, mock_trends):
        """Test that auto_select_topic returns a dictionary."""
        state = initial_state.copy()
        state["trending_topics"] = mock_trends
        
        result = auto_select_topic(state)
        
        assert isinstance(result, dict)

    def test_auto_select_topic_preserves_topic_data(self, initial_state, mock_trends):
        """Test that auto_select_topic preserves all topic data."""
        state = initial_state.copy()
        state["trending_topics"] = mock_trends
        
        result = auto_select_topic(state)
        
        selected = result["selected_topic"]
        first_trend = mock_trends[0]
        
        assert selected.name == first_trend.name
        assert selected.rank == first_trend.rank
        assert selected.tweet_count == first_trend.tweet_count

