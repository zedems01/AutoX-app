import logging

from langgraph.prebuilt import create_react_agent

from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt, get_state_items_as_list
from ..tools.writer_schema import WriterResponse
from ..tools.get_tweets_tool import get_tweets_tool


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import time


llm = OPENAI_LLM

def writer_agent(state: WorkflowState):
    """Agent for crafting the final tweet using insights from the Trends Analyst Agent and a curated set of user tweets related to the topic.
- ....
    """

    print("---------- Activating Writer Agent ----------")
    time.sleep(10)

    writer_responses_list = get_state_items_as_list(state.get('news_schema'))


    system_role = f"""
        You are a Twitter copywriting expert specialized in virality.
        You will be provided with information about different trending topics and the final choice of the user.
        Write a highly engaging tweet about the chosen topic, crafted to maximize interactions (likes, retweets, comments).
        Use a human, punchy, emotional tone, and if relevant, add a touch of humor or light controversy.
        Keep it short (under 280 characters), easy to read, with a strong hook in the first few words.
        Use hashtags to enhance engagement, but avoid excessive hashtags.
    """
        
    agent = create_react_agent(
        model=llm,
        tools=[],
        prompt=make_system_prompt(system_role),
        response_format=WriterResponse
    )

    user_msg = f"""

    """

    print(f"--- Writing the tweet... ---")
    response = agent.invoke({"messages": [("user", user_msg)]})

    return {
            "messages": response["messages"],
            "writer_schema": response["structured_response"],

        }
    pass