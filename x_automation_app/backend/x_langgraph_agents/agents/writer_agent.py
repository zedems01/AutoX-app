import logging

from langgraph.prebuilt import create_react_agent

from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt
from ..tools.writer_tool import WriterResponse, get_tweets_tool


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



llm = OPENAI_LLM

def writer_agent(state: WorkflowState):
    """Agent for crafting the final tweet using insights from the Trends Analyst Agent and a curated set of user tweets related to the topic.
- ....
    """
    pass