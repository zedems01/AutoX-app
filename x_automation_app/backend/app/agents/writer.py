from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from ..utils.prompts import writer_prompt
from typing import Dict, Any, Optional
from .state import OverallState
from ..utils.schemas import WriterOutput
from ..config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# try:
#     llm = ChatOpenAI(model=settings.OPENAI_MODEL)
# except Exception as e:
#     logger.error(f"Error initializing OpenAI model: {e}")
#     try:
#         llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, google_api_key=settings.GEMINI_API_KEY)
#     except Exception as e:
#         logger.error(f"Error initializing Google Generative AI model: {e}")
#         llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)

llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)
structured_llm = llm.with_structured_output(WriterOutput)

def writer_node(state: OverallState) -> Dict[str, Any]:
    """
    Generates a content draft and image prompts based on research and user requirements.

    This node uses a structured LLM to synthesize deep research context, public
    opinion analysis, and user-defined parameters into a draft. It also
    handles revision feedback from the HiTL loop.
    
    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'content_draft' and 'image_prompts' keys in the state.
    """
    logger.info("----DRAFTING CONTENT AND IMAGE PROMPTS----\n")

    try:
        final_deep_research_report = state.get("final_deep_research_report", "No deep research context provided.")
        opinion_summary = state.get("opinion_summary", "No opinion summary provided.")
        overall_sentiment = state.get("overall_sentiment", "Neutral")
        x_content_type = state.get("x_content_type", "Article")
        content_length = state.get("content_length", "Medium")
        brand_voice = state.get("brand_voice", "Professional")
        target_audience = state.get("target_audience", "General audience")

        user_config = state.get("user_config") or {}
        content_language = (user_config.content_language if user_config and user_config.content_language is not None 
            else settings.CONTENT_LANGUAGE
        )
        
        # Handle feedback from the HiTL validation step
        feedback = "No feedback provided."
        validation_result = state.get("validation_result")
        if validation_result and validation_result.get("action") == "reject":
            if validation_result.get("data"):
                feedback = validation_result.get("data").get("feedback", "No specific feedback provided.")
            logger.info(f"----Revising draft based on feedback: {feedback}----\n")

        prompt = writer_prompt.format(
            final_deep_research_report=final_deep_research_report,
            opinion_summary=opinion_summary,
            overall_sentiment=overall_sentiment,
            x_content_type=x_content_type,
            content_length=content_length,
            brand_voice=brand_voice,
            target_audience=target_audience,
            feedback=feedback,
            content_language=content_language
        )
        
        writer_output = structured_llm.invoke(prompt)

        logger.info(f"----Draft content generated. {len(writer_output.image_prompts)} image prompts created.----\n")

        return {
            "content_draft": writer_output.content_draft,
            "image_prompts": writer_output.image_prompts if isinstance(writer_output.image_prompts, list) else [writer_output.image_prompts],
        }

    except Exception as e:
        logger.error(f"An error occurred in the writer node: {e}\n")
        return {"error_message": f"An unexpected error occurred during content writing: {str(e)}"}
