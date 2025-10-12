"""Integration tests for workflow."""
import pytest
from unittest.mock import MagicMock
from backend.app.agents.graph import graph
from backend.app.agents.state import OverallState


@pytest.mark.integration
class TestWorkflowIntegration:
    """Integration tests for complete workflow."""

    def test_workflow_state_initialization(self, initial_state):
        """Test that workflow can be initialized with complete state."""
        thread_id = "test-integration-thread-001"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(config, initial_state)
        
        state = graph.get_state(config)
        
        assert state is not None
        assert state.values["is_autonomous_mode"] == initial_state["is_autonomous_mode"]
        assert state.values["output_destination"] == initial_state["output_destination"]
        assert state.values["current_step"] == initial_state["current_step"]

    def test_workflow_with_manual_mode_validation(self, initial_state, mock_trends):
        """Test workflow pauses at validation step in manual mode."""
        thread_id = "test-integration-thread-002"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Set up state for manual mode
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["trending_topics"] = mock_trends
        state["current_step"] = "trend_harvester"
        
        graph.update_state(config, state)
        
        # Get state to verify
        updated_state = graph.get_state(config)
        assert updated_state.values["is_autonomous_mode"] is False

    def test_workflow_state_persistence(self, initial_state):
        """Test that workflow state persists between updates."""
        thread_id = "test-integration-thread-003"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(config, initial_state)
        state1 = graph.get_state(config)
        
        update_data = {
            "current_step": "tweet_searcher",
            "user_provided_topic": "Python Testing"
        }
        graph.update_state(config, update_data)
        state2 = graph.get_state(config)
        
        # Verify persistence
        assert state2.values["current_step"] == "tweet_searcher"
        assert state2.values["user_provided_topic"] == "Python Testing"
        # Original data should still be there
        assert state2.values["is_autonomous_mode"] == initial_state["is_autonomous_mode"]

    def test_workflow_handles_topic_selection(self, initial_state, mock_trends):
        """Test workflow handles topic selection correctly."""
        thread_id = "test-integration-thread-004"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Set up with trending topics
        state = initial_state.copy()
        state["trending_topics"] = mock_trends
        state["current_step"] = "trend_harvester"
        
        graph.update_state(config, state)
        
        # Simulate topic selection
        selected_topic = mock_trends[0]
        topic_update = {
            "selected_topic": selected_topic,
            "current_step": "tweet_searcher"
        }
        graph.update_state(config, topic_update)
        
        updated_state = graph.get_state(config)
        assert updated_state.values["selected_topic"] is not None
        assert updated_state.values["selected_topic"].name == mock_trends[0].name

    def test_workflow_autonomous_mode_no_interrupts(self, initial_state):
        """Test workflow in autonomous mode doesn't set human input steps."""
        thread_id = "test-integration-thread-005"
        config = {"configurable": {"thread_id": thread_id}}
        
        state = initial_state.copy()
        state["is_autonomous_mode"] = True
        state["next_human_input_step"] = None
        
        graph.update_state(config, state)
        
        updated_state = graph.get_state(config)
        assert updated_state.values["is_autonomous_mode"] is True
        assert updated_state.values["next_human_input_step"] is None

    def test_workflow_validation_flow(self, initial_state, validation_approve):
        """Test workflow validation flow."""
        thread_id = "test-integration-thread-006"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Set up state awaiting validation
        state = initial_state.copy()
        state["is_autonomous_mode"] = False
        state["next_human_input_step"] = "await_content_validation"
        state["final_content"] = "Draft content"
        
        graph.update_state(config, state)
        
        # Submit validation
        validation_update = {
            "validation_result": validation_approve.model_dump(),
            "next_human_input_step": None
        }
        graph.update_state(config, validation_update)
        
        updated_state = graph.get_state(config)
        assert updated_state.values["validation_result"] is not None
        assert updated_state.values["next_human_input_step"] is None

    def test_workflow_handles_research_loop_tracking(self, initial_state):
        """Test workflow tracks research loop count."""
        thread_id = "test-integration-thread-007"
        config = {"configurable": {"thread_id": thread_id}}
        
        state = initial_state.copy()
        state["research_loop_count"] = 0
        state["max_research_loops"] = 3
        
        graph.update_state(config, state)
        
        # Simulate research loop increment
        graph.update_state(config, {"research_loop_count": 1})
        state1 = graph.get_state(config)
        assert state1.values["research_loop_count"] == 1
        
        graph.update_state(config, {"research_loop_count": 2})
        state2 = graph.get_state(config)
        assert state2.values["research_loop_count"] == 2

    def test_workflow_handles_multiple_threads(self, initial_state):
        """Test that multiple workflow threads can coexist."""
        thread_id_1 = "test-integration-thread-008-a"
        thread_id_2 = "test-integration-thread-008-b"
        config1 = {"configurable": {"thread_id": thread_id_1}}
        config2 = {"configurable": {"thread_id": thread_id_2}}
        
        # Create two different workflows
        state1 = initial_state.copy()
        state1["user_provided_topic"] = "Topic A"
        
        state2 = initial_state.copy()
        state2["user_provided_topic"] = "Topic B"
        
        graph.update_state(config1, state1)
        graph.update_state(config2, state2)
        
        # Verify they're independent
        retrieved_state1 = graph.get_state(config1)
        retrieved_state2 = graph.get_state(config2)
        
        assert retrieved_state1.values["user_provided_topic"] == "Topic A"
        assert retrieved_state2.values["user_provided_topic"] == "Topic B"

    def test_workflow_content_generation_flow(self, initial_state):
        """Test workflow content generation flow."""
        thread_id = "test-integration-thread-009"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(config, initial_state)
        
        # Simulate content generation stages
        graph.update_state(config, {
            "opinion_summary": "Public is excited",
            "overall_sentiment": "Positive",
            "current_step": "writer"
        })
        
        state1 = graph.get_state(config)
        assert state1.values["opinion_summary"] == "Public is excited"
        
        graph.update_state(config, {
            "content_draft": "Draft tweet content",
            "image_prompts": ["Logo"],
            "current_step": "quality_assurer"
        })
        
        state2 = graph.get_state(config)
        assert state2.values["content_draft"] == "Draft tweet content"
        assert len(state2.values["image_prompts"]) == 1

    def test_workflow_error_handling(self, initial_state):
        """Test workflow handles errors gracefully."""
        thread_id = "test-integration-thread-010"
        config = {"configurable": {"thread_id": thread_id}}
        
        state = initial_state.copy()
        state["error_message"] = "Test error occurred"
        state["current_step"] = "error"
        
        graph.update_state(config, state)
        
        retrieved_state = graph.get_state(config)
        assert retrieved_state.values["error_message"] == "Test error occurred"
        assert retrieved_state.values["current_step"] == "error"

    def test_workflow_state_updates_are_additive(self, initial_state):
        """Test that state updates add to existing state rather than replace."""
        thread_id = "test-integration-thread-011"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(config, initial_state)
        
        # Multiple incremental updates
        graph.update_state(config, {"current_step": "step1"})
        graph.update_state(config, {"user_provided_topic": "Topic"})
        graph.update_state(config, {"opinion_summary": "Summary"})
        
        final_state = graph.get_state(config)
        
        # All updates should be present
        assert final_state.values["current_step"] == "step1"
        assert final_state.values["user_provided_topic"] == "Topic"
        assert final_state.values["opinion_summary"] == "Summary"
        # Original values should still be there
        assert final_state.values["is_autonomous_mode"] == initial_state["is_autonomous_mode"]


