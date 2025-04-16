from dotenv import load_dotenv
load_dotenv()
import logging

from langgraph.prebuilt import create_react_agent
from ..tools.get_trends_tool import TrendsResponse, get_trending_topics
from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


llm = OPENAI_LLM

def web_scraping_agent(state: WorkflowState):
    """Agent that extracts trending topics on X based on a specified location (city, country, or worldwide).
    """
    system_role=f"""
        You can get trending topics using provided tools.
    """

    agent = create_react_agent(
        model=llm,
        tools=[get_trending_topics],
        prompt=make_system_prompt(system_role),
        response_format=TrendsResponse
    )
    logger.info("--- Scraping Twitter trends... ---")
    response = agent.invoke(state)

    return {
            "messages": response["messages"],
            "trends_schema": response["structured_response"],
        }