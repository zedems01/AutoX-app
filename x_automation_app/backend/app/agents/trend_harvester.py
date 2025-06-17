from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from ..utils.prompts import trend_harvester_prompt
from typing import Dict, Any, List
from .state import OverallState
from ..utils.schemas import Trend, TrendResponse
from ..utils.x_utils import get_trends
from ..config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the agent once and reuse it
# llm = ChatOpenAI(model=settings.OPENAI_MODEL) or ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL)
llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL)
trend_harvester_agent = create_react_agent(model=llm, tools=[get_trends], response_format=TrendResponse)

def trend_harvester_node(state: OverallState) -> Dict[str, List[Trend]]:
    """
    Fetches a curated list of trending topics using a ReAct agent.

    This node invokes an agent that uses the `get_trends` tool, reasons
    over the results to select a curated subset, and returns them in a
    structured format.
    """
    logger.info("---FETCHING AND CURATING TRENDING TOPICS---\n")
    
    try:
        # Format the prompt with values from the settings
        # print(f"type state: {state}\n\n")
        safe_user_config = state.get("user_config") or {}
        prompt = trend_harvester_prompt.format(
            woeid = safe_user_config.get("trends_woeid") or settings.TRENDS_WOEID,
            count = safe_user_config.get("trends_count") or settings.TRENDS_COUNT
        )
        response = trend_harvester_agent.invoke({"messages": [("user", prompt)]})
        parsed_response = response["structured_response"]
        logger.info(f"---Curated {len(parsed_response.trends)} trends successfully.---\n")
        return {"trending_topics": parsed_response.trends}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the trend harvester node: {e}\n")
        return {"error_message": f"An unexpected error occurred: {str(e)}"}