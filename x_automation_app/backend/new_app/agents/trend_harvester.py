from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .prompts import trend_harvester_prompt
from typing import Dict, Any, List
from .state import OverallState, Trend, TrendResponse
from ..services.twitter_service import get_trends
from ...config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the agent once and reuse it
llm = ChatOpenAI(model="gpt-4o")
trend_harvester_agent = create_react_agent(model=llm, tools=[get_trends], response_format=TrendResponse)

def trend_harvester_node(state: OverallState) -> Dict[str, Any]:
    """
    Fetches a curated list of trending topics using a ReAct agent.

    This node invokes an agent that uses the `get_trends` tool, reasons
    over the results to select a curated subset, and returns them in a
    structured format.
    """
    logger.info("---FETCHING AND CURATING TRENDING TOPICS---")
    
    try:
        # Format the prompt with values from the settings
        prompt = trend_harvester_prompt.format(
            woeid=settings.TRENDS_WOEID,
            count=settings.TRENDS_COUNT
        )
        response = trend_harvester_agent.invoke({"messages": [("user", prompt)]})
        parsed_response = response["structured_response"]
        logger.info(f"---Curated {len(parsed_response.trends)} trends successfully.---")
        return {"trending_topics": parsed_response.trends}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the trend harvester node: {e}")
        return {"error_message": f"An unexpected error occurred: {str(e)}"}