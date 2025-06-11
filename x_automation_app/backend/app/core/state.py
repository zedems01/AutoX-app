from typing import TypedDict, List, Optional
from typing_extensions import Annotated
from langgraph.graph import add_messages
import operator

class Trend(TypedDict):
    """Represents a single trending topic found on X."""
    name: str
    url: str
    tweet_count: Optional[int]

class TweetDraft(TypedDict):
    """Represents a single generated tweet draft."""
    text: str
    image_prompt: Optional[str]

class OverallState(TypedDict):
    """
    Represents the complete state of the content generation workflow.
    This TypedDict is used as the schema for the StateGraph.
    """
    messages: Annotated[list, add_messages]

    # Agent-specific outputs
    trending_topics: Annotated[List[Trend], operator.add]
    selected_topic: Optional[Trend]
    current_context: Optional[str]
    noteworthy_fact: Optional[str]
    tweet_drafts: Annotated[List[TweetDraft], operator.add]
    final_tweet: Optional[str]
    final_image_prompt: Optional[str]
    final_image_url: Optional[str]

    # Human-in-the-Loop interaction state
    human_in_the_loop_required: bool
    validation_result: Optional[dict] # To store user's validation choice

    # Meta-state
    current_step: str # To track the current step in the process for UI
    error_message: Optional[str]
    publication_id: Optional[str] 