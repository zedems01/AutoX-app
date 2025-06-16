from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .prompts import quality_assurance_prompt
from typing import Dict, Any
from .state import OverallState
from .schemas import QAOutput
import logging
from ...config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the base LLM and create a structured version for QA
llm = ChatOpenAI(model=settings.OPENAI_MODEL) or ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL)
structured_llm = llm.with_structured_output(QAOutput)

def quality_assurance_node(state: OverallState) -> Dict[str, Any]:
    """
    Reviews and refines the content draft and image prompts to ensure quality.

    This node uses a structured LLM to act as a QA specialist, making final
    edits to the content and prompts before they are sent to the next step.

    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'final_content' and 'final_image_prompts' keys.
    """
    logger.info("---PERFORMING QUALITY ASSURANCE ON DRAFT---")

    try:
        content_draft = state.get("content_draft")
        image_prompts = state.get("image_prompts")

        if not content_draft or not image_prompts:
            raise ValueError("Content draft or image prompts are missing for QA.")

        # Format the prompt
        prompt = quality_assurance_prompt.format(
            content_draft=content_draft,
            image_prompts=image_prompts,
        )

        # Invoke the structured LLM to get the final, refined output
        qa_output = structured_llm.invoke(prompt)

        logger.info("---QA complete. Content and prompts are finalized.---")

        return {
            "final_content": qa_output.final_content,
            "final_image_prompts": qa_output.final_image_prompts,
        }

    except Exception as e:
        logger.error(f"An error occurred in the quality assurance node: {e}")
        return {"error_message": f"An unexpected error occurred during QA: {str(e)}"}
