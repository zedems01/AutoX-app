from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .prompts import trend_harvester_prompt
from typing import Dict, Any, List
from agents.state import (
    OverallState,
    Trend
)
from ..services.twitter_service import get_trends
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


llm = ChatOpenAI(model="gpt-4o")

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
    logger.info("---Fetching Trending Topics---")

    agent = create_react_agent(
        model=llm,
        tools=[get_trends],
        response_format=List[Trend]
    )
    response = agent.invoke({"messages": [("user", trend_harvester_prompt)]})

    return {"trending_topics": response}