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
    
    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'publication_id' in the state.
    """
    logger.info("---PUBLISHING OR PACKAGING FINAL CONTENT---\n")

    try:
        output_destination = state.get("output_destination")
        final_content = state.get("final_content")
        if not final_content:
            raise ValueError("Final content is missing and cannot be published.")

        generated_images = state.get("generated_images")
        session = state.get("session")
        x_content_type = state.get("x_content_type")

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

            elif x_content_type == "SINGLE_TWEET":
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
            publication_id = "Content processed and available for viewing."
            logger.info("---Content packaged successfully.---\n")

        else:
            raise ValueError(f"Unknown output destination: {output_destination}")

        return {"publication_id": publication_id}

    except Exception as e:
        logger.error(f"An error occurred in the publicator node: {e}\n")
        return {"error_message": f"An unexpected error occurred during publication: {str(e)}"}
