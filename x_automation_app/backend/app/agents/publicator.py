from typing import Dict, Any, List
from .state import OverallState
from ..utils import x_utils
from ..utils.prompts import thread_composer_prompt
from ..utils.schemas import ThreadPlan, GeneratedImage

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import ValidationError
from langchain.agents import AgentExecutor, create_react_agent
from ..config import settings


from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()


def create_thread_composer_agent(llm, tools, prompt):
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=5
    )
    return agent_executor


def publicator_node(state: OverallState) -> Dict[str, Any]:
    """
    Handles the final output of the workflow, either by publishing the content
    to a platform like X or by packaging it for retrieval.
    
    Args:
        state: The current state of the LangGraph.

    Returns:
        A dictionary to update the 'publication_id' in the state.
    """
    logger.info("PUBLISHING/DISPLAYING FINAL CONTENT...")

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
                
                # --- Initialize the Thread Composer Agent ---
                llm = ChatGoogleGenerativeAI(model=settings.GEMINI_REASONING_MODEL, temperature=0.3)
                tools = [x_utils.get_char_count]
                prompt = ChatPromptTemplate.from_template(thread_composer_prompt)
                agent_executor = create_thread_composer_agent(llm, tools, prompt)

                # --- Invoke the agent to get the thread plan ---
                logger.info("Invoking Thread Composer Agent to plan the thread...")
                agent_response = agent_executor.invoke({
                    "final_content": final_content,
                    "image_paths": image_paths
                })
                
                try:
                    thread_plan = ThreadPlan.parse_raw(agent_response["output"])
                except (ValidationError, KeyError) as e:
                    logger.error(f"Failed to parse agent output into ThreadPlan: {e}\nOutput was: {agent_response['output']}")
                    raise ValueError("Could not generate a valid tweet thread plan from the agent.")

                # --- Execute the thread plan ---
                posted_tweets = []
                reply_to_id = None
                for i, chunk in enumerate(thread_plan.thread):
                    logger.info(f"Posting chunk {i+1}/{len(thread_plan.thread)}...")
                    chunk_image_path = [chunk.image_path] if chunk.image_path else None
                    
                    tweet_id = x_utils.post_tweet_v2(
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
                            publication_id = tweet_id  # Set publication_id to the first tweet's ID
                    else:
                        error_msg = f"Failed to post chunk {i+1}"
                        posted_tweets.append({"status": "error", "message": error_msg})
                        logger.error(error_msg)
                        break 

            elif x_content_type == "SINGLE_TWEET":
                logger.info(ctext("Content Type: SINGLE_TWEET", color='white'))
                publication_id = x_utils.post_tweet_v2(
                    login_cookies=session,
                    tweet_text=final_content,
                    image_paths=image_paths,
                    proxy=proxy
                )
            
            logger.info(ctext(f"Successfully posted to X. Publication ID: {publication_id}\n\n", color='white'))

        elif output_destination == "GET_OUTPUTS":
            logger.info(ctext("Destination: GET_OUTPUTS", color='white'))
            publication_id = "Content processed and available for viewing"
            logger.info(ctext("Content displayed successfully.\n\n", color='white'))

        else:
            raise ValueError(f"Unknown output destination: {output_destination}")

        return {"publication_id": publication_id}

    except Exception as e:
        logger.error(f"An error occurred in the publicator node: {e}\n")
        return {"error_message": f"An unexpected error occurred during publication: {str(e)}"}
