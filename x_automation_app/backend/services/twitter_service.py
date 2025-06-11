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

twitter_service = TwitterService() 