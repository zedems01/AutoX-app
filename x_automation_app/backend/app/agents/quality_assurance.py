from typing import List, Optional
import json
from langchain_openai import ChatOpenAI
from ..agents.state import OverallState, TweetDraft
from ..agents.prompts import qa_agent_prompt
from ..agents.tools_and_schemas import FinalTweet

def quality_assurance_node(state: OverallState) -> dict:
    """
    Refines tweet drafts, selects the best one, and decides if an image is needed.

    Args:
        state (OverallState): The current state of the application.

    Returns:
        dict: A dictionary with the final tweet and image prompt.
    """
    # Initialize the LLM with structured output
    # TODO: Make the model configurable via config.py
    model = ChatOpenAI(model="gpt-4.1", temperature=0)
    structured_llm = model.with_structured_output(FinalTweet)

    # Prepare the prompt
    # The prompt expects a JSON string of the tweet drafts
    drafts_json_string = json.dumps(state["tweet_drafts"], indent=2)
    prompt = qa_agent_prompt.format(
        drafts=drafts_json_string
    )

    # Generate content
    response = structured_llm.invoke(prompt)
    
    final_tweet = response.final_tweet
    final_image_prompt = response.final_image_prompt
    
    print("QA Agent selected final tweet.")
    if final_image_prompt:
        print(f"QA Agent finalized image prompt: {final_image_prompt}")

    return {
        "final_tweet": final_tweet,
        "final_image_prompt": final_image_prompt,
    } 