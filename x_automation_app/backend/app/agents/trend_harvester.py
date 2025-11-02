from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from ..utils.prompts import trend_harvester_prompt
from typing import Dict, List
from .state import OverallState
from ..utils.schemas import Trend, TrendResponse
from ..utils.x_utils import get_trends
from ..config import settings

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



def trend_harvester_node(state: OverallState) -> Dict[str, List[Trend]]:
    """
    Fetches a curated list of trending topics using a ReAct agent.

    This node invokes an agent that uses the `get_trends` tool, reasons
    over the results to select a curated subset, and returns them in a
    structured format.
    """

    try:
        llm = f"google_genai:{settings.GEMINI_RESEARCH_MODEL}"
        model = init_chat_model(llm, api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing OpenRouter model, using Gemini model as fallback: {e}")
        try:
            llm = f"openai:{settings.OPENAI_MODEL}"
            model = init_chat_model(llm)
        except Exception as e:
            logger.error(f"Error initializing Google Generative AI model, please check your credentials: {e}")

    trend_harvester_agent = create_agent(
        model=model,
        tools=[get_trends],
        response_format=TrendResponse
    )


    logger.info("FETCHING AND CURATING TRENDING TOPICS...")

    
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

        msg1 = f"Successfully curated {len(parsed_response.trends)} trends from woeid: {woeid}\n"
        msg2 = f"Top trends: {ctext(", ".join([f'{trend.name} ({trend.tweet_count})' for trend in parsed_response.trends[:10]]), italic=True)}\n"
        logger.info(ctext(msg1 + msg2, color='white'))

        return {"trending_topics": parsed_response.trends}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the trend harvester node: {e}\n")
        return {"error_message": f"An unexpected error occurred: {str(e)}"}
