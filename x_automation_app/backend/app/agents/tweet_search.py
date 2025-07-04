import json
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from ..utils.prompts import tweet_search_prompt, get_current_date
from typing import Dict, Any
from .state import OverallState
from ..utils.x_utils import tweet_advanced_search
from ..utils.schemas import TweetSearched, TweetSearchResponse, TweetAuthor
from typing import List
from ..config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


try:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL)
except Exception as e:
    logger.error(f"Error initializing OpenAI model: {e}")
    try:
        llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, google_api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing Google Generative AI model: {e}")
        llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)

tweet_search_agent = create_react_agent(model=llm, tools=[tweet_advanced_search], response_format=TweetSearchResponse)

def tweet_search_node(state: OverallState) -> Dict[str, List[TweetSearched]]:
    """
    Uses a ReAct agent to search for tweets based on the current topic and updates the state.

    This node determines the search topic from various possible keys in the state,
    invokes an agent to generate a search query, executes the search, and returns
    the results to be saved in the state.

    Returns:
        A dictionary to update the 'tweet_search_results' key in the state.
    """
    logger.info("----SEARCHING FOR TWEETS----\n")
    
    try:
        topic = ""
        selected_topic = state.get("selected_topic")
        if selected_topic:
            topic = selected_topic["name"] if isinstance(selected_topic, dict) else selected_topic.name
        elif state.get("user_provided_topic"):
            topic = state.get("user_provided_topic")

        if not topic:
            raise ValueError("No topic found in the state to initiate tweet search.")

        logger.info(f"----Searching tweets for topic: {topic}----")

        user_config = state.get("user_config") or {}
        tweets_language = (user_config.tweets_language if user_config and user_config.tweets_language is not None 
            else settings.TWEETS_LANGUAGE
        )
        
        if tweets_language:
            prompt = tweet_search_prompt.format(
                topic=topic,
                current_date=get_current_date(),
                tweets_language=tweets_language
            )        
        response = tweet_search_agent.invoke({"messages": [("user", prompt)]})
        parsed_response = response["structured_response"]
        
        logger.info(f"----Found {len(parsed_response.tweets)} tweets.----\n")

        return {"tweet_search_results": parsed_response.tweets}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the tweet search node: {e}\n")
        return {"error_message": f"An unexpected error occurred during tweet search: {str(e)}"}