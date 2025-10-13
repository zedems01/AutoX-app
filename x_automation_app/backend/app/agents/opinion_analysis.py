import json
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..utils.prompts import opinion_analysis_prompt
from typing import Dict, Any
from .state import OverallState
from ..utils.schemas import OpinionAnalysisOutput
from ..config import settings
from ..utils.x_utils import data_to_csv

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()


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

    try:
        llm = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            model=settings.OPENROUTER_MODEL
        )
    except Exception as e:
        logger.error(f"Error initializing OpenRouter model, using Gemini model as fallback: {e}")
        try:
            llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
        except Exception as e:
            logger.error(f"Error initializing Google Generative AI model, please check your credentials: {e}")

    structured_llm = llm.with_structured_output(OpinionAnalysisOutput)


    logger.info("ANALYZING TWEETS CONTENT...")

    try:
        tweets = state.get("tweet_search_results")
        if not tweets:
            raise ValueError("No tweets found in the state to analyze.")

        data = [tweet.model_dump() for tweet in tweets]
        csv_data = data_to_csv(data)
        prompt = opinion_analysis_prompt.format(tweets=csv_data)
        print(prompt)

        analysis_result = structured_llm.invoke(prompt)

        logger.info(ctext(f"Opinion analysis completed\nOverall sentiment: {analysis_result.overall_sentiment};\nRefined topic: {analysis_result.topic_from_opinion_analysis}\n", color='white'))

        return {
            "opinion_summary": analysis_result.opinion_summary,
            "overall_sentiment": analysis_result.overall_sentiment,
            "topic_from_opinion_analysis": analysis_result.topic_from_opinion_analysis,
        }

    except Exception as e:
        logger.error(f"An error occurred in the opinion analysis node: {e}\n")
        return {"error_message": f"An unexpected error occurred during opinion analysis: {str(e)}"} 
