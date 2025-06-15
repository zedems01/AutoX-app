import requests
from ..config import settings
from ..agents.tools_and_schemas import Trend, TweetSearched, TweetAuthor
from typing import List, Optional



def start_login(
        email: str,
        password: str,
        proxy: str,
        api_key: str = settings.X_API_KEY
    ) -> str:
    """
    Performs the first step of the 2FA login process.
    Returns the login_data required for the second step.
    """
    url = "https://api.twitterapi.io/twitter/login_by_email_or_username"
    payload = {
        "username_or_email": email,
        "password": password,
        "proxy": proxy
    }
    headers = {
        "X-API-Key": api_key,
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
    


def complete_login(
        login_data: str,
        two_fa_code: str,
        proxy: str,
        api_key: str = settings.X_API_KEY
    ) -> dict:
    """
    Performs the second step of the 2FA login process.
    Saves the session token upon successful login.
    Returns the user session details.
    """
    url = "https://api.twitterapi.io/twitter/login_by_2fa"
    payload = {
        "login_data": login_data,
        "2fa_code": two_fa_code,
        "proxy": proxy
    }
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        output = {}
        if data.get("status") == "success" and "session" in data:
            output["session"] = data["session"]
            output["user"] = data["user"]
            return output
        else:
            raise Exception(f"Login Step 2 failed: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during Login Step 2: {e}")


def get_trends(
        woeid: int,
        count: int,
        api_key: str = settings.X_API_KEY
    ) -> List[Trend]:
    """
    Fetches trending topics for a given Where On Earth ID (WOEID) and count,
    based on settings in the config.
    """
    url = "https://api.twitterapi.io/twitter/trends"
    params = {"woeid": woeid, "count": count}
    headers = {"X-API-Key": api_key}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        processed_trends: List[Trend] = []

        if data.get("status") == "success":
            for trend in data.get("trends", []):
                trend_details = trend.get("trend", {})
                name = trend_details.get("name", "Unknown Trend")
                rank = trend_details.get("rank", 0)
                tweet_count = trend_details.get("tweet_count", "")
                processed_trends.append(Trend(name=name, rank=rank, tweet_count=tweet_count))
            return processed_trends
        else:
            raise Exception(f"Failed to get trends: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error while fetching trends: {e}")


def tweet_advanced_search(
        query: str,
        query_type: str = "Latest",
        cursor: str = "",
        num_requests: int = 7,
        api_key: str = settings.X_API_KEY
    ) -> List[TweetSearched]:
    """
    Performs an advanced search for tweets based on the provided query and query type.
    Collects tweets over multiple pages up to num_requests.
    """
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    all_tweets: List[TweetSearched] = []
    current_cursor = cursor
    requests_made = 0

    while requests_made < num_requests:
        params = {"query": query, "query_type": query_type, "cursor": current_cursor}
        headers = {"X-API-Key": api_key}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # Directly process the data, assuming success if raise_for_status() passed
            for tweet_data in data.get("tweets", []):
                # Extract author details
                author_data = tweet_data.get("author", {})
                author = TweetAuthor(
                    userName=author_data.get("user_name", ""),
                    name=author_data.get("name", ""),
                    isVerified=author_data.get("is_verified", False),
                    followers=author_data.get("followers_count", 0),
                    following=author_data.get("following_count", 0)
                )

                # Extract tweet details
                tweet_obj = TweetSearched(
                    text=tweet_data.get("text", ""),
                    source=tweet_data.get("source", ""),
                    retweetCount=tweet_data.get("retweet_count", 0),
                    replyCount=tweet_data.get("reply_count", 0),
                    likeCount=tweet_data.get("like_count", 0),
                    quoteCount=tweet_data.get("quote_count", 0),
                    viewCount=tweet_data.get("views", 0),
                    createdAt=tweet_data.get("created_at", ""),
                    lang=tweet_data.get("lang", ""),
                    isReply=tweet_data.get("is_reply", False),
                    author=author
                )
                all_tweets.append(tweet_obj)

            has_next_page = data.get("has_next_page", False)
            next_cursor = data.get("next_cursor", "")

            if not has_next_page or not next_cursor:
                break # No more pages, exit loop
            current_cursor = next_cursor
            
        except requests.exceptions.RequestException as e:
            # Handle network errors or HTTP errors caught by raise_for_status()
            raise Exception(f"Network or API error during tweet advanced search: {e}")
        
        requests_made += 1

    return all_tweets


def upload_image(
        session: str, image_url: str, proxy: str, api_key: str = settings.X_API_KEY
    ) -> str:
    """
    Uploads media from a URL to Twitter and returns the media_id.
    This is a helper method for post_tweet.
    """

    if not session:
        raise Exception("Cannot upload image: User is not logged in. Call login methods first.")

    url = "https://api.twitterapi.io/twitter/upload_image"
    payload = {"auth_session": session, "image_url": image_url, "proxy": proxy}
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success" and "media_id" in data:
            return data["media_id"]
        else:
            raise Exception(f"Failed to upload media: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during media upload: {e}")
    

def post_tweet(
        session: str,
        tweet_text: str,
        proxy: str,
        image_url: Optional[str]=None,
        in_reply_to_tweet_id: Optional[str]=None,
        api_key: str = settings.X_API_KEY
    ):
    """
    Posts a tweet with optional media and returns the tweet ID.
    Requires a valid session from a successful login.
    """
    if not session:
        raise Exception("Cannot post tweet: User is not logged in. Call login methods first.")

    media_id = None
    if image_url:
        media_id = upload_image(session, image_url, proxy, api_key)

    url = "https://api.twitterapi.io/twitter/create_tweet"

    payload = {
        "auth_session": session,
        "tweet_text": tweet_text,
        "proxy": proxy
    }

    if media_id:
        payload["media_id"] = media_id
    if in_reply_to_tweet_id:
        payload["in_reply_to_tweet_id"] = in_reply_to_tweet_id

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success" and "data" in data:
            # Attempt to extract the tweet ID
            tweet_id = data.get("data", {}).get("create_tweet", {}).get("tweet_result", {}).get("result", {}).get("rest_id")
            if tweet_id:
                return tweet_id
            else:
                # Raise an error if tweet ID is not found, even if status is success
                raise Exception("Tweet ID not found in API response.")
        else:
            raise Exception(f"Failed to post tweet: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during tweet posting: {e}")
    # response format:
    # {
    #   "status": "<string>",
    #   "msg": "<string>",
    #   "data": {
    #     "create_tweet": {
    #       "tweet_result": {
    #         "result": {
    #           "rest_id": "<string>" # The ID of the tweet
    #         }
    #       }
    #     }
    #   }
    # } 


    #TODO: Complete with the logic defined in the plan
    return {}




# class TwitterService:
#     """
#     A service class to interact with the Twitter API.
#     Handles authentication and provides methods for API actions.
#     """
#     def __init__(self):
#         self.api_key = settings.X_API_KEY
#         self.email = settings.USER_EMAIL
#         self.password = settings.USER_PASSWORD
#         self.proxy = settings.USER_PROXY
#         self.base_url = "https://api.twitterapi.io/twitter"
#         self.session_token = None

#     def login_step_1(self):
#         """
#         Performs the first step of the 2FA login process.
#         Returns the login_data required for the second step.
#         """
#         url = f"{self.base_url}/login_by_email_or_username"
#         payload = {
#             "username_or_email": self.email,
#             "password": self.password,
#             "proxy": self.proxy
#         }
#         headers = {
#             "X-API-Key": self.api_key,
#             "Content-Type": "application/json"
#         }
#         try:
#             response = requests.post(url, json=payload, headers=headers)
#             response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
#             data = response.json()
#             if data.get("status") == "success" and "login_data" in data:
#                 return data["login_data"]
#             else:
#                 # Handle cases where the API returns a success status but is missing data
#                 raise Exception(f"Login Step 1 failed: {data.get('msg', 'Unknown error')}")
#         except requests.exceptions.RequestException as e:
#             # Handle network errors
#             raise Exception(f"Network error during Login Step 1: {e}")

#     def login_step_2(self, login_data: str, two_fa_code: str):
#         """
#         Performs the second step of the 2FA login process.
#         Saves the session token upon successful login.
#         Returns the user session details.
#         """
#         url = f"{self.base_url}/login_by_2fa"
#         payload = {
#             "login_data": login_data,
#             "2fa_code": two_fa_code,
#             "proxy": self.proxy
#         }
#         headers = {
#             "X-API-Key": self.api_key,
#             "Content-Type": "application/json"
#         }
#         try:
#             response = requests.post(url, json=payload, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             output = {}
#             if data.get("status") == "success" and "session" in data:
#                 self.session_token = data["session"]
#                 output["session"] = data["session"]
#                 output["user"] = data["user"]
#                 return output
#             else:
#                 raise Exception(f"Login Step 2 failed: {data.get('msg', 'Unknown error')}")
#         except requests.exceptions.RequestException as e:
#             raise Exception(f"Network error during Login Step 2: {e}")

#     def get_trends(self):
#         """
#         Fetches trending topics for a given Where On Earth ID (WOEID) and count,
#         based on settings in the config.
#         """
#         url = f"{self.base_url}/trends"
#         params = {
#             "woeid": settings.TRENDS_WOEID,
#             "count": settings.TRENDS_COUNT
#         }
#         headers = {"X-API-Key": self.api_key}
#         try:
#             response = requests.get(url, params=params, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             processed_trends: List[Trend] = []

#             if data.get("status") == "success":
#                 for trend in data.get("trends", []):
#                     trend_details = trend.get("trend", {})
#                     name = trend_details.get("name", "Unknown Trend")
#                     rank = trend_details.get("rank", 0)
#                     tweet_count = trend_details.get("tweet_count", "")
#                     processed_trends.append(Trend(name=name, rank=rank, tweet_count=tweet_count))
#                 return processed_trends
#             else:
#                 raise Exception(f"Failed to get trends: {data.get('msg', 'Unknown error')}")
#         except requests.exceptions.RequestException as e:
#             raise Exception(f"Network error while fetching trends: {e}")

#     def tweet_advanced_search(self, query: str, query_type: str = "Latest", cursor: str = ""):
#         """
#         Performs an advanced search for tweets based on the provided query and query type.
#         """
#         url = f"{self.base_url}/tweet/advanced_search"
#         params = {"query": query, "query_type": query_type, "cursor": cursor}
#         headers = {"X-API-Key": self.api_key}

#         response = requests.get(url, params=params, headers=headers)
#         response.raise_for_status()
#         data = response.json()
    
#     def _upload_media(self, media_url: str):
#         """
#         Uploads media from a URL to Twitter and returns the media_id.
#         This is a helper method for post_tweet.
#         """
#         # Download the media from the provided URL
#         # try:
#         #     media_response = requests.get(media_url)
#         #     media_response.raise_for_status()
#         #     media_data = media_response.content
#         #     content_type = media_response.headers.get('Content-Type', 'application/octet-stream')
#         # except requests.exceptions.RequestException as e:
#         #     raise Exception(f"Failed to download media from URL: {e}")
        
#         # Upload to Twitter
#         url = f"{self.base_url}/upload_image"
#         files = {'media': ('image', media_data, content_type)}
#         headers = {"X-API-Key": self.api_key}
#         payload = {"proxy": self.proxy}

#         try:
#             response = requests.post(url, files=files, data=payload, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             if data.get("status") == "success" and "media_id" in data:
#                 return data["media_id"]
#             else:
#                 raise Exception(f"Failed to upload media: {data.get('msg', 'Unknown error')}")
#         except requests.exceptions.RequestException as e:
#             raise Exception(f"Network error during media upload: {e}")

#     def post_tweet(self, tweet_text: str, media_url: str = None):
#         """
#         Posts a tweet with optional media.
#         Requires a valid session from a successful login.
#         """
#         if not self.session_token:
#             raise Exception("Cannot post tweet: User is not logged in. Call login methods first.")

#         media_id = None
#         if media_url:
#             media_id = self._upload_media(media_url)

#         url = f"{self.base_url}/create_tweet"
#         payload = {
#             "auth_session": self.session_token,
#             "tweet_text": tweet_text,
#             "proxy": self.proxy
#         }
#         if media_id:
#             payload["media_id"] = media_id
            
#         headers = {
#             "X-API-Key": self.api_key,
#             "Content-Type": "application/json"
#         }

#         try:
#             response = requests.post(url, json=payload, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             if data.get("status") == "success" and "data" in data:
#                 return data["data"]
#             else:
#                 raise Exception(f"Failed to post tweet: {data.get('msg', 'Unknown error')}")
#         except requests.exceptions.RequestException as e:
#             raise Exception(f"Network error during tweet posting: {e}")

# twitter_service = TwitterService() 