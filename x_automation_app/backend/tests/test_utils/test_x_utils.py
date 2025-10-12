"""Tests for X API utility functions."""
import pytest
from unittest.mock import Mock, mock_open
from backend.app.utils.x_utils import (
    login_v2, verify_session, get_char_count,
    upload_image_v2, post_tweet_v2, InvalidSessionError
)


class TestLoginV2:
    """Tests for login_v2 function."""

    def test_login_with_valid_credentials(self, mocker):
        """Test successful login with valid credentials."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login_cookies": "session_cookie_12345",
            "message": "Login successful"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        result = login_v2(
            user_name="testuser",
            email="test@example.com",
            password="password123",
            proxy="http://proxy.example.com:8080",
            totp_secret="ABCD1234"
        )

        assert result["session_cookie"] == "session_cookie_12345"
        assert result["user_details"]["user_name"] == "testuser"
        assert result["user_details"]["email"] == "test@example.com"

    def test_login_with_invalid_credentials(self, mocker):
        """Test login fails with invalid credentials."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login_cookies": "",
            "message": "Invalid credentials"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            login_v2(
                user_name="wronguser",
                email="wrong@example.com",
                password="wrongpass",
                proxy="http://proxy.example.com:8080",
                totp_secret="WRONG1234"
            )
        
        assert "Login failed" in str(excinfo.value)

    def test_login_network_error(self, mocker):
        """Test login handles network errors."""
        import requests
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        with pytest.raises(Exception) as excinfo:
            login_v2(
                user_name="testuser",
                email="test@example.com",
                password="password123",
                proxy="http://proxy.example.com:8080",
                totp_secret="ABCD1234"
            )
        
        assert "Network error during Login" in str(excinfo.value)


class TestVerifySession:
    """Tests for verify_session function."""

    def test_verify_valid_session(self, mocker):
        """Test verification of valid session."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        result = verify_session(
            login_cookies="valid_session_cookie",
            proxy="http://proxy.example.com:8080"
        )

        assert result["isValid"] is True

    def test_verify_invalid_session_raises_error(self, mocker):
        """Test verification raises InvalidSessionError for invalid session."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"status": "error", "message": "Invalid session"}
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        with pytest.raises(InvalidSessionError) as excinfo:
            verify_session(
                login_cookies="invalid_session_cookie",
                proxy="http://proxy.example.com:8080"
            )
        
        assert "Session is invalid" in str(excinfo.value)

    def test_verify_session_network_error(self, mocker):
        """Test verify_session handles network errors."""
        import requests
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(InvalidSessionError) as excinfo:
            verify_session(
                login_cookies="session_cookie",
                proxy="http://proxy.example.com:8080"
            )
        
        assert "Network error" in str(excinfo.value)


class TestGetCharCount:
    """Tests for get_char_count function."""

    def test_char_count_normal_text(self):
        """Test character count for normal text."""
        text = "Hello, this is a test tweet."
        count = get_char_count.invoke(text)
        assert count == len(text)

    def test_char_count_with_emojis(self):
        """Test character count with emojis (count as 2)."""
        text = "Hello 👋 World 🌍"
        # "Hello " (6) + 👋 (2) + " World " (7) + 🌍 (2) = 17
        count = get_char_count.invoke(text)
        assert count == 17

    def test_char_count_with_urls(self):
        """Test character count with URLs (count as 23)."""
        text = "Check this out https://example.com/path"
        # "Check this out " (15) + URL (23) = 38
        count = get_char_count.invoke(text)
        assert count == 38

    def test_char_count_with_multiple_urls(self):
        """Test character count with multiple URLs."""
        text = "Visit https://example.com and https://test.com"
        # "Visit " (6) + " and " (5) + 2 URLs (23 * 2) = 57
        count = get_char_count.invoke(text)
        assert count == 57

    def test_char_count_complex_text(self):
        """Test character count with mixed content."""
        text = "Great article 📚 https://example.com 👍"
        # "Great article " (14) + 📚 (2) + " " (1) + URL (23) + " " (1) + 👍 (2) = 43
        count = get_char_count.invoke(text)
        assert count == 43

    def test_char_count_empty_string(self):
        """Test character count for empty string."""
        text = ""
        count = get_char_count.invoke(text)
        assert count == 0


