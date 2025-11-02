from langchain.chat_models import init_chat_model

from ..utils.prompts import quality_assurance_prompt
from typing import Dict, Any
from .state import OverallState
from ..utils.schemas import QAOutput
from ..config import settings

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()



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

    try:
        llm = f"google_genai:{settings.GEMINI_MODEL}"
        model = init_chat_model(llm, api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error initializing OpenRouter model, using Gemini model as fallback: {e}")
        try:
            llm = f"openai:{settings.OPENAI_MODEL}"
            model = init_chat_model(llm)
        except Exception as e:
            logger.error(f"Error initializing Google Generative AI model, please check your credentials: {e}")

    structured_llm = model.with_structured_output(QAOutput)


    logger.info("QUALITY REVIEW ON CONTENT DRAFT")

    try:
        content_draft = state.get("content_draft")
        content_length = state.get("content_length")
        image_prompts = state.get("image_prompts")
        if not content_draft or not image_prompts:
            raise ValueError("Content draft or image prompts are missing for QA.")

        # final_deep_research_report = state.get("final_deep_research_report", "No deep research context provided.")
        # opinion_summary = state.get("opinion_summary", "No opinion summary provided.")
        # x_content_type = state.get("x_content_type", "Article")
        # brand_voice = state.get("brand_voice", "Professional")
        # target_audience = state.get("target_audience", "General audience")

        # user_config = state.get("user_config") or {}
        # content_language = (user_config.content_language if user_config and user_config.content_language is not None 
        #     else settings.CONTENT_LANGUAGE
        # )

        # Handle feedback from the HiTL validation step
        # feedback = "No feedback provided."
        # validation_result = state.get("validation_result")
        # if validation_result and validation_result.get("action") == "reject":
        #     if validation_result.get("data"):
        #         feedback = validation_result.get("data").get("feedback", "No specific feedback provided.")

        # prompt = quality_assurance_prompt.format(
        #     content_draft=content_draft,
        #     image_prompts=image_prompts,
        #     final_deep_research_report=final_deep_research_report,
        #     opinion_summary=opinion_summary,
        #     x_content_type=x_content_type,
        #     brand_voice=brand_voice,
        #     target_audience=target_audience,
        #     feedback=feedback,
        #     content_language=content_language,
        # )

        # qa_output = structured_llm.invoke(prompt)
        # final_content = qa_output.final_content
        # final_image_prompts = qa_output.final_image_prompts if isinstance(qa_output.final_image_prompts, list) else [qa_output.final_image_prompts]

        # logger.info(ctext("Content and prompts are finalized.\n", color='white'))
        # if content_length in ["Short", "Medium"] and len(final_image_prompts) > 0:
        #     logger.info(ctext(f"Content:\n{final_content}\n\nImage prompts:\n{'\n- '.join(final_image_prompts)}\n", color='white', italic=True))
        # else:
        #     logger.info(ctext(f"Content:\n{final_content}\n", color='white', italic=True))

        # return {
        #     "final_content": final_content,
        #     "final_image_prompts": final_image_prompts,
        # }

        logger.info(ctext("Content and prompts are finalized.\n", color='white'))
        if content_length in ["Short", "Medium"] and len(image_prompts) > 0:
            logger.info(ctext(f"Content:\n{content_draft}\n\nImage prompts:\n{'\n- '.join(image_prompts)}\n", color='white', italic=True))
        else:
            logger.info(ctext(f"Content:\n{content_draft}\n", color='white', italic=True))

        return {
            "final_content": content_draft,
            "final_image_prompts": image_prompts,
        }

    except Exception as e:
        logger.error(f"An error occurred in the quality assurance node: {e}\n")
        return {"error_message": f"An unexpected error occurred during QA: {str(e)}"}
