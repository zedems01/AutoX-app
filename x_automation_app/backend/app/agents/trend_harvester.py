from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from ..utils.prompts import trend_harvester_prompt
from typing import Dict, Any, List
from .state import OverallState
from ..utils.schemas import Trend, TrendResponse
from ..utils.x_utils import get_trends
from ..config import settings

# import logging
from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()


try:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL)
except Exception as e:
    logger.error(f"Error initializing OpenAI model: {e}")
    try:
        llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, google_api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing Google Generative AI model: {e}")
        llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)

# llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)
trend_harvester_agent = create_react_agent(model=llm, tools=[get_trends], response_format=TrendResponse)

def trend_harvester_node(state: OverallState) -> Dict[str, List[Trend]]:
    """
    Fetches a curated list of trending topics using a ReAct agent.

    This node invokes an agent that uses the `get_trends` tool, reasons
    over the results to select a curated subset, and returns them in a
    structured format.
    """
    logger.info("FETCHING AND CURATING TRENDING TOPICS")
    parsed_response = [{"name":"Messi","rank":2,"tweet_count":"268K posts"},{"name":"Porto","rank":5,"tweet_count":"102K posts"},{"name":"#ONEPIECE1152","rank":19,"tweet_count":"13.4K posts"},{"name":"Schengen","rank":30,"tweet_count":"1,534 posts"}]
    logger.info(ctext(f'Curated {len(parsed_response)} trends successfully from woeid:{2000000}\n', color='white'))
    return {"trending_topics": parsed_response}
    
    try:
        safe_user_config = state.get("user_config") or {}
        woeid = (safe_user_config.trends_woeid if safe_user_config and safe_user_config.trends_woeid is not None 
                else settings.TRENDS_WOEID
            )
        count = (safe_user_config.trends_count if safe_user_config and safe_user_config.trends_count is not None 
                else settings.TRENDS_COUNT
            )

        prompt = trend_harvester_prompt.format(
            woeid = woeid,
            count = count
        )
        response = trend_harvester_agent.invoke({"messages": [("user", prompt)]})
        parsed_response = response["structured_response"]
        logger.info(ctext(f'Successfully curated {len(parsed_response.trends)} trends from woeid:{woeid}\n', color='white'))

        return {"trending_topics": parsed_response.trends}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the trend harvester node: {e}\n")
        return {"error_message": f"An unexpected error occurred: {str(e)}"}