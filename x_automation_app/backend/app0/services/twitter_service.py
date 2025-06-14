import requests
from ..config import settings

class TwitterService:
    """
    A service class to interact with the Twitter API.
    Handles authentication and provides methods for API actions.
    """
    def __init__(self):
        self.api_key = settings.X_API_KEY
        self.email = settings.USER_EMAIL
        self.password = settings.USER_PASSWORD
        self.proxy = settings.USER_PROXY
        self.base_url = "https://api.twitterapi.io/twitter"
        self.session_token = None

    def login_step_1(self):
        """
        Performs the first step of the 2FA login process.
        Returns the login_data required for the second step.
        """
        url = f"{self.base_url}/login_by_email_or_username"
        payload = {
            "username_or_email": self.email,
            "password": self.password,
            "proxy": self.proxy
        }
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if data.get("status") == "success" and "login_data" in data:
                return data["login_data"]
            else:
                # Handle cases where the API returns a success status but is missing data
                raise Exception(f"Login Step 1 failed: {data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            # Handle network errors
            raise Exception(f"Network error during Login Step 1: {e}")

    def login_step_2(self, login_data: str, two_fa_code: str):
        """
        Performs the second step of the 2FA login process.
        Saves the session token upon successful login.
        Returns the user session details.
        """
        url = f"{self.base_url}/login_by_2fa"
        payload = {
            "login_data": login_data,
            "2fa_code": two_fa_code,
            "proxy": self.proxy
        }
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success" and "session" in data:
                self.session_token = data["session"]
                return data
            else:
                raise Exception(f"Login Step 2 failed: {data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during Login Step 2: {e}")

    def get_trends(self):
        """
        Fetches trending topics for a given Where On Earth ID (WOEID) and count,
        based on settings in the config.
        """
        url = f"{self.base_url}/trends"
        params = {
            "woeid": settings.TRENDS_WOEID,
            "count": settings.TRENDS_COUNT
        }
        headers = {"X-API-Key": self.api_key}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("trends", [])
            else:
                raise Exception(f"Failed to get trends: {data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while fetching trends: {e}")

    def _upload_media(self, media_url: str):
        """
        Uploads media from a URL to Twitter and returns the media_id.
        This is a helper method for post_tweet.
        """
        # Download the media from the provided URL
        try:
            media_response = requests.get(media_url)
            media_response.raise_for_status()
            media_data = media_response.content
            content_type = media_response.headers.get('Content-Type', 'application/octet-stream')
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download media from URL: {e}")
        
        # Upload to Twitter
        url = f"{self.base_url}/upload_tweet_image"
        files = {'media': ('image', media_data, content_type)}
        headers = {"X-API-Key": self.api_key}
        payload = {"proxy": self.proxy}

        try:
            response = requests.post(url, files=files, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success" and "media_id" in data:
                return data["media_id"]
            else:
                raise Exception(f"Failed to upload media: {data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during media upload: {e}")

    def post_tweet(self, tweet_text: str, media_url: str = None):
        """
        Posts a tweet with optional media.
        Requires a valid session from a successful login.
        """
        if not self.session_token:
            raise Exception("Cannot post tweet: User is not logged in. Call login methods first.")

        media_id = None
        if media_url:
            media_id = self._upload_media(media_url)

        url = f"{self.base_url}/create_tweet"
        payload = {
            "auth_session": self.session_token,
            "tweet_text": tweet_text,
            "proxy": self.proxy
        }
        if media_id:
            payload["media_id"] = media_id
            
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success" and "data" in data:
                return data["data"]
            else:
                raise Exception(f"Failed to post tweet: {data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during tweet posting: {e}")

twitter_service = TwitterService() 