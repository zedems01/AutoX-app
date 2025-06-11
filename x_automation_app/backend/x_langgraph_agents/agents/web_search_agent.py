import logging
from langgraph.prebuilt import create_react_agent

from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt, get_state_items_as_list
from ..tools.get_web_news_tool import WebResponse, TAVILY_TOOL


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import time


llm = OPENAI_LLM
tavily_tool = TAVILY_TOOL

def web_search_agent(state: WorkflowState):
    """Agent that performs real-time web searches to gather contextual news and information related to the trending topics identified.
    """
    print("\n\n---------- Activating Web Agent ----------\n\n")
    time.sleep(10)
    
    # List of all the trends already scrapped
    # We will always just search news for the last ones
    trends_responses_list = get_state_items_as_list(state.get('trends_schema'))

    system_role=f"""
        You can search the web for latest news using provided tools.
    """

    agent = create_react_agent(
        model=llm,
        tools=[tavily_tool],
        prompt=make_system_prompt(system_role),
        response_format=WebResponse
    )

    logger.info("--- Searching on the web... ---")
    user_msg = f"""
        Search on the web for latest news about these specific trending subjects:
        {'\n'.join(['- '+t.trend_subject for t in trends_responses_list[-1].trends])}
        """
    response = agent.invoke({"messages": [("user", user_msg)]})

    return {
            "messages": response["messages"],
            "news_schema": response["structured_response"],
        }