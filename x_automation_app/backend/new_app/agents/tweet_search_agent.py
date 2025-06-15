import json
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .prompts import tweet_search_prompt, get_current_date
from typing import Dict, Any
from .state import OverallState
from ..services.twitter_service import tweet_advanced_search
from .tools_and_schemas import TweetSearched, TweetSearchResponse
from typing import List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the agent once and reuse it
llm = ChatOpenAI(model="gpt-4o")
tweet_search_agent = create_react_agent(model=llm, tools=[tweet_advanced_search], response_format=TweetSearchResponse)

def tweet_search_node(state: OverallState) -> Dict[str, Any]:
    """
    Uses a ReAct agent to search for tweets based on the current topic and updates the state.

    This node determines the search topic from various possible keys in the state,
    invokes an agent to generate a search query, executes the search, and returns
    the results to be saved in the state.

    Returns:
        A dictionary to update the 'tweet_search_results' key in the state.
    """
    logger.info("---SEARCHING FOR TWEETS---")
    
    try:
        # Determine the topic from the state, with a clear priority
        topic = ""
        selected_topic = state.get("selected_topic")
        if selected_topic:
            topic = selected_topic.name
        elif state.get("user_provided_topic"):
            topic = state.get("user_provided_topic")

        if not topic:
            raise ValueError("No topic found in the state to initiate tweet search.")

        logger.info(f"---Searching tweets for topic: {topic}---")
        
        prompt = tweet_search_prompt.format(
            topic=topic,
            current_date=get_current_date()
        )
        
        response = tweet_search_agent.invoke({"messages": [("user", prompt)]})
        
        # The result of the tool call is usually in the last message content
        tool_output = response['messages'][-1].content
        
        # The tool returns a list of TweetSearched objects, but via the agent it may be a string
        # We'll assume the tool's direct output is what we need. If it's a string, it needs parsing.
        try:
            # If the tool output is a JSON string in the message content
            tweet_search_results = json.loads(tool_output)
        except (json.JSONDecodeError, TypeError):
            # If the output is already a list of objects (ideal case)
            tweet_search_results = tool_output

        logger.info(f"---Found {len(tweet_search_results)} tweets.---")

        return {"tweet_search_results": tweet_search_results}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the tweet search node: {e}")
        return {"error_message": f"An unexpected error occurred during tweet search: {str(e)}"}