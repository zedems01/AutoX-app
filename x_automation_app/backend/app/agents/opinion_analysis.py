import json
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from ..utils.prompts import opinion_analysis_prompt
from typing import Dict, Any
from .state import OverallState
from ..utils.schemas import OpinionAnalysisOutput
from ..config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


try:
    llm = ChatOpenAI(model=settings.OPENAI_MODEL)
except Exception as e:
    logger.error(f"Error initializing OpenAI model: {e}")
    try:
        llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, google_api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing Google Generative AI model: {e}")
        llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)

structured_llm = llm.with_structured_output(OpinionAnalysisOutput)

def opinion_analysis_node(state: OverallState) -> Dict[str, Any]:
    """
    Analyzes tweets from the state to produce a summary, sentiment, and refined topic.

    This node uses a structured LLM call to ensure the output is a valid
    Pydantic object. It takes the list of tweets, asks the LLM to analyze them,
    and returns the structured data to update the state.

    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'opinion_summary', 'overall_sentiment',
        and 'topic_from_opinion_analysis' keys in the state.
    """
    logger.info("----ANALYZING TWEET OPINIONS----\n")

    try:
        tweets = state.get("tweet_search_results")
        if not tweets:
            raise ValueError("No tweets found in the state to analyze.")

        tweets_json_string = json.dumps([tweet.model_dump() for tweet in tweets])
        prompt = opinion_analysis_prompt.format(tweets=tweets_json_string)

        analysis_result = structured_llm.invoke(prompt)

        logger.info(f"----Opinion analysis complete. Refined topic: {analysis_result.topic_from_opinion_analysis}----\n")

        return {
            "opinion_summary": analysis_result.opinion_summary,
            "overall_sentiment": analysis_result.overall_sentiment,
            "topic_from_opinion_analysis": analysis_result.topic_from_opinion_analysis,
        }

    except Exception as e:
        logger.error(f"An error occurred in the opinion analysis node: {e}\n")
        return {"error_message": f"An unexpected error occurred during opinion analysis: {str(e)}"}
