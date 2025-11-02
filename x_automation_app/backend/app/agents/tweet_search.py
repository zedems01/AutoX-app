from langchain.chat_models import init_chat_model

from ..utils.prompts import tweet_search_prompt, get_current_date
from typing import Dict, Any
from .state import OverallState
from ..utils.x_utils import tweet_advanced_search
# from ..utils.schemas import TweetSearched, TweetSearchResponse, TweetAuthor, TweetQuery
from ..utils.schemas import TweetSearched, TweetQuery
from typing import List
from ..config import settings

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



def tweet_search_node(state: OverallState) -> Dict[str, List[TweetSearched]]:
    """
    Uses a ReAct agent to search for tweets based on the current topic and updates the state.

    This node determines the search topic from various possible keys in the state,
    invokes an agent to generate a search query, executes the search, and returns
    the results to be saved in the state.

    Returns:
        A dictionary to update the 'tweet_search_results' key in the state.
    """

    try:
        llm = f"google_genai:{settings.GEMINI_MODEL}"
        model = init_chat_model(llm, api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing OpenRouter model, using Gemini model as fallback: {e}")
        try:
            llm = f"openai:{settings.OPENAI_MODEL}"
            model = init_chat_model(llm)
        except Exception as e:
            logger.error(f"Error initializing Google Generative AI model, please check your credentials: {e}")


    logger.info("TWEET SEARCH PROCESS")


    try:
        topic = ""
        selected_topic = state.get("selected_topic")
        if selected_topic:
            topic = selected_topic["name"] if isinstance(selected_topic, dict) else selected_topic.name
        elif state.get("user_provided_topic"):
            topic = state.get("user_provided_topic")

        if not topic:
            raise ValueError("No topic found in the state to initiate tweet search.")

        logger.info(ctext(f"Searching for tweets about: {topic}\n", color='white'))

        structured_llm = model.with_structured_output(TweetQuery)


        user_config = state.get("user_config") or {}
        tweets_language = (user_config.tweets_language if user_config and user_config.tweets_language is not None 
            else settings.TWEETS_LANGUAGE
        )

        prompt = tweet_search_prompt.format(
                topic=topic,
                current_date=get_current_date(),
                tweets_language=tweets_language
            )    

        tweets = []
        while len(tweets) < 15:
            response = structured_llm.invoke(prompt)
            query = response.query
            logger.info(ctext(f"Generated query: {query}\n", color='white'))
            tweets = tweet_advanced_search(query)
            tweets.extend(tweets)
        
        logger.info(ctext(f"Successfully fetched {len(tweets)} tweets.\n", color='white'))

        return {"tweet_search_results": tweets}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the tweet search node: {e}\n")
        return {"error_message": f"An unexpected error occurred during tweet search: {str(e)}"}