@pytest.mark.integration
class TestWorkflowMemorySaver:
    """Tests for workflow memory/checkpointing."""

    def test_memory_saver_persists_state(self, initial_state):
        """Test that MemorySaver persists state correctly."""
        thread_id = "test-memory-thread-001"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(config, initial_state)
        
        # Retrieve state (simulating a new session)
        retrieved_state = graph.get_state(config)
        
        assert retrieved_state is not None
        assert retrieved_state.values["current_step"] == initial_state["current_step"]

    def test_memory_saver_handles_different_threads(self, initial_state):
        """Test that MemorySaver keeps different threads separate."""
        config1 = {"configurable": {"thread_id": "mem-thread-1"}}
        config2 = {"configurable": {"thread_id": "mem-thread-2"}}
        
        state1 = initial_state.copy()
        state1["current_step"] = "step_a"
        
        state2 = initial_state.copy()
        state2["current_step"] = "step_b"
        
        graph.update_state(config1, state1)
        graph.update_state(config2, state2)
        
        retrieved1 = graph.get_state(config1)
        retrieved2 = graph.get_state(config2)
        
        assert retrieved1.values["current_step"] == "step_a"
        assert retrieved2.values["current_step"] == "step_b"

    def test_memory_saver_state_updates_persist(self, initial_state):
        """Test that state updates persist across get operations."""
        thread_id = "test-memory-thread-003"
        config = {"configurable": {"thread_id": thread_id}}
        
        graph.update_state(config, initial_state)
        
        # Make multiple updates
        for i in range(5):
            graph.update_state(config, {"research_loop_count": i})
            state = graph.get_state(config)
            assert state.values["research_loop_count"] == i

