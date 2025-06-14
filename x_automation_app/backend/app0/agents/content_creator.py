from typing import List
from langchain_openai import ChatOpenAI
from ..agents.state import OverallState
from ..agents.prompts import content_creator_prompt
from ..agents.tools_and_schemas import TweetDrafts


def content_creator_node(state: OverallState) -> dict:
    """
    Generates tweet drafts based on the selected topic and noteworthy fact.

    Args:
        state (OverallState): The current state of the application.

    Returns:
        dict: A dictionary with the updated list of tweet drafts.
    """
    # Initialize the LLM with structured output
    # TODO: Make the model configurable via config.py
    model = ChatOpenAI(model="gpt-4.1", temperature=0.7)
    structured_llm = model.with_structured_output(TweetDrafts)

    # Prepare the prompt
    prompt = content_creator_prompt.format(
        topic=state["selected_topic"]["name"],
        fact=state["noteworthy_fact"]
    )

    # Generate content
    response = structured_llm.invoke(prompt)
    
    # Convert Pydantic models to dictionaries for state compatibility
    tweet_drafts = [draft.model_dump() for draft in response.drafts]

    print(f"Generated {len(tweet_drafts)} tweet drafts.")

    return {"tweet_drafts": tweet_drafts} 