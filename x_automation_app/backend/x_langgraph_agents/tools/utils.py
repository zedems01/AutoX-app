import collections.abc

from typing import (
    TypeVar,
    Annotated,
    Optional,
    Literal,
    List,
    Union,
    Sequence
)

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from .get_trends_tool import TrendsResponse
from .get_web_news_tool import WebResponse
from .analyst_schema import TrendsAnalysisResponse
from .writer_schema import WriterResponse


# Generic type variable
T = TypeVar('T')

def aggregate_list(
    left: Optional[Union[T, List[T]]],
    right: Optional[Union[T, List[T]]]
) -> List[T]:
    """
    Aggregates items or lists of items into a single list.

    Handles LangGraph's behavior where 'left' might be the first single item
    assigned directly to the state channel before aggregation starts.
    """
    # 1. Initialize or standardize 'left' into a list
    if left is None:
        left_list = []
    elif not isinstance(left, list):
        # If left is a single item (LangGraph's first assignment), wrap it in a list.
        left_list = [left]
    else:
        # left is already a list being built upon.
        left_list = left

    # 2. Add 'right' to the 'left_list'
    if right is None:
        # Nothing to add from right.
        return left_list

    # Check if 'right' is a sequence (list, tuple, etc.) but not a string/bytes
    if isinstance(right, collections.abc.Sequence) and not isinstance(right, (str, bytes)):
        # If right is a list/sequence, extend left_list with its elements.
        # Convert right to list just to be safe for '+' concatenation.
        return left_list + list(right)
    else:
        # If right is a single item, append it as a new element.
        return left_list + [right]

# --- Specific aggregation functions using the robust aggregate_list ---

def aggregate_feedbacks(
    left: Optional[Union[str, List[str]]],
    right: Optional[Union[str, List[str]]]
) -> List[str]:
    return aggregate_list(left, right)

def aggregate_trendsresponses(
    left: Optional[Union[TrendsResponse, List[TrendsResponse]]],
    right: Optional[Union[TrendsResponse, List[TrendsResponse]]]
) -> List[TrendsResponse]:
    return aggregate_list(left, right)

def aggregate_webresponses(
    left: Optional[Union[WebResponse, List[WebResponse]]],
    right: Optional[Union[WebResponse, List[WebResponse]]]
) -> List[WebResponse]:
    return aggregate_list(left, right)

def aggregate_analysisresponses(
    left: Optional[Union[TrendsAnalysisResponse, List[TrendsAnalysisResponse]]],
    right: Optional[Union[TrendsAnalysisResponse, List[TrendsAnalysisResponse]]]
) -> List[TrendsAnalysisResponse]:
    return aggregate_list(left, right)

def aggregate_writerresponses(
    left: Optional[Union[WriterResponse, List[WriterResponse]]],
    right: Optional[Union[WriterResponse, List[WriterResponse]]]
) -> List[WriterResponse]:
    return aggregate_list(left, right)



# --- Workflow State Definition ---


class WorkflowState(MessagesState):
    complete_automation: bool
    next_scraping_prompt: Optional[str]
    chosen_trend: Optional[str]
    final_tweet: Optional[str]


    trends_schema: Annotated[Optional[List[TrendsResponse]], aggregate_trendsresponses]
    news_schema: Annotated[Optional[List[WebResponse]], aggregate_webresponses]
    analysis_schema: Annotated[Optional[List[TrendsAnalysisResponse]], aggregate_analysisresponses]
    trend_choice_feedback: Annotated[Optional[List[str]], aggregate_feedbacks]
    writer_schema: Annotated[Optional[List[WriterResponse]], aggregate_writerresponses]
    tweet_validation_feedback: Annotated[Optional[List[str]], aggregate_feedbacks]


def get_state_items_as_list(
    state_value: Optional[Union[T, List[T]]]
) -> List[T]:
    """
    Safely returns the state value as a list.
    Returns an empty list if the value is None.
    Wraps a single item in a list if it's not already a list.
    Returns the list directly if it's already a list.
    """
    if state_value is None:
        return []
    if isinstance(state_value, list):
        return state_value
    else:
        # It's a single item T
        return [state_value]

# --- Base system prompt for all the agents ---
def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards completing the task you were asked."
        f"\n{suffix}"
    )


def router_trend_choice(state: WorkflowState) -> Literal["writer", "trend_feedback_node"]:
    if state.get('complete_automation')==True:
        return "writer"
    else:
        return "trend_feedback_node"
    
def router_tweet_validation(state: WorkflowState) -> Literal["publication_node", "tweet_feedback_node"]:
    if state.get('complete_automation')==True:
        return "publication_node"
    else:
        return "tweet_feedback_node"



def print_stream(stream):
    """A utility to pretty print the stream."""
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

OPENAI_LLM = ChatOpenAI(model="gpt-4o")
ANTHROPIC_LLM = ChatAnthropic(model="claude-3-5-sonnet-latest")