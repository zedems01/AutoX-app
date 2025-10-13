"""Tests for authentication endpoints."""
import pytest
from unittest.mock import Mock

class TestLogin:
    """Tests for /auth/login endpoint."""

    def test_login_with_valid_credentials(self, client, mocker, mock_x_api_response):
        """Test login with valid credentials."""
        mock_login = mocker.patch("backend.app.main.x_utils.login_v2")
        # mock_login = mocker.patch(".../")
        mock_login.return_value = {
            "session_cookie": mock_x_api_response["login_cookies"],
            "user_details": {"user_name": "testuser", "email": "test@example.com"}
        }

        payload = {
            "user_name": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "proxy": "http://proxy.example.com:8080",
            "totp_secret": "ABCD1234"
        }

        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "userDetails" in data
        assert "proxy" in data
        assert data["session"] == mock_x_api_response["login_cookies"]
        assert data["userDetails"]["user_name"] == "testuser"

    def test_login_with_invalid_credentials(self, client, mocker):
        """Test login with invalid credentials."""
        mock_login = mocker.patch("backend.app.main.x_utils.login_v2")
        mock_login.side_effect = Exception("Invalid credentials")

        payload = {
            "user_name": "wronguser",
            "email": "wrong@example.com",
            "password": "wrongpassword",
            "proxy": "http://proxy.example.com:8080",
            "totp_secret": "WRONG1234"
        }

        response = client.post("/auth/login", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]

    def test_login_calls_x_utils_with_correct_params(self, client, mocker):
        """Test that login calls x_utils.login_v2 with correct parameters."""
        mock_login = mocker.patch("backend.app.main.x_utils.login_v2")
        mock_login.return_value = {
            "session_cookie": "test_session",
            "user_details": {"user_name": "testuser", "email": "test@example.com"}
        }

        payload = {
            "user_name": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "proxy": "http://proxy.example.com:8080",
            "totp_secret": "ABCD1234"
        }

        client.post("/auth/login", json=payload)
        
        mock_login.assert_called_once_with(
            user_name="testuser",
            email="test@example.com",
            password="password123",
            proxy="http://proxy.example.com:8080",
            totp_secret="ABCD1234"
        )


class TestDemoLogin:
    """Tests for /auth/demo-login endpoint."""

    def test_demo_login_with_valid_token(self, client, mocker):
        """Test demo login with valid token."""
        mocker.patch("backend.app.main.settings.DEMO_TOKEN", "valid_demo_token")
        mocker.patch("backend.app.main.settings.TEST_USER_NAME", "demo_user")
        mocker.patch("backend.app.main.settings.TEST_USER_EMAIL", "demo@example.com")
        mocker.patch("backend.app.main.settings.TEST_USER_PASSWORD", "demo_password")
        mocker.patch("backend.app.main.settings.TEST_USER_PROXY", "http://proxy.example.com:8080")
        mocker.patch("backend.app.main.settings.TEST_USER_TOTP_SECRET", "DEMO1234")

        mock_login = mocker.patch("backend.app.main.x_utils.login_v2")
        mock_login.return_value = {
            "session_cookie": "demo_session_cookie",
            "user_details": {"user_name": "demo_user", "email": "demo@example.com"}
        }

        payload = {"token": "valid_demo_token"}
        response = client.post("/auth/demo-login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "session" in data
        assert "userDetails" in data
        assert data["session"] == "demo_session_cookie"

    def test_demo_login_with_invalid_token(self, client, mocker):
        """Test demo login with invalid token."""
        mocker.patch("backend.app.main.settings.DEMO_TOKEN", "valid_demo_token")

        payload = {"token": "invalid_token"}
        response = client.post("/auth/demo-login", json=payload)
        
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "Invalid token" in data["detail"]

    def test_demo_login_when_not_configured(self, client, mocker):
        """Test demo login when demo token is not configured."""
        mocker.patch("backend.app.main.settings.DEMO_TOKEN", None)

        payload = {"token": "any_token"}
        response = client.post("/auth/demo-login", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "not configured" in data["detail"].lower()

    def test_demo_login_when_credentials_incomplete(self, client, mocker):
        """Test demo login when demo credentials are incomplete."""
        mocker.patch("backend.app.main.settings.DEMO_TOKEN", "valid_demo_token")
        mocker.patch("backend.app.main.settings.TEST_USER_NAME", "demo_user")
        mocker.patch("backend.app.main.settings.TEST_USER_EMAIL", None)  # Missing email
        mocker.patch("backend.app.main.settings.TEST_USER_PASSWORD", "demo_password")
        mocker.patch("backend.app.main.settings.TEST_USER_PROXY", "http://proxy.example.com:8080")
        mocker.patch("backend.app.main.settings.TEST_USER_TOTP_SECRET", "DEMO1234")

        payload = {"token": "valid_demo_token"}
        response = client.post("/auth/demo-login", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "not configured" in data["detail"].lower()


class TestValidateSession:
    """Tests for /auth/validate-session endpoint."""

    def test_validate_session_with_valid_session(self, client, mocker):
        """Test session validation with valid session."""
        mock_verify = mocker.patch("backend.app.main.x_utils.verify_session")
        mock_verify.return_value = {"isValid": True}

        payload = {
            "session": "valid_session_cookie",
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/auth/validate-session", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["isValid"] is True

    def test_validate_session_with_invalid_session(self, client, mocker):
        """Test session validation with invalid session."""
        from ...app.utils.x_utils import InvalidSessionError
        
        mock_verify = mocker.patch("backend.app.main.x_utils.verify_session")
        mock_verify.side_effect = InvalidSessionError("Session expired")

        payload = {
            "session": "invalid_session_cookie",
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/auth/validate-session", json=payload)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Session expired" in data["detail"]

    def test_validate_session_handles_unexpected_error(self, client, mocker):
        """Test session validation handles unexpected errors."""
        mock_verify = mocker.patch("backend.app.main.x_utils.verify_session")
        mock_verify.side_effect = Exception("Unexpected error")

        payload = {
            "session": "some_session",
            "proxy": "http://proxy.example.com:8080"
        }

        response = client.post("/auth/validate-session", json=payload)
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "unexpected error" in data["detail"].lower()

