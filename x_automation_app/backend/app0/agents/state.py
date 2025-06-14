from __future__ import annotations
from typing import TypedDict, List, Optional
from typing_extensions import Annotated
from langgraph.graph import add_messages
import operator
from dataclasses import dataclass, field

# --- Helper schemas for state ---

class Trend(TypedDict):
    """Represents a single trending topic found on X."""
    name: str
    url: str
    tweet_count: Optional[int]

class TweetDraft(TypedDict):
    """Represents a single generated tweet draft."""
    text: str
    image_prompt: Optional[str]

# --- State for the Deep Research Loop ---

class Query(TypedDict):
    query: str
    rationale: str

class QueryGenerationState(TypedDict):
    query_list: list[Query]

class WebSearchState(TypedDict):
    search_query: str
    id: str

class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int

@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)

# --- Main Application State ---

class OverallState(TypedDict):
    """
    Represents the complete state of the workflow.
    """
    messages: Annotated[list, add_messages]

    # Overall workflow state
    trending_topics: Annotated[List[Trend], operator.add]
    selected_topic: Optional[Trend]
    current_context: Optional[str]
    noteworthy_fact: Optional[str]
    tweet_drafts: Annotated[List[TweetDraft], operator.add]
    final_tweet: Optional[str]
    final_image_prompt: Optional[str]
    final_image_url: Optional[str]
    publication_id: Optional[str]

    # State for the Deep Research loop
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str

    # Human-in-the-Loop interaction state
    human_in_the_loop_required: bool
    validation_result: Optional[dict]

    # Meta-state
    current_step: str
    error_message: Optional[str] 