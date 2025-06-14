from __future__ import annotations
from typing import TypedDict, List, Optional
from typing_extensions import Annotated
from langgraph.graph import add_messages
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
    running_summary: str = field(default=None)

# --- Main Application State ---

class OverallState(TypedDict):
    """
    Represents the complete state of the workflow.
    """
    messages: Annotated[list, add_messages]

    # State for the Deep Research loop
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str