from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
from ..utils.prompts import image_generator_prompt
from typing import Dict, Any, List
from .state import OverallState
from ..utils.schemas import (
    GeneratedImage,
    ValidationAction,
    ImageGeneratorOutput
)
from ..utils.image import generate_and_upload_image
from ..config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



llm = ChatOpenAI(model=settings.OPENAI_MODEL) or ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL)
image_generating_agent = create_react_agent(model=llm, tools=[generate_and_upload_image], response_format=ImageGeneratorOutput)

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
    logger.info("---GENERATING IMAGES---\n")
    logger.info("No prompts found for image generation.")
    return {"generated_images": None}
    
    # try:
    #     final_image_prompts = state.get("final_image_prompts")
    #     if not final_image_prompts:
    #         logger.info("No image prompts found. Skipping image generation.")
    #         return {"generated_images": []}

    #     # Handle feedback from the HiTL validation step
    #     feedback = "No feedback provided."
    #     validation_result = state.get("validation_result")
    #     if validation_result and validation_result.action == ValidationAction.REJECT:
    #         if validation_result.data and validation_result.data.feedback:
    #             feedback = validation_result.data.feedback
    #             logger.info(f"---Revising image prompts based on feedback: {feedback}---\n")

    #     prompt = image_generator_prompt.format(
    #         final_image_prompts=final_image_prompts,
    #         feedback=feedback
    #     )
        
    #     response = image_generating_agent.invoke({"messages": [("user", prompt)]})
    #     parsed_response = response["structured_response"]
    #     # Extract the GeneratedImage objects from the tool call responses
    #     # generated_images = []
    #     # for msg in response.get("messages", []):
    #     #     if isinstance(msg, ToolMessage) and isinstance(msg.content, GeneratedImage):
    #     #         generated_images.append(msg.content)

    #     logger.info(f"---Successfully generated {len(parsed_response.images)} images.---\n")

    #     return {"generated_images": parsed_response.images}

    # except Exception as e:
    #     logger.error(f"An unexpected error occurred in the image generator node: {e}\n")
    #     return {"error_message": f"An unexpected error occurred during image generation: {str(e)}"}
