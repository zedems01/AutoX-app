from __future__ import annotations
from typing import TypedDict, Optional, List
from typing_extensions import Annotated
from langgraph.graph import add_messages
from langgraph.graph.message import add_messages
from .tools_and_schemas import Trend, GeneratedImage, TweetSearched, TrendResponse, ValidationResult
import operator
from dataclasses import dataclass, field


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
    running_summary: str = field(default=None)   # Final report


class OverallState(TypedDict):
    """
    Represents the overall state of the workflow, holding all data passed between nodes.
    """

    # === Workflow Configuration ===
    is_autonomous_mode: bool
    output_destination: str
    has_user_provided_topic: bool
    x_content_type: Optional[str]
    content_length: Optional[str]
    brand_voice: Optional[str]
    target_audience: Optional[str]

    # === Login & Session ===
    login_data: Optional[str]
    session: Optional[str]
    user_details: Optional[dict]
    proxy: Optional[str]

    # === Content Generation Data ===
    trending_topics: Optional[List[Trend]]
    selected_topic: Optional[Trend]
    user_provided_topic: Optional[str]

    # === Advanced Search & Opinion Analysis Output ===
    tweet_search_results: Optional[List[TweetSearched]]
    opinion_summary: Optional[str]
    overall_sentiment: Optional[str]
    topic_from_opinion_analysis: Optional[str]

    # === Deep Research Output ===
    final_deep_research_report: Optional[str]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    # reasoning_model: str

    # === Content & Image Drafts ===
    content_draft: Optional[str]
    image_prompts: Optional[List[str]]

    # === Final Output ===
    final_content: Optional[str]
    final_image_prompts: Optional[List[str]]
    generated_images: Optional[List[GeneratedImage]]
    publication_id: Optional[str]

    # === HiTL & Meta-state ===
    next_human_input_step: Optional[str]
    validation_result: Optional[ValidationResult]
    current_step: str
    error_message: Optional[str]
    messages: Annotated[list, add_messages]