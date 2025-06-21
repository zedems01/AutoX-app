from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from ..utils.prompts import quality_assurance_prompt
from typing import Dict, Any
from .state import OverallState
from ..utils.schemas import QAOutput
import logging
from ..config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the base LLM and create a structured version for QA
# llm = ChatOpenAI(model=settings.OPENAI_MODEL) or ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, google_api_key=settings.GEMINI_API_KEY)
# llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, google_api_key=settings.GEMINI_API_KEY)
# llm = ChatGroq(model=settings.GROQ_MODEL)
llm = ChatAnthropic(model=settings.ANTHROPIC_MODEL)
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
    logger.info("---PERFORMING QUALITY ASSURANCE ON DRAFT---\n")

    try:
        # Extract existing draft and prompts
        content_draft = state.get("content_draft")
        image_prompts = state.get("image_prompts")
        if not content_draft or not image_prompts:
            raise ValueError("Content draft or image prompts are missing for QA.")

        # Extract the original writer's context for a more informed QA
        final_deep_research_report = state.get("final_deep_research_report", "No deep research context provided.")
        opinion_summary = state.get("opinion_summary", "No opinion summary provided.")
        x_content_type = state.get("x_content_type", "Article")
        brand_voice = state.get("brand_voice", "Professional")
        target_audience = state.get("target_audience", "General audience")

        # Handle feedback from the HiTL validation step (same as writer)
        feedback = "No feedback provided."
        validation_result = state.get("validation_result")
        if validation_result and validation_result.get("action") == "reject":
            if validation_result.get("data"):
                feedback = validation_result.get("data").get("feedback", "No specific feedback provided.")


        # Format the prompt with all the context
        prompt = quality_assurance_prompt.format(
            content_draft=content_draft,
            image_prompts=image_prompts,
            final_deep_research_report=final_deep_research_report,
            opinion_summary=opinion_summary,
            x_content_type=x_content_type,
            brand_voice=brand_voice,
            target_audience=target_audience,
            feedback=feedback,
        )

        # Invoke the structured LLM to get the final, refined output
        qa_output = structured_llm.invoke(prompt)

        logger.info("---QA complete. Content and prompts are finalized.---\n")

        return {
            "final_content": qa_output.final_content,
            "final_image_prompts": qa_output.final_image_prompts,
        }

    except Exception as e:
        logger.error(f"An error occurred in the quality assurance node: {e}\n")
        return {"error_message": f"An unexpected error occurred during QA: {str(e)}"}
