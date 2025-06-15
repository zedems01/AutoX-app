import json
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .prompts import trend_harvester_prompt
from typing import Dict, Any, List
from .state import OverallState, Trend
from ..services.twitter_service import get_trends
from ...config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the agent once and reuse it
llm = ChatOpenAI(model="gpt-4o")
trend_harvester_agent = create_react_agent(model=llm, tools=[get_trends])

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
        
        # Invoke the agent
        response = trend_harvester_agent.invoke({"messages": [("user", prompt)]})
        
        # Extract the last message content
        last_message = response['messages'][-1]
        raw_content = last_message.content
        
        # Clean and parse the JSON response
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-4].strip()
        
        parsed_trends = json.loads(raw_content)
        
        # Validate and structure the trends using the Pydantic model
        trending_topics = [Trend.model_validate(t) for t in parsed_trends]
        
        logger.info(f"---Curated {len(trending_topics)} trends successfully.---")
        
        return {"trending_topics": trending_topics}

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from agent response: {e}\nRaw content: {raw_content}")
        return {"error_message": "Failed to parse trends from the agent."}
    except Exception as e:
        logger.error(f"An unexpected error occurred in the trend harvester node: {e}")
        return {"error_message": f"An unexpected error occurred: {str(e)}"}