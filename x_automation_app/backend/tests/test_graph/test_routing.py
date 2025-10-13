"""Tests for graph routing functions."""
import pytest
from backend.app.agents.graph import (
    initial_routing, route_after_trend_harvester,
    route_after_qa, route_after_validation,
    route_after_image_generation
)
from backend.app.agents.state import OverallState
from backend.app.utils.schemas import Trend, ValidationAction


class TestInitialRouting:
    """Tests for initial_routing function."""

    def test_routing_with_user_provided_topic(self, initial_state):
        """Test routing when user provides a topic."""
        state = initial_state.copy()
        state["has_user_provided_topic"] = True
        state["user_provided_topic"] = "Python 3.13"
        
        route = initial_routing(state)
        assert route == "tweet_searcher"

    def test_routing_without_user_provided_topic(self, initial_state):
        """Test routing when no user topic is provided."""
        state = initial_state.copy()
        state["has_user_provided_topic"] = False
        state["user_provided_topic"] = None
        
        route = initial_routing(state)
        assert route == "trend_harvester"


class TestRouteAfterTrendHarvester:
    """Tests for route_after_trend_harvester function."""

    def test_routing_in_autonomous_mode(self, initial_state, mock_trends):
        """Test routing in autonomous mode."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = True
        state["trending_topics"] = mock_trends
        
        route = route_after_trend_harvester(state)
        assert route == "auto_select_topic"

    def test_routing_in_manual_mode(self, initial_state, mock_trends):
        """Test routing in manual mode."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["trending_topics"] = mock_trends
        
        route = route_after_trend_harvester(state)
        assert route == "await_topic_selection"


class TestRouteAfterQA:
    """Tests for route_after_qa function."""

    def test_routing_in_autonomous_mode_with_image_prompts(self, initial_state):
        """Test routing in autonomous mode with image prompts."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = True
        state["final_image_prompts"] = ["Python logo", "Code snippet"]
        
        route = route_after_qa(state)
        assert route == "image_generator"

    def test_routing_in_autonomous_mode_without_image_prompts(self, initial_state):
        """Test routing in autonomous mode without image prompts."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = True
        state["final_image_prompts"] = None
        
        route = route_after_qa(state)
        assert route == "publicator"

    def test_routing_in_autonomous_mode_with_empty_image_prompts(self, initial_state):
        """Test routing in autonomous mode with empty image prompts list."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = True
        state["final_image_prompts"] = []
        
        route = route_after_qa(state)
        assert route == "publicator"

    def test_routing_in_manual_mode(self, initial_state):
        """Test routing in manual mode always goes to validation."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["final_image_prompts"] = ["Python logo"]
        
        route = route_after_qa(state)
        assert route == "await_content_validation"

    def test_routing_in_manual_mode_without_images(self, initial_state):
        """Test routing in manual mode without images."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["final_image_prompts"] = None
        
        route = route_after_qa(state)
        assert route == "await_content_validation"


class TestRouteAfterImageGeneration:
    """Tests for route_after_image_generation function."""

    def test_routing_in_autonomous_mode(self, initial_state):
        """Test routing in autonomous mode goes to publicator."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = True
        state["generated_images"] = [{"image_name": "test.png"}]
        
        route = route_after_image_generation(state)
        assert route == "publicator"

    def test_routing_in_manual_mode_with_images(self, initial_state):
        """Test routing in manual mode with generated images."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["generated_images"] = [{"image_name": "test.png"}]
        
        route = route_after_image_generation(state)
        assert route == "await_image_validation"

    def test_routing_in_manual_mode_without_images(self, initial_state):
        """Test routing in manual mode without generated images."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["generated_images"] = None
        
        route = route_after_image_generation(state)
        assert route == "publicator"

    def test_routing_in_manual_mode_with_empty_images(self, initial_state):
        """Test routing in manual mode with empty images list."""
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["generated_images"] = []
        
        route = route_after_image_generation(state)
        assert route == "publicator"


class TestRouteAfterValidation:
    """Tests for route_after_validation function."""

    def test_routing_after_topic_approval(self, initial_state, mock_trends):
        """Test routing after approving topic selection."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "approve",
            "validated_step": "await_topic_selection"
        }
        state["selected_topic"] = mock_trends[0]
        
        route = route_after_validation(state)
        assert route == "tweet_searcher"

    def test_routing_after_content_approval_with_images(self, initial_state):
        """Test routing after approving content with image prompts."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "approve",
            "validated_step": "await_content_validation"
        }
        state["final_image_prompts"] = ["Python logo"]
        
        route = route_after_validation(state)
        assert route == "image_generator"

    def test_routing_after_content_approval_without_images(self, initial_state):
        """Test routing after approving content without image prompts."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "approve",
            "validated_step": "await_content_validation"
        }
        state["final_image_prompts"] = None
        
        route = route_after_validation(state)
        assert route == "publicator"

    def test_routing_after_image_approval(self, initial_state):
        """Test routing after approving images."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "approve",
            "validated_step": "await_image_validation"
        }
        
        route = route_after_validation(state)
        assert route == "publicator"

    def test_routing_after_content_rejection(self, initial_state):
        """Test routing after rejecting content."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "reject",
            "validated_step": "await_content_validation",
            "data": {"feedback": "Please improve"}
        }
        
        route = route_after_validation(state)
        assert route == "writer"

    def test_routing_after_image_rejection(self, initial_state):
        """Test routing after rejecting images."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "reject",
            "validated_step": "await_image_validation"
        }
        
        route = route_after_validation(state)
        assert route == "image_generator"

    def test_routing_after_content_edit(self, initial_state):
        """Test routing after editing content."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "edit",
            "validated_step": "await_content_validation",
            "data": {"extra_data": {"final_content": "Edited content"}}
        }
        state["final_image_prompts"] = ["Logo"]
        
        route = route_after_validation(state)
        assert route == "image_generator"

    def test_routing_with_unknown_validation_step(self, initial_state):
        """Test routing with unknown validation step defaults to END."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "approve",
            "validated_step": "unknown_step"
        }
        
        route = route_after_validation(state)
        assert route == "END"

    def test_routing_after_topic_edit(self, initial_state, mock_trends):
        """Test routing after editing topic selection."""
        state = initial_state.copy()
        state["validation_result"] = {
            "action": "edit",
            "validated_step": "await_topic_selection",
            "data": {"extra_data": {"selected_topic": mock_trends[1].model_dump()}}
        }
        state["selected_topic"] = mock_trends[1]
        
        route = route_after_validation(state)
        assert route == "tweet_searcher"

    def test_routing_with_no_validation_result(self, initial_state):
        """Test routing when validation_result is None."""
        state = initial_state.copy()
        state["validation_result"] = None
        
        route = route_after_validation(state)
        assert route == "END"

    def test_routing_with_empty_validation_result(self, initial_state):
        """Test routing with empty validation result dict."""
        state = initial_state.copy()
        state["validation_result"] = {}
        
        route = route_after_validation(state)
        # Default action is approve, but without validated_step it goes to END
        assert route == "END"

