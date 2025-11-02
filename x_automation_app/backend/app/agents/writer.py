from langchain.chat_models import init_chat_model
from ..utils.prompts import writer_prompt
from typing import Dict, Any
from .state import OverallState
from ..utils.schemas import WriterOutput
from ..config import settings

from ..utils.logging_config import setup_logging, ctext
from ..utils.metrics import CONTENT_DRAFTS_TOTAL, AGENT_EXECUTION_TIME, AGENT_INVOCATIONS_TOTAL, ERRORS_TOTAL
import time

logger = setup_logging()



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
    start_time = time.time()
    status = "success"
    AGENT_INVOCATIONS_TOTAL.labels(agent_name="writer", status="started").inc()

    try:
        llm = f"openai:{settings.OPENAI_MODEL}"
        model = init_chat_model(llm)
        # llm = f"google_genai:{settings.GEMINI_MODEL}"
        # model = init_chat_model(llm, api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing OpenRouter model, using Gemini model as fallback: {e}")
        try:
            # llm = f"openai:{settings.OPENAI_MODEL}"
            # model = init_chat_model(llm)
            llm = f"google_genai:{settings.GEMINI_MODEL}"
            model = init_chat_model(llm, api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Error initializing Google Generative AI model, please check your credentials: {e}")

    structured_llm = model.with_structured_output(WriterOutput)
    
    logger.info("DRAFTING CONTENT AND IMAGE PROMPTS...")

    try:
        final_deep_research_report = state.get("final_deep_research_report", "No deep research context provided.")
        opinion_summary = state.get("opinion_summary", "No opinion summary provided.")
        overall_sentiment = state.get("overall_sentiment", "Neutral")
        x_content_type = state.get("x_content_type", "Article")
        content_length = state.get("content_length", "Medium")
        content_draft = state.get("content_draft", "")  # Get existing draft for revisions
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
            content_draft=content_draft,
            feedback=feedback,
            content_language=content_language
        )
        
        writer_output = structured_llm.invoke(prompt)
        content_draft = writer_output.content_draft
        image_prompts = writer_output.image_prompts if isinstance(writer_output.image_prompts, list) else [writer_output.image_prompts]

        logger.info(ctext(f"Content successfully drafted; {len(image_prompts)} image prompts created.\n", color='white'))

        # Track content draft generation
        CONTENT_DRAFTS_TOTAL.labels(
            content_type=x_content_type,
            content_length=content_length
        ).inc()

        return {
            "content_draft": content_draft,
            "image_prompts": image_prompts,
        }

    except Exception as e:
        logger.error(f"An error occurred in the writer node: {e}\n")
        status = "error"
        ERRORS_TOTAL.labels(error_type=type(e).__name__, component="agent_writer").inc()
        return {"error_message": f"An unexpected error occurred during content writing: {str(e)}"}
    
    finally:
        duration = time.time() - start_time
        AGENT_EXECUTION_TIME.labels(agent_name="writer", status=status).observe(duration)
        AGENT_INVOCATIONS_TOTAL.labels(agent_name="writer", status=status).inc()
