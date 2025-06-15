import requests

def post_tweet(api_key, url, payload, in_reply_to_tweet_id=None):
    if in_reply_to_tweet_id:
        payload["in_reply_to_tweet_id"] = in_reply_to_tweet_id
    
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success" and "tweet_id" in data:
            return data["tweet_id"]
        else:
            raise Exception(f"Failed to post tweet: {data.get('msg', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error while posting tweet: {e}") 