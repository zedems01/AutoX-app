import json
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..utils.prompts import tweet_search_prompt, get_current_date
from typing import Dict, Any
from .state import OverallState
from ..utils.x_utils import tweet_advanced_search
from ..utils.schemas import TweetSearched, TweetSearchResponse, TweetAuthor
from typing import List
from ..config import settings

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



try:
    llm = ChatOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        model=settings.OPENROUTER_MODEL
    )
except Exception as e:
    logger.error(f"Error initializing OpenRouter model, using Gemini model as fallback: {e}")
    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY
        )
    except Exception as e:
        logger.error(f"Error initializing Google Generative AI model, please check your credentials: {e}")

tweet_search_agent = create_react_agent(
    model=llm,
    tools=[tweet_advanced_search],
    response_format=TweetSearchResponse
)

def tweet_search_node(state: OverallState) -> Dict[str, List[TweetSearched]]:
    """
    Uses a ReAct agent to search for tweets based on the current topic and updates the state.

    This node determines the search topic from various possible keys in the state,
    invokes an agent to generate a search query, executes the search, and returns
    the results to be saved in the state.

    Returns:
        A dictionary to update the 'tweet_search_results' key in the state.
    """
    logger.info("TWEET SEARCH PROCESS")

#     parsed_response = [TweetSearched(text='Why would they have to ask? that’s weird. Israel said Donald Trump was involved in this operation from the beginning. I was told the only reason he was allowed to become president was to corral white kids into the army again and go to war with Iran.', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='Wed Nov 11 16:35:27 +0000 2020', lang='en', isReply=False, author=TweetAuthor(userName='kenpaichi', name='Dr. StormyWaters', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='Two days ago, the idea that Israel might pull us into a war with Iran was "hysterical," "unfounded," "paranoid," etc. \n\nNow, it\'s a stated policy preference.', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='Brandan P. Buck', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='@RealAlexJones don’t forget the sadistic nature of netanyahu. He’s the type of guy to flee israel, deliberately cut off defense systems and cause mass casualties to force America into a war with iran', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='Wed Nov 11 16:35:27 +0000 2020', lang='en', isReply=False, author=TweetAuthor(userName='', name='westsidephilosophy', isVerified=False, followers=0, following=0)),
#   TweetSearched(text="-FDD/Israel: Bomb Iran so it doesn't get a bomb!\n\n*Israel bombs but fails to destroy the nuclear program*\n\n-FDD/Israel: America must bomb Iran now because, after Israel tried, Iran really wants to get a bomb\n\nSo the plan was all along: Israel starts a war TO PULL THE US INTO IT", source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='Trita Parsi', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='🚨⚡️ Israel officially ‘ASKS’ US to ‘join’ war with Iran — Axios\n\nWill Trump agree or put ‘America first’? https://t.co/ooZuOA5bLp', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='RussiaNews 🇷🇺', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='Why would they have to ask? that’s weird. Israel said Donald Trump was involved in this operation from the beginning. I was told the only reason he was allowed to become president was to corral white kids into the army again and go to war with Iran.', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='Dr. StormyWaters', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='Two days ago, the idea that Israel might pull us into a war with Iran was "hysterical," "unfounded," "paranoid," etc. \n\nNow, it\'s a stated policy preference.', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='Brandan P. Buck', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='@RealAlexJones don’t forget the sadistic nature of netanyahu. He’s the type of guy to flee israel, deliberately cut off defense systems and cause mass casualties to force America into a war with iran', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='Wed Nov 11 16:35:27 +0000 2020', lang='en', isReply=False, author=TweetAuthor(userName='', name='westsidephilosophy', isVerified=False, followers=0, following=0)),
#   TweetSearched(text="-FDD/Israel: Bomb Iran so it doesn't get a bomb!\n\n*Israel bombs but fails to destroy the nuclear program*\n\n-FDD/Israel: America must bomb Iran now because, after Israel tried, Iran really wants to get a bomb\n\nSo the plan was all along: Israel starts a war TO PULL THE US INTO IT", source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='Trita Parsi', isVerified=False, followers=0, following=0)),
#   TweetSearched(text='🚨⚡️ Israel officially ‘ASKS’ US to ‘join’ war with Iran — Axios\n\nWill Trump agree or put ‘America first’? https://t.co/ooZuOA5bLp', source='Twitter for iPhone', retweetCount=0, replyCount=0, likeCount=0, quoteCount=0, viewCount=0, createdAt='', lang='en', isReply=False, author=TweetAuthor(userName='', name='RussiaNews 🇷🇺', isVerified=False, followers=0, following=0))]
    
#     logger.info(ctext(f"Successfully fetched {len(parsed_response)} tweets.\n", color='white'))

#     return {"tweet_search_results": parsed_response}


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
        
        logger.info(ctext(f"Successfully fetched {len(parsed_response.tweets)} tweets.\n", color='white'))

        return {"tweet_search_results": parsed_response.tweets}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the tweet search node: {e}\n")
        return {"error_message": f"An unexpected error occurred during tweet search: {str(e)}"}