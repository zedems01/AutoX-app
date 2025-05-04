from typing import (
    Annotated,
    Optional
)

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from .get_trends_tool import TrendsResponse
from .get_web_news_tool import WebResponse
from .analyst_schema import TrendsAnalysisResponse
from .writer_tool import WriterResponse


def aggregation(left, right):
    if left is None: left = []
    if right is None: right = []
    return left + right

def aggregate_feedbacks(
    left: List[str],
    right: List[str]
) -> List[str]:
    return aggregation(left, right)

def aggregate_trendsresponses(
    left: Optional[List[TrendsResponse]],
    right: Optional[List[TrendsResponse]]
) -> List[TrendsResponse]:
    return aggregation(left, right)

def aggregate_webresponses(
    left: Optional[List[WebResponse]],
    right: Optional[List[WebResponse]]
) -> List[WebResponse]:
    return aggregation(left, right)
    
def aggregate_analysisresponses(
    left: Optional[List[TrendsAnalysisResponse]],
    right: Optional[List[TrendsAnalysisResponse]]
) -> List[TrendsAnalysisResponse]:
    return aggregation(left, right)
    

def aggregate_writerresponses(
    left: Optional[List[WriterResponse]],
    right: Optional[List[WriterResponse]]
) -> List[WriterResponse]:
    return aggregation(left, right)



# --- State shared by all agents ---
# class WorkflowState(MessagesState):
#     trends_schema: TrendsResponse
#     news_schema: WebResponse
#     analysis_schema: TrendsAnalysisResponse
#     trend_choice_feedback: str
#     chosen_trend: str
#     writer_schema: WriterResponse
#     tweet_feedback: str
#     final_tweet: str

auto = True
class WorkflowState(MessagesState):
    complete_automation: bool=auto
    trends_schema: Annotated[Optional[List[TrendsResponse]], aggregate_trendsresponses]
    news_schema: Annotated[Optional[List[WebResponse]], aggregate_webresponses]
    analysis_schema: Annotated[Optional[List[TrendsAnalysisResponse]], aggregate_analysisresponses]
    trend_choice_feedback: Annotated[Optional[List[str]], aggregate_feedbacks]
    chosen_trend: Optional[str]
    writer_schema: Annotated[Optional[List[WriterResponse]], aggregate_writerresponses]
    tweet_validation_feedback: Annotated[Optional[List[str]], aggregate_feedbacks]
    final_tweet: Optional[str]

# --- Base system prompt for all the agents ---
def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards completing the task you were asked."
        f"\n{suffix}"
    )


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