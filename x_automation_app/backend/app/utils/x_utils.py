# TODO:
# - refine the logic of the 'tweet_advanced_search' tool to give more autonomy to the agent 


import requests
from ..config import settings
from .schemas import Trend, TweetSearched, TweetAuthor
from typing import List, Optional
from langchain_core.tools import tool
import re
import unicodedata
import csv
import json
from io import StringIO

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()


class InvalidSessionError(Exception):
    """Custom exception for invalid session."""
    pass


def login_v2(
        user_name: str,
        email: str,
        password: str,
        proxy: str,
        totp_secret: str,
        api_key: str = settings.X_API_KEY
    ) -> dict:
    """
    Performs the login process using the v2 API.
    Returns the user session details.
    """
    url = "https://api.twitterapi.io/twitter/user_login_v2"
    payload = {
        "user_name": user_name,
        "email": email,
        "password": password,
        "totp_secret": totp_secret,
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
        if "login_cookies" in data and data["login_cookies"] != "":
            return {
                "session_cookie": data["login_cookies"],
                "user_details": {"user_name": user_name, "email": email}
            }
        else:
            raise Exception(f"Login failed: {data.get('message', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during Login: {e}")


@tool
def get_trends(
        woeid: int,
        count: Optional[int]=30,
        api_key: str = settings.X_API_KEY
    ) -> List[Trend]:
    """
    Fetches trending topics for a given Where On Earth ID (WOEID) and count (the number of trends to fetch),
    based on settings in the config.

    Args:
    ---
        woeid: The Where On Earth ID (WOEID) of the location to fetch trends for.
        count: The number of trends to fetch.
        api_key: The API key to use for the request.
        
    Returns:
    ---
        List[Trend]: A list of trending topics.
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
                tweet_count = trend_details.get("meta_description", "")
                processed_trends.append(Trend(name=name, rank=rank, tweet_count=tweet_count))
            return processed_trends
        else:
            raise Exception(f"Failed to get trends: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error while fetching trends: {e}")

@tool
def tweet_advanced_search(
        query: str,
        query_type: str = "Latest",
        api_key: str = settings.X_API_KEY
    ) -> List[TweetSearched]:
    """
    Performs an advanced search for tweets based on the provided query and query type.

    Args:
    ---
        query: The query to search for.
        query_type: The type of query to search for.
        api_key: The API key to use for the request.

    Returns:
    ---
        List[TweetSearched]: A list of tweets.
    """
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    all_tweets: List[TweetSearched] = []
    current_cursor = ""
    max_tweets_to_retrieve = int(settings.MAX_TWEETS_TO_RETRIEVE)
    # print(f"MAX_TWEETS_TO_RETRIEVE: {max_tweets_to_retrieve}; Type: {type(max_tweets_to_retrieve)}")
    while len(all_tweets) < max_tweets_to_retrieve:
        params = {"query": query, "query_type": query_type, "cursor": current_cursor}
        headers = {"X-API-Key": api_key}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            for tweet_data in data.get("tweets", []):
                author_data = tweet_data.get("author", {})
                author = TweetAuthor(
                    userName=author_data.get("userName", ""),
                    name=author_data.get("name", ""),
                    isVerified=author_data.get("isVerified", False),
                    followers=author_data.get("followers", 0),
                    following=author_data.get("following", 0)
                )

                tweet_obj = TweetSearched(
                    text=tweet_data.get("text", ""),
                    source=tweet_data.get("source", ""),
                    retweetCount=tweet_data.get("retweetCount", 0),
                    replyCount=tweet_data.get("replyCount", 0),
                    likeCount=tweet_data.get("likeCount", 0),
                    quoteCount=tweet_data.get("quoteCount", 0),
                    viewCount=tweet_data.get("viewCount", 0),
                    createdAt=tweet_data.get("createdAt", ""),
                    lang=tweet_data.get("lang", ""),
                    isReply=tweet_data.get("isReply", False),
                    author=author
                )
                all_tweets.append(tweet_obj)
            logger.info(ctext(f"Fetched {len(all_tweets)} tweets so far...", color='white'))

            if len(all_tweets) >= max_tweets_to_retrieve:
                logger.info(ctext(f"Max tweets reached: {max_tweets_to_retrieve}, exiting loop.", color='white'))
                break

            has_next_page = data.get("has_next_page", False)
            next_cursor = data.get("next_cursor", "")

            if not has_next_page or not next_cursor:
                break
            current_cursor = next_cursor
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network or API error during tweet advanced search: {e}")

    return all_tweets



def verify_session(login_cookies: str, proxy: str, api_key: str = settings.X_API_KEY) -> dict:
    """
    Verifies if a session is valid by performing a low-cost action (liking a tweet).
    Raises InvalidSessionError if the session is not valid.
    """

    try:
        like_url = "https://api.twitterapi.io/twitter/like_tweet_v2"
        like_payload = {
            "login_cookies": login_cookies,
            "tweet_id": "1967212782207844463",
            "proxy": proxy
        }
        like_headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(like_url, json=like_payload, headers=like_headers)
        like_data = response.json()

        if response.status_code >= 400:
            raise InvalidSessionError("Session is invalid or expired.")
        elif like_data.get("status") == "success":
            return {"isValid": True}
        else:
            raise InvalidSessionError("Session is invalid or expired, unable to verify session.")

    except requests.exceptions.RequestException as e:
        raise InvalidSessionError(f"Network error during session validation: {e}")



def upload_image_v2(
        login_cookies: str,
        image_path: str,
        proxy: str,
        api_key: str = settings.X_API_KEY
    ) -> str:
    """
    Uploads media from a URL to Twitter and returns the media_id.
    """

    if not login_cookies:
        raise Exception("Cannot upload image: User is not logged in. Call login methods first.")

    url = "https://api.twitterapi.io/twitter/upload_media_v2"

    with open(image_path, 'rb') as file:
        files = {'file': file}
        payload = {
            "proxy": proxy,
            "login_cookies": login_cookies,
            "is_long_video": "false"
        }
        headers = {"X-API-Key": api_key}

        try:
            response = requests.post(url, data=payload, files=files, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success" and "media_id" in data:
                return data["media_id"]
            else:
                raise Exception(f"Failed to upload media: {data.get('msg', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during media upload: {e}")

@tool
def get_char_count(text: str) -> int:
    """
    Calculates the character count of a string for Twitter, where emojis count as 2 characters
    and URLs count as 23 characters.
    """
    url_regex = r"https?://[^\s]+"
    urls = re.findall(url_regex, text)
    
    # Replace URLs with a placeholder to not count their length
    text_no_urls = re.sub(url_regex, "", text)
    
    emoji_count = 0
    char_count = 0

    for char in text_no_urls:
        # Check if the character is an emoji
        if unicodedata.category(char) in ('So', 'Sc'):
            emoji_count += 1
        else:
            char_count += 1
    
    # Emojis count as 2, normal chars as 1, and each URL as 23
    return char_count + (emoji_count * 2) + (len(urls) * 23)

def post_tweet_v2(
        login_cookies: str,
        tweet_text: str,
        proxy: str,
        image_paths: Optional[List[str]]=None,
        reply_to_tweet_id: Optional[str]=None,
        api_key: str = settings.X_API_KEY
    ):
    """
    Posts a tweet with optional media and returns the tweet ID.
    Requires a valid session from a successful login.
    """
    if not login_cookies:
        raise Exception("Cannot post tweet: User is not logged in. Call login methods first.")

    media_ids = None
    if image_paths:
        media_ids = [upload_image_v2(login_cookies, image_path, proxy, api_key) for image_path in image_paths]

    url = "https://api.twitterapi.io/twitter/create_tweet_v2"

    payload = {
        "login_cookies": login_cookies,
        "tweet_text": tweet_text,
        "proxy": proxy
    }

    if media_ids:
        payload["media_ids"] = media_ids
    if reply_to_tweet_id:
        payload["reply_to_tweet_id"] = reply_to_tweet_id

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            tweet_id = data.get("tweet_id")
            
            if tweet_id:
                return tweet_id
            else:
                raise Exception("Tweet ID not found in a successful API response.")
        else:
            raise Exception(f"Failed to post tweet: {data.get('msg', 'Unknown error')}")

    except requests.exceptions.JSONDecodeError:
        raise Exception("Failed to decode API response as JSON.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during tweet posting: {e}") from e


def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary by combining keys with a separator.
    """
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def data_to_csv(data, delimiter='|'):
    """
    Convert a list of objects to a CSV string, handling nested dictionaries.
    """
    if isinstance(data, str):
        data = json.loads(data)

    if not isinstance(data, list) or not data:
        raise ValueError("The data must be a non-empty list")

    flattened_data = [flatten_dict(item) for item in data]
    headers = list(flattened_data[0].keys())

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator='\n', delimiter=delimiter)

    writer.writeheader()

    for item in flattened_data:
        writer.writerow(item)

    csv_content = output.getvalue()
    output.close()

    return csv_content
