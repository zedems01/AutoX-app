from typing import Dict, Any
from .state import OverallState
from ..utils import x_utils
import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..utils.prompts import markdown_formatter_prompt
from ..config import settings
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Helper function for Markdown Formatting ---
def _create_markdown_from_content(content: str, images: list, model: str) -> str:
    """
    Uses an LLM to format the given content and images into a markdown string.
    """
    try:
        # llm = ChatGoogleGenerativeAI(model=model, google_api_key=settings.GEMINI_API_KEY)
        llm = ChatAnthropic(model=model)
        
        prompt_template = ChatPromptTemplate.from_template(markdown_formatter_prompt)
        
        chain = prompt_template | llm | StrOutputParser()
        
        # Format images for the prompt
        image_details = [
            f"Image Name: {img.image_name}, URL: {img.s3_url}" for img in images
        ] if images else "No images provided."
        
        formatted_prompt = {
            "content": content,
            "images": "\n".join(image_details)
        }
        
        markdown_output = chain.invoke(formatted_prompt)
        return markdown_output
    except Exception as e:
        logger.error(f"Error formatting content to markdown: {e}")
        # Fallback to a simpler markdown format if LLM fails
        fallback_md = f"## Final Content\n\n{content}\n\n"
        if images:
            fallback_md += "## Generated Images\n\n"
            for img in images:
                fallback_md += f"![{img.image_name}]({img.s3_url})\n"
        return fallback_md

def publicator_node(state: OverallState) -> Dict[str, Any]:
    """
    Handles the final output of the workflow. It formats the content into markdown,
    and optionally publishes it to a platform like X.
    
    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the state with publication details and final markdown.
    """
    logger.info("---PUBLISHING AND/OR PACKAGING FINAL CONTENT---\n")

    try:
        final_content = state.get("final_content")
        if not final_content:
            raise ValueError("Final content is missing.")

        generated_images = state.get("generated_images", [])
        output_destination = state.get("output_destination")
        session = state.get("session")
        x_content_type = state.get("x_content_type")
        
        # Always generate markdown content
        logger.info("---Formatting final content into Markdown---\n")
        markdown_content = _create_markdown_from_content(
            final_content, 
            generated_images,
            settings.ANTHROPIC_MODEL
        )

        publication_id = None
        if output_destination == "PUBLISH_X":
            logger.info("---Destination: PUBLISH_X---\n")
            if not session:
                raise ValueError("Authentication session is required to publish on X. Please log in.")
            
            image_url = generated_images[0].s3_url if generated_images else None

            if x_content_type == "TWEET_THREAD":
                logger.info("---Content Type: TWEET_THREAD---\n")
                thread_results = x_utils.post_tweet_thread(
                    session=session,
                    tweet_text=final_content,
                    image_url=image_url,
                    proxy=session.get("proxy")
                )
                if thread_results and thread_results[0].get("status") == "success":
                    publication_id = thread_results[0].get("tweet_id")
            else: # SINGLE_TWEET
                logger.info("---Content Type: SINGLE_TWEET---\n")
                publication_id = x_utils.post_tweet(
                    session=session,
                    tweet_text=final_content,
                    image_url=image_url,
                    proxy=session.get("proxy")
                )
            
            logger.info(f"---Successfully posted to X. Publication ID: {publication_id}---\n")

        elif output_destination == "GET_OUTPUTS":
            logger.info("---Destination: GET_OUTPUTS---\n")
            # For GET_OUTPUTS, the publication_id can be a confirmation message.
            publication_id = "Content processed and available for viewing."
            logger.info("---Content packaged successfully.---\n")

        else:
            raise ValueError(f"Unknown output destination: {output_destination}")

        return {
            "publication_id": publication_id,
            "final_markdown_content": markdown_content
        }

    except Exception as e:
        logger.error(f"An error occurred in the publicator node: {e}\n")
        return {"error_message": f"An unexpected error occurred during publication: {str(e)}"}
