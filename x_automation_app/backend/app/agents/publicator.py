from typing import Dict, Any
from .state import OverallState
from ..utils import x_utils
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def publicator_node(state: OverallState) -> Dict[str, Any]:
    """
    Handles the final output of the workflow, either by publishing the content
    to a platform like X or by packaging it for retrieval.
    
    This node is purely programmatic and does not use an LLM.
    
    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'publication_id' in the state.
    """
    logger.info("---PUBLISHING OR PACKAGING FINAL CONTENT---")

    try:
        output_destination = state.get("output_destination")
        final_content = state.get("final_content")
        generated_images = state.get("generated_images")
        session = state.get("session")
        x_content_type = state.get("x_content_type")

        if not final_content:
            raise ValueError("Final content is missing and cannot be published.")

        publication_id = None

        if output_destination == "PUBLISH_X":
            logger.info("---Destination: PUBLISH_X---")
            if not session:
                raise ValueError("Cannot publish to X without a valid session.")

            # For now, we only support attaching the first generated image.
            # This can be expanded to support multiple images per tweet.
            image_url = generated_images[0].s3_url if generated_images else None

            if x_content_type == "TWEET_THREAD":
                logger.info("---Content Type: TWEET_THREAD---")
                # The post_tweet_thread service handles chunking internally.
                # It returns a list of results; we'll use the ID of the first tweet as the publication ID.
                thread_results = x_utils.post_tweet_thread(
                    session=session,
                    tweet_text=final_content,
                    image_url=image_url,
                    proxy=session.get("proxy") # Assuming proxy is stored in session dict
                )
                if thread_results and thread_results[0].get("status") == "success":
                    publication_id = thread_results[0].get("tweet_id")

            elif x_content_type == "SINGLE_TWEET":
                logger.info("---Content Type: SINGLE_TWEET---")
                publication_id = x_utils.post_tweet(
                    session=session,
                    tweet_text=final_content,
                    image_url=image_url,
                    proxy=session.get("proxy")
                )
            
            logger.info(f"---Successfully posted to X. Publication ID: {publication_id}---")

        elif output_destination == "GET_OUTPUTS":
        # else:
            logger.info("---Destination: GET_OUTPUTS---")
            # Format the output as a Markdown string
            markdown_output = f"## Final Content\n\n{final_content}\n\n"
            if generated_images:
                markdown_output += "## Generated Images\n\n"
                for img in generated_images:
                    markdown_output += f"![{img.image_name}]({img.s3_url})\n"
            
            # For GET_OUTPUTS, the publication_id can be the content itself or a confirmation message.
            publication_id = markdown_output
            logger.info("---Content packaged successfully as Markdown.---")

        else:
            raise ValueError(f"Unknown output destination: {output_destination}")

        return {"publication_id": publication_id}

    except Exception as e:
        logger.error(f"An error occurred in the publicator node: {e}")
        return {"error_message": f"An unexpected error occurred during publication: {str(e)}"}