class TestUploadImageV2:
    """Tests for upload_image_v2 function."""

    def test_upload_image_success(self, mocker):
        """Test successful image upload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "media_id": "media_12345"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response
        
        # Mock file opening
        mock_file = mocker.patch("builtins.open", mock_open(read_data=b"fake image data"))

        result = upload_image_v2(
            login_cookies="session_cookie",
            image_path="/path/to/image.png",
            proxy="http://proxy.example.com:8080"
        )

        assert result == "media_12345"

    def test_upload_image_without_login(self, mocker):
        """Test upload fails when not logged in."""
        with pytest.raises(Exception) as excinfo:
            upload_image_v2(
                login_cookies="",
                image_path="/path/to/image.png",
                proxy="http://proxy.example.com:8080"
            )
        
        assert "not logged in" in str(excinfo.value)

    def test_upload_image_api_failure(self, mocker):
        """Test upload handles API failure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "error",
            "msg": "Upload failed"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response
        
        mock_file = mocker.patch("builtins.open", mock_open(read_data=b"fake image data"))

        with pytest.raises(Exception) as excinfo:
            upload_image_v2(
                login_cookies="session_cookie",
                image_path="/path/to/image.png",
                proxy="http://proxy.example.com:8080"
            )
        
        assert "Failed to upload media" in str(excinfo.value)


class TestPostTweetV2:
    """Tests for post_tweet_v2 function."""

    def test_post_tweet_text_only(self, mocker):
        """Test posting tweet with text only."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "tweet_id": "tweet_12345"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        result = post_tweet_v2(
            login_cookies="session_cookie",
            tweet_text="This is a test tweet",
            proxy="http://proxy.example.com:8080"
        )

        assert result == "tweet_12345"

    def test_post_tweet_with_images(self, mocker):
        """Test posting tweet with images."""
        # Mock upload_image_v2
        mock_upload = mocker.patch("backend.app.utils.x_utils.upload_image_v2")
        mock_upload.side_effect = ["media_1", "media_2"]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "tweet_id": "tweet_67890"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        result = post_tweet_v2(
            login_cookies="session_cookie",
            tweet_text="Tweet with images",
            proxy="http://proxy.example.com:8080",
            image_paths=["/path/to/image1.png", "/path/to/image2.png"]
        )

        assert result == "tweet_67890"
        assert mock_upload.call_count == 2

    def test_post_tweet_without_login(self, mocker):
        """Test posting fails when not logged in."""
        with pytest.raises(Exception) as excinfo:
            post_tweet_v2(
                login_cookies="",
                tweet_text="Test tweet",
                proxy="http://proxy.example.com:8080"
            )
        
        assert "not logged in" in str(excinfo.value)

    def test_post_tweet_api_failure(self, mocker):
        """Test posting handles API failure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "error",
            "msg": "Tweet posting failed"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            post_tweet_v2(
                login_cookies="session_cookie",
                tweet_text="Test tweet",
                proxy="http://proxy.example.com:8080"
            )
        
        assert "Failed to post tweet" in str(excinfo.value)

    def test_post_tweet_with_reply_to(self, mocker):
        """Test posting tweet as reply."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "tweet_id": "reply_12345"
        }
        
        mock_post = mocker.patch("backend.app.utils.x_utils.requests.post")
        mock_post.return_value = mock_response

        result = post_tweet_v2(
            login_cookies="session_cookie",
            tweet_text="This is a reply",
            proxy="http://proxy.example.com:8080",
            reply_to_tweet_id="original_tweet_123"
        )

        assert result == "reply_12345"

