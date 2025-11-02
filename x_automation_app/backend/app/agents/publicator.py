from typing import Dict, Any, List
from .state import OverallState
from ..utils.x_utils import get_char_count, post_tweet_v2
from ..utils.prompts import thread_composer_prompt
from ..utils.schemas import ThreadPlan, GeneratedImage
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings


from ..utils.logging_config import setup_logging, ctext
from ..utils.metrics import PUBLICATIONS_TOTAL, AGENT_EXECUTION_TIME, AGENT_INVOCATIONS_TOTAL, ERRORS_TOTAL
import time

logger = setup_logging()





def publicator_node(state: OverallState) -> Dict[str, Any]:
    """
    Handles the final output of the workflow, either by publishing the content
    to a platform like X or by packaging it for retrieval.
    
    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'publication_id' in the state.
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

    thread_composer_agent = create_agent(
        model=model,
        tools=[get_char_count],
        response_format=ThreadPlan
    )

    logger.info("PUBLISHING/DISPLAYING FINAL CONTENT...")

    start_time = time.time()
    status = "success"
    AGENT_INVOCATIONS_TOTAL.labels(agent_name="publicator", status="started").inc()

    try:
        output_destination = state.get("output_destination")
        final_content = state.get("final_content")
        if not final_content:
            raise ValueError("Final content is missing and cannot be published.")

        generated_images: List[GeneratedImage] = state.get("generated_images")
        session = state.get("session")
        proxy = state.get("proxy")
        x_content_type = state.get("x_content_type")

        publication_id = None

        if output_destination == "PUBLISH_X":
            logger.info(ctext("Destination: PUBLISH_X", color='white'))
            if not session:
                raise ValueError("Authentication session is required to publish on X. Please log in.")

            image_paths = [img.local_file_path for img in generated_images] if generated_images else []

            if x_content_type == "TWEET_THREAD":
                logger.info(ctext("Content Type: TWEET_THREAD", color='white'))

                prompt = thread_composer_prompt.format(
                    final_content=final_content,
                    image_paths=image_paths
                )

                response = thread_composer_agent.invoke({"messages": [("user", prompt)]})
                parsed_response = response["structured_response"]

                logger.info(ctext(f"Thread plan completed\n{parsed_response}\n", color='white'))

                # --- Execute the thread plan ---
                posted_tweets = []
                reply_to_id = None
                for i, chunk in enumerate(parsed_response.thread):
                    logger.info(ctext(f"Posting chunk {i+1}/{len(parsed_response.thread)}...", color='white'))
                    chunk_image_path = [chunk.image_path] if chunk.image_path else None
                    
                    tweet_id = post_tweet_v2(
                        login_cookies=session,
                        tweet_text=chunk.text,
                        proxy=proxy,
                        image_paths=chunk_image_path,
                        reply_to_tweet_id=reply_to_id
                    )
                    
                    if tweet_id:
                        posted_tweets.append({"status": "success", "tweet_id": tweet_id})
                        reply_to_id = tweet_id
                        if i == 0:
                            publication_id = tweet_id
                        logger.info(ctext(f"Successfully posted chunk {i+1}\nhttps://x.com/{settings.USER_NAME}/status/{tweet_id}\n", color='white'))
                    else:
                        error_msg = f"Failed to post chunk {i+1}"
                        posted_tweets.append({"status": "error", "message": error_msg})
                        logger.error(error_msg)
                        break 

            elif x_content_type == "SINGLE_TWEET":
                logger.info(ctext("Content Type: SINGLE_TWEET", color='white'))
                publication_id = post_tweet_v2(
                    login_cookies=session,
                    tweet_text=final_content,
                    image_paths=image_paths,
                    proxy=proxy
                )
            
            logger.info(ctext(f"Successfully posted to X: https://x.com/{settings.USER_NAME}/status/{publication_id}\n\n", color='white'))
            PUBLICATIONS_TOTAL.labels(destination="X", status="success").inc()

        elif output_destination == "GET_OUTPUTS":
            logger.info(ctext("Destination: GET_OUTPUTS", color='white'))
            publication_id = "Content processed and available for viewing"
            logger.info(ctext("Content displayed successfully.\n\n", color='white'))
            PUBLICATIONS_TOTAL.labels(destination="draft", status="success").inc()

        else:
            raise ValueError(f"Unknown output destination: {output_destination}")

        return {"publication_id": publication_id}

    except Exception as e:
        logger.error(f"An error occurred in the publicator node: {e}\n")
        status = "error"
        destination = state.get("output_destination", "unknown")
        PUBLICATIONS_TOTAL.labels(
            destination="X" if destination == "PUBLISH_X" else "draft",
            status="failure"
        ).inc()
        ERRORS_TOTAL.labels(error_type=type(e).__name__, component="agent_publicator").inc()
        return {"error_message": f"An unexpected error occurred during publication: {str(e)}"}
    
    finally:
        duration = time.time() - start_time
        AGENT_EXECUTION_TIME.labels(agent_name="publicator", status=status).observe(duration)
        AGENT_INVOCATIONS_TOTAL.labels(agent_name="publicator", status=status).inc()
