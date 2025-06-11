import logging

from langgraph.prebuilt import create_react_agent

from ..tools.utils import WorkflowState, OPENAI_LLM, ANTHROPIC_LLM, make_system_prompt, get_state_items_as_list
from ..tools.analyst_schema import TrendsAnalysisResponse


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import time


llm = OPENAI_LLM

def trends_analyst_agent(state: WorkflowState):
    """Agent that evaluates the trending topics and recommends the one most likely to generate high engagement if tweeted.
    """
    print("\n\n---------- Activating Trends Analyst Agent ----------\n\n")
    time.sleep(10)

    # Same here, we just analyze the last inputs, not the previous ones
    news_responses_list = get_state_items_as_list(state.get('news_schema'))

    system_role = f"""
        You are a social media and trend analysis expert, specialized in maximizing engagement on Twitter. I will provide you with a list of current trending topics on Twitter, along with information about related news for each topic. Your task is to recommend **the topic most likely to generate maximum interactions** (likes, retweets, comments) if I tweet about it, and explain why this choice is optimal.

        **Instructions:**
        1. Analyze each topic and its associated news, considering the following factors:
        - Current relevance and popularity of the topic on Twitter.
        - Emotional potential (ability to evoke reactions like excitement, surprise, debate, etc.).
        - Accessibility and universality (does the topic appeal to a broad audience or a specific niche?).
        - Engagement opportunities (does the topic encourage replies, retweets, or discussions?).
        2. Select **one topic** as the best choice for tweeting.
        3. Provide a structured response with:
        - A clear recommendation of the chosen topic.
        - A concise justification (3-5 sentences) explaining why this topic is most likely to generate interactions, based on your analysis.
        4. Adopt a professional, objective, and pragmatic tone, with an understanding of social media dynamics.
        5. Limit your response to 150 words maximum to remain concise and actionable.


        **Expected Response Example:**
        **Recommendation:** Release of a new Marvel movie.
        **Justification:** This topic is highly popular with a broad audience, sparking lively discussions on Twitter. The recent release generates excitement and debates about reviews, encouraging retweets and comments. Associated hashtags (#MarvelMovie) are already viral, amplifying visibility.

        The user will provide you with the list of trending topics and their associated news.
    """

    info = ""
    for news in news_responses_list[-1].news:
        info += f"- Topic: {news.subject}\n{news.content}\n\n"
    user_msg = f"""
        **Provided Data:**
        {info}
    """

    agent = create_react_agent(
        model=llm,
        tools=[],
        prompt=make_system_prompt(system_role),
        response_format=TrendsAnalysisResponse
    )
    logger.info("--- Checking which trend is likely to go viral... ---")
    response = agent.invoke({"messages": [("user", user_msg)]})

    chosen = response.get("structured_response").trend_choice if response.get("structured_response") else None
    return {
            "messages": response["messages"],
            "analysis_schema": response["structured_response"],
            "chosen_trend": chosen,
        }