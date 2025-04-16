from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState

from .get_trends_tool import TrendsResponse
from .get_web_news_tool import WebResponse
from .analyst_schema import TrendsAnalysisResponse
from .writer_tool import WriterResponse




# --- State shared by all agents ---
class WorkflowState(MessagesState):
    trends_schema: TrendsResponse
    news_schema: WebResponse
    analysis_schema: TrendsAnalysisResponse
    writer_schema: WriterResponse
    topic_choice_feedback: str
    final_tweet_feedback: str

# --- Base system prompt for all the agents ---
def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards completing the task you were asked."
        f"\n{suffix}"
    )

OPENAI_LLM = ChatOpenAI(model="gpt-4o")
ANTHROPIC_LLM = ChatAnthropic(model="claude-3-5-sonnet-latest")