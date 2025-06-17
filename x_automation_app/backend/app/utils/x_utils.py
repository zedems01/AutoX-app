import requests
from ..config import settings
from .schemas import Trend, TweetSearched, TweetAuthor
from typing import List, Optional
from langchain_core.tools import tool
import logging
import re
import unicodedata

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InvalidSessionError(Exception):
    """Custom exception for invalid session."""
    pass


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
        if "login_data" in data and data["login_data"] != "":
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
        if "session" in data and data["session"] != "":
            return {
                "session": data["session"],
                "user_details": data["user"]
            }
        else:
            raise Exception(f"Login Step 2 failed: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during Login Step 2: {e}")


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

    while len(all_tweets) < settings.MAX_TWEETS_TO_RETRIEVE:
        params = {"query": query, "query_type": query_type, "cursor": current_cursor}
        headers = {"X-API-Key": api_key}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()

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
            logger.info(f"Tweets fetched!! Found {len(all_tweets)} tweets so far...")

            if len(all_tweets) >= settings.MAX_TWEETS_TO_RETRIEVE:
                logger.info(f"Total tweets reached max limit {settings.MAX_TWEETS_TO_RETRIEVE}, exiting loop.")
                break

            has_next_page = data.get("has_next_page", False)
            next_cursor = data.get("next_cursor", "")

            if not has_next_page or not next_cursor:
                break # No more pages, exit loop
            current_cursor = next_cursor
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network or API error during tweet advanced search: {e}")

    return all_tweets



def verify_session(session: str, proxy: str, api_key: str = settings.X_API_KEY) -> dict:
    """
    Verifies if a session is valid by performing a low-cost action (liking a tweet).
    Raises InvalidSessionError if the session is not valid.
    """
    # 1. Get a tweet to like
    try:
        search_url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
        search_params = {"query": "Real Madrid min_faves:500", "query_type": "Latest"}
        search_headers = {"X-API-Key": api_key}
        
        response = requests.get(search_url, params=search_params, headers=search_headers)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get("tweets"):
            raise Exception("Could not fetch a tweet to test the like action.")
            
        tweet_id = search_data["tweets"][0].get("id")
        if not tweet_id:
            raise Exception("Could not find an ID for the fetched tweet.")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch a tweet for session validation: {e}")

    # 2. Try to like the tweet
    try:
        like_url = "https://api.twitterapi.io/twitter/like_tweet"
        like_payload = {
            "auth_session": session,
            "tweet_id": tweet_id,
            "proxy": proxy
        }
        like_headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(like_url, json=like_payload, headers=like_headers)
        like_data = response.json()

        # The twitterapi.io does not always return a clear status,
        # so we check if the response indicates a failure.
        # A common failure message for invalid sessions is related to authentication.
        if response.status_code >= 400 or "auth" in like_data.get("msg", "").lower():
            raise InvalidSessionError("Session is invalid or expired.")

        # If the call succeeds, we assume the session is valid.
        # The API might return success even if the tweet is already liked.
        return {"isValid": True}

    except requests.exceptions.RequestException as e:
        # Network errors are not necessarily session errors, but we treat them as failures here.
        raise InvalidSessionError(f"Network error during session validation: {e}")


# Helper functions
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

def chunk_text(text: str, max_length: int = 270) -> list[str]:
    """
    Chunks a long text into a list of smaller strings, each within the max_length,
    respecting word boundaries and Twitter's character counting rules.
    """
    if get_char_count(text) <= max_length:
        return [text]

    chunks = []
    words = text.split(' ')
    current_chunk = ""

    for word in words:
        # Check if adding the next word exceeds the max length
        if get_char_count(current_chunk + " " + word) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    # Add numbering (e.g., 1/n)
    num_chunks = len(chunks)
    if num_chunks > 1:
        for i, chunk in enumerate(chunks):
            prefix = f"({i+1}/{num_chunks}) "
            # Check if the prefix can be added without exceeding the limit
            if get_char_count(prefix + chunk) <= max_length:
                chunks[i] = prefix + chunk
            else:
                # This part needs a more robust implementation if chunks are already near the limit.
                # For now, we prepend and might slightly exceed, assuming initial chunking left some space.
                # A better way would be to account for the prefix length during initial chunking.
                chunks[i] = prefix + chunk 

    return chunks 

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
    
def post_tweet_thread(
        session: str,
        tweet_text: str,
        proxy: str,
        image_url: Optional[str]=None,
        api_key: str = settings.X_API_KEY
    ) -> List[dict]:
    """
    Publishes a thread of tweets.
    
    Args:
        session (str): The authenticated user session.
        tweet_texts (List[str]): A list of tweet content strings. The first is the main tweet.
        proxy (str): The proxy to use for the requests.
        image_url (Optional[str]): The URL of the image to attach to the first tweet.
        api_key (str): The API key.

    Returns:
        List[dict]: A list of dictionaries containing the response from the API for each posted tweet.
    """
    if not session:
        raise Exception("Cannot post tweet thread: User is not logged in.")

    chunks = chunk_text(tweet_text)
    posted_tweets = []
    reply_to_id = None

    for i, chunk in enumerate(chunks):
        # For now, we are not handling multiple images in threads.
        # If there is an image, it will be added to the first tweet.
        # This can be extended to use media_ids_per_tweet.
        tweet_id = post_tweet(
            session=session,
            tweet_text=chunk,
            proxy=proxy,
            image_url=image_url if i == 0 else None,
            in_reply_to_tweet_id=reply_to_id,
            api_key=api_key
        )
        
        if tweet_id:
            posted_tweets.append({"status": "success", "tweet_id": tweet_id})
            reply_to_id = tweet_id  # The next tweet will reply to this one
        else:
            # If a tweet fails, we stop and report the failure.
            posted_tweets.append({"status": "error", "message": f"Failed to post chunk {i+1}"})
            break
            
    return posted_tweets


