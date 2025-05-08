from dotenv import load_dotenv
load_dotenv()
import logging

from langgraph.prebuilt import create_react_agent
from ..tools.get_trends_tool import TrendsResponse, get_trending_topics
from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import time

llm = OPENAI_LLM

def complete_auto_node(state: WorkflowState):
    print("\n---------- Activating USER PREFERENCE AUTOMATION ----------\n")
    time.sleep(10)

    ans = input(f"Do you want a complete automation???")
    if ans=='yes':
        auto=True
    else:
        auto=False
    return {
        "complete_automation": auto
    }

def web_scraping_agent(state: WorkflowState):
    """Agent that extracts trending topics on X based on a specified location (city, country, or worldwide).
    """
    print("\n---------- Activating Scraping Agent ----------\n\n")
    time.sleep(10)

    input_prompt = state.get('next_scraping_prompt') # Check for specific prompt first
    if input_prompt:
        logger.info("--- Fetching others trending topics for the user... ---")
        # Optionally clear the prompt after use if it's meant for one specific re-run
    else:
        logger.info("--- Using last message for scraping... ---")
        # Fallback to the last message in the state (assuming it's the human input)
        if state.get('messages'):
            input_prompt = state.get('messages')[-1].content # Adjust if message format is different
        else:
            # Handle case with no initial messages if necessary
            logger.error("Web scraping agent called with no initial message and no next_scraping_prompt.")
            raise ValueError("Web scraping agent called with no initial message.")

    if not input_prompt:
        logger.error("Web scraping agent: Input prompt is empty.")
        raise ValueError("Web scraping agent: Input prompt is empty.")




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
    response = agent.invoke({"messages": [("user", input_prompt)]})
    logger.info("--- Scraping Ended... ---")


    return {
            "messages": response["messages"],
            "trends_schema": response["structured_response"],
        }