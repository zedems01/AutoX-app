from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..utils.prompts import image_generator_prompt, get_current_time
from typing import Dict, Any, List
from .state import OverallState
from ..utils.schemas import (
    GeneratedImage,
    ValidationAction,
    ImageGeneratorOutput
)
from ..utils.image import generate_and_upload_image
from ..config import settings

from ..utils.logging_config import setup_logging, ctext
from ..utils.metrics import IMAGES_GENERATED_TOTAL, AGENT_EXECUTION_TIME, AGENT_INVOCATIONS_TOTAL, ERRORS_TOTAL
import time

logger = setup_logging()


def image_generator_node(state: OverallState) -> Dict[str, List[GeneratedImage]]:
    """
    Generates images based on a list of prompts using a ReAct agent.

    This node invokes an agent that iteratively calls an image generation tool.
    It then inspects the agent's message history to extract the results of
    those tool calls and updates the state.

    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'generated_images' key in the state.
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


    image_generating_agent = create_react_agent(
        model=llm,
        tools=[generate_and_upload_image],
        response_format=ImageGeneratorOutput
    )


    logger.info("GENERATING CONTENT IMAGES...")
    
    start_time = time.time()
    status = "success"
    AGENT_INVOCATIONS_TOTAL.labels(agent_name="image_generator", status="started").inc()
    
    try:
        final_image_prompts = state.get("final_image_prompts")
        if not final_image_prompts:
            logger.info(ctext("No image prompts found. Skipping image generation.", color='white'))
            return {"generated_images": []}

        # Handle feedback from the HiTL validation step
        feedback = "No feedback provided."
        validation_result = state.get("validation_result")

        if isinstance(validation_result, dict) and validation_result.get("action") == ValidationAction.REJECT:
            data = validation_result.get("data")
            if isinstance(data, dict):
                feedback_from_data = data.get("feedback")
                if feedback_from_data:
                    feedback = feedback_from_data
                    logger.info(ctext(f"Revising image prompts based on feedback: {feedback}\n", color='white'))


        prompt = image_generator_prompt.format(
            final_image_prompts=final_image_prompts,
            feedback=feedback,
            current_timestamp=get_current_time()
        )
        
        response = image_generating_agent.invoke({"messages": [("user", prompt)]})
        parsed_response = response["structured_response"]

        logger.info(ctext(f"Successfully generated {len(parsed_response.images)} images.\n", color='white'))

        # Track image generation
        for _ in parsed_response.images:
            IMAGES_GENERATED_TOTAL.labels(status="success").inc()

        return {"generated_images": parsed_response.images}

    except Exception as e:
        logger.error(f"An unexpected error occurred in the image generator node: {e}\n")
        status = "error"
        IMAGES_GENERATED_TOTAL.labels(status="failure").inc()
        ERRORS_TOTAL.labels(error_type=type(e).__name__, component="agent_image_generator").inc()
        return {"error_message": f"An unexpected error occurred during image generation: {str(e)}"}
    
    finally:
        duration = time.time() - start_time
        AGENT_EXECUTION_TIME.labels(agent_name="image_generator", status=status).observe(duration)
        AGENT_INVOCATIONS_TOTAL.labels(agent_name="image_generator", status=status).inc()
