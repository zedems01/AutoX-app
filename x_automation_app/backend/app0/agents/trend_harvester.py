from typing import Dict, Any, List
from agents.state import (
    OverallState,
    Trend
)
from ..services.twitter_service import twitter_service

def trend_harvester_node(state: OverallState) -> Dict[str, Any]:
    """
    Fetches trending topics from the Twitter service and updates the state.

    This node calls the `twitter_service.get_trends` method, processes the
    raw trend data into the structured `Trend` format, and adds it to the
    `trending_topics` list in the application's state.

    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary with the `trending_topics` key to update the state.
    """
    print("---Fetching Trending Topics---")
    try:
        raw_trends = twitter_service.get_trends()
        
        processed_trends: List[Trend] = []
        for trend in raw_trends:
            # The API returns a 'target' object with a 'query'.
            # We can construct a search URL from this query.
            # The query is often URI-encoded, so it's ready for a URL.
            query = trend.get("target", {}).get("query", "")
            
            processed_trends.append({
                "name": trend.get("name", "Unknown Trend"),
                "url": f"https://twitter.com/search?q={query}",
                "tweet_count": trend.get("tweet_count") # This might be None
            })

        print(f"Found {len(processed_trends)} trends.")
        return {"trending_topics": processed_trends}

    except Exception as e:
        print(f"Error fetching trends: {e}")
        return {"error_message": f"Failed to fetch trends: {e}"}
