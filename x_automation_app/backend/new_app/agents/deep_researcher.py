import os
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from google.genai import Client
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from .tools_and_schemas import SearchQueryList, Reflection
from .configuration import Configuration
from .prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from .utils import (
    get_citations,
    insert_citation_markers,
    resolve_urls,
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# This client is used for the Google Search API tool
# Ensure the API key is loaded from the environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai_client = Client(api_key=api_key)

# --- Research Loop Nodes ---

def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """
    Generates a list of search queries based on the research topic from the state.
    """
    logger.info("---GENERATING DEEP RESEARCH QUERIES---")
    configurable = Configuration.from_runnable_config(config)

    # Determine the topic from the state, prioritizing the analysis result
    topic = state.get("topic_from_opinion_analysis") or state.get("user_provided_topic")
    if not topic:
        raise ValueError("No topic found in the state for deep research.")
    
    logger.info(f"---Researching topic: {topic}---")

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=api_key,
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    formatted_prompt = query_writer_instructions.format(
        current_date=get_current_date(),
        research_topic=topic,
        number_queries=state["initial_search_query_count"],
    )
    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """
    Sends the generated search queries to the web research node for parallel execution.
    """
    logger.info("---CONTINUING TO WEB RESEARCH---")
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """
    Performs web research for a single query using the Google Search API tool.
    """
    logger.info(f"---PERFORMING WEB RESEARCH FOR: {state['search_query']}---")
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )
    # Uses the google genai client as the langchain client doesn't return grounding metadata
    response = genai_client.models.generate_content(
        model=configurable.query_generator_model,
        contents=formatted_prompt,
        config={
            "tools": [{"google_search": {}}],
            "temperature": 0,
        },
    )
    
    # resolve the urls to short urls for saving tokens and time
    resolved_urls = resolve_urls(
        response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
    )
    # Gets the citations and adds them to the generated text
    citations = get_citations(response, resolved_urls)
    modified_text = insert_citation_markers(response.text, citations)
    sources_gathered = [item for citation in citations for item in citation["segments"]]

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [modified_text],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """
    Analyzes research results, identifies knowledge gaps, and generates follow-up queries.
    """
    logger.info("---REFLECTING ON RESEARCH RESULTS---")
    configurable = Configuration.from_runnable_config(config)
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # Determine the topic from the state for the prompt
    topic = state.get("topic_from_opinion_analysis") or state.get("user_provided_topic")

    formatted_prompt = reflection_instructions.format(
        current_date=get_current_date(),
        research_topic=topic,
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )

    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=1.0,
        max_retries=2,
        api_key=api_key,
    )
    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(state: ReflectionState, config: RunnableConfig) -> OverallState:
    """
    LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.
    """
    logger.info("---EVALUATING RESEARCH---")
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        logger.info("---RESEARCH IS SUFFICIENT. FINALIZING ANSWER.---")
        return "finalize_answer"
    else:
        logger.info("---RESEARCH NOT SUFFICIENT. CONTINUING.---")
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """
    LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.
    """
    logger.info("---FINALIZING DEEP RESEARCH REPORT---")
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # Determine the topic from the state for the prompt
    topic = state.get("topic_from_opinion_analysis") or state.get("user_provided_topic")

    formatted_prompt = answer_instructions.format(
        current_date=get_current_date(),
        research_topic=topic,
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=0,
        max_retries=2,
        api_key=api_key,
    )
    response = llm.invoke(formatted_prompt).content

    # Replace the short urls with the original urls and add all used urls to the sources_gathered
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in response:
            response = response.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)
            
    return {
        "final_deep_research_report": response,
        "sources_gathered": unique_sources
    } 