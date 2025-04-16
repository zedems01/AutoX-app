import logging
from langgraph.prebuilt import create_react_agent

from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt
from ..tools.get_web_news_tool import WebResponse, TAVILY_TOOL


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



llm = OPENAI_LLM
tavily_tool = TAVILY_TOOL

def web_search_agent(state: WorkflowState):
    """Agent that performs real-time web searches to gather contextual news and information related to the trending topics identified.
    """
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
        {'\n'.join(['- '+t.trend_subject for t in state.get('trends_schema').trends])}
        """
    response = agent.invoke({"messages": [("user", user_msg)]})

    return {
            "messages": response["messages"],
            "news_schema": response["structured_response"],
        }