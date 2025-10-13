"""Tests for workflow endpoints."""
import pytest
import uuid
from unittest.mock import MagicMock


class TestStartWorkflow:
    """Tests for /workflow/start endpoint."""

    def test_start_workflow_with_valid_payload(self, client, mocker, mock_user_details, mock_user_config):
        """Test starting workflow with valid payload."""
        mock_update = mocker.patch("backend.app.main.graph.update_state")
        
        payload = {
            "is_autonomous_mode": False,
            "output_destination": "DOWNLOAD",
            "has_user_provided_topic": False,
            "user_provided_topic": None,
            "x_content_type": "TWEET",
            "content_length": "SHORT",
            "brand_voice": "professional",
            "target_audience": "developers",
            "user_config": mock_user_config.model_dump(),
            "session": "test_session",
            "user_details": mock_user_details.model_dump(),
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/workflow/start", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert "initial_state" in data
        assert data["initial_state"]["is_autonomous_mode"] is False
        assert data["initial_state"]["output_destination"] == "DOWNLOAD"

    def test_start_workflow_creates_unique_thread_id(self, client, mocker, mock_user_details, mock_user_config):
        """Test that each workflow gets a unique thread_id."""
        mocker.patch("backend.app.main.graph.update_state")
        
        payload = {
            "is_autonomous_mode": True,
            "output_destination": "PUBLISH_X",
            "has_user_provided_topic": False,
            "user_provided_topic": None,
            "x_content_type": "THREAD",
            "content_length": "MEDIUM",
            "brand_voice": "casual",
            "target_audience": "general",
            "user_config": mock_user_config.model_dump(),
            "session": "test_session",
            "user_details": mock_user_details.model_dump(),
            "proxy": "http://proxy.example.com:8080"
        }

        # Make two requests
        response1 = client.post("/workflow/start", json=payload)
        response2 = client.post("/workflow/start", json=payload)
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Thread IDs should be different
        assert data1["thread_id"] != data2["thread_id"]
        
        # Both should be valid UUIDs
        uuid.UUID(data1["thread_id"])
        uuid.UUID(data2["thread_id"])

    def test_start_workflow_initializes_state_correctly(self, client, mocker, mock_user_details, mock_user_config):
        """Test that workflow initializes state with correct default values."""
        mock_update = mocker.patch("backend.app.main.graph.update_state")
        
        payload = {
            "is_autonomous_mode": False,
            "output_destination": "DOWNLOAD",
            "has_user_provided_topic": True,
            "user_provided_topic": "Python Programming",
            "x_content_type": "TWEET",
            "content_length": "SHORT",
            "brand_voice": "technical",
            "target_audience": "developers",
            "user_config": mock_user_config.model_dump(),
            "session": "test_session",
            "user_details": mock_user_details.model_dump(),
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/workflow/start", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that state was initialized with correct values
        initial_state = data["initial_state"]
        assert initial_state["current_step"] == "workflow_started"
        assert initial_state["messages"] == []
        assert initial_state["trending_topics"] is None
        assert initial_state["selected_topic"] is None
        assert initial_state["validation_result"] is None
        assert initial_state["research_loop_count"] == 0
        assert initial_state["max_research_loops"] == 3

    def test_start_workflow_with_user_provided_topic(self, client, mocker, mock_user_details, mock_user_config):
        """Test workflow start with user-provided topic."""
        mocker.patch("backend.app.main.graph.update_state")
        
        payload = {
            "is_autonomous_mode": False,
            "output_destination": "DOWNLOAD",
            "has_user_provided_topic": True,
            "user_provided_topic": "Machine Learning Trends",
            "x_content_type": "TWEET",
            "content_length": "MEDIUM",
            "brand_voice": "educational",
            "target_audience": "students",
            "user_config": mock_user_config.model_dump(),
            "session": "test_session",
            "user_details": mock_user_details.model_dump(),
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/workflow/start", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["initial_state"]["has_user_provided_topic"] is True
        assert data["initial_state"]["user_provided_topic"] == "Machine Learning Trends"

    def test_start_workflow_handles_error(self, client, mocker, mock_user_details, mock_user_config):
        """Test workflow start handles errors gracefully."""
        mock_update = mocker.patch("backend.app.main.graph.update_state")
        mock_update.side_effect = Exception("Graph update failed")
        
        payload = {
            "is_autonomous_mode": False,
            "output_destination": "DOWNLOAD",
            "has_user_provided_topic": False,
            "user_provided_topic": None,
            "x_content_type": "TWEET",
            "content_length": "SHORT",
            "brand_voice": "professional",
            "target_audience": "developers",
            "user_config": mock_user_config.model_dump(),
            "session": "test_session",
            "user_details": mock_user_details.model_dump(),
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/workflow/start", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Graph update failed" in data["detail"]


class TestValidateStep:
    """Tests for /workflow/validate endpoint."""

    def test_validate_topic_selection_approve(self, client, mocker, mock_trends):
        """Test validation of topic selection with approve action."""
        # Create mock state with next_human_input_step set
        mock_state = MagicMock()
        mock_state.values = {
            "next_human_input_step": "await_topic_selection",
            "trending_topics": [t.model_dump() for t in mock_trends]
        }
        
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        # mock_get_state.return_value = mock_state
        
        mock_update = mocker.patch("backend.app.main.graph.update_state")
        
        # Mock the updated state after validation
        updated_mock_state = MagicMock()
        updated_mock_state.values = {
            "next_human_input_step": None,
            "selected_topic": mock_trends[0].model_dump(),
            "validation_result": {
                "action": "approve",
                "validated_step": "await_topic_selection",
                "data": {"extra_data": {"selected_topic": mock_trends[0].model_dump()}}
            }
        }
        # mock_get_state.return_value = updated_mock_state  # Remove this
        mock_get_state.side_effect = [mock_state, updated_mock_state]  # Add this
        
        payload = {
            "thread_id": "test-thread-123",
            "validation_result": {
                "action": "approve",
                "data": {
                    "extra_data": {
                        "selected_topic": mock_trends[0].model_dump()
                    }
                }
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 200
        assert mock_update.called

    def test_validate_content_approval(self, client, mocker):
        """Test validation of content with approve action."""
        mock_state = MagicMock()
        mock_state.values = {
            "next_human_input_step": "await_content_validation",
            "final_content": "Draft content",
            "final_image_prompts": ["prompt 1"]
        }
        
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        mock_get_state.return_value = mock_state
        
        mock_update = mocker.patch("backend.app.main.graph.update_state")

        payload = {
            "thread_id": "test-thread-456",
            "validation_result": {
                "action": "approve",
                "data": None
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 200

    def test_validate_content_with_edits(self, client, mocker):
        """Test validation with edits to content."""
        mock_state = MagicMock()
        mock_state.values = {
            "next_human_input_step": "await_content_validation",
            "final_content": "Draft content",
            "final_image_prompts": ["prompt 1"]
        }
        
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        mock_get_state.return_value = mock_state
        
        mock_update = mocker.patch("backend.app.main.graph.update_state")

        new_content = "Edited content that is better"
        payload = {
            "thread_id": "test-thread-789",
            "validation_result": {
                "action": "edit",
                "data": {
                    "extra_data": {
                        "final_content": new_content
                    }
                }
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 200
        
        # Check that update was called with edited content
        call_args = mock_update.call_args
        assert call_args is not None

    def test_validate_rejection_with_feedback(self, client, mocker):
        """Test validation with rejection and feedback."""
        mock_state = MagicMock()
        mock_state.values = {
            "next_human_input_step": "await_content_validation",
            "final_content": "Draft content"
        }
        
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        mock_get_state.return_value = mock_state
        
        mock_update = mocker.patch("backend.app.main.graph.update_state")

        payload = {
            "thread_id": "test-thread-reject",
            "validation_result": {
                "action": "reject",
                "data": {
                    "feedback": "Please make it more engaging"
                }
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 200

    def test_validate_when_thread_not_found(self, client, mocker):
        """Test validation when thread doesn't exist."""
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        mock_get_state.return_value = None

        payload = {
            "thread_id": "non-existent-thread",
            "validation_result": {
                "action": "approve",
                "data": None
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_validate_when_no_human_input_awaited(self, client, mocker):
        """Test validation when no human input is awaited."""
        mock_state = MagicMock()
        mock_state.values = {
            "next_human_input_step": None,  # No human input awaited
        }
        
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        mock_get_state.return_value = mock_state

        payload = {
            "thread_id": "test-thread-no-hitl",
            "validation_result": {
                "action": "approve",
                "data": None
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "no human input" in data["detail"].lower()

    def test_validate_handles_exception(self, client, mocker):
        """Test validation endpoint handles exceptions."""
        mock_get_state = mocker.patch("backend.app.main.graph.get_state")
        mock_get_state.side_effect = Exception("Database error")

        payload = {
            "thread_id": "test-thread-error",
            "validation_result": {
                "action": "approve",
                "data": None
            }
        }

        response = client.post("/workflow/validate", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

