import os
from typing import Any, Dict, List
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from google.genai import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage

from .state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from ..utils.schemas import SearchQueryList, Reflection
from .deep_research_config import Configuration
from ..utils.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)

from ..utils.logging_config import setup_logging, ctext
logger = setup_logging()


# Helper functions

def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {message.content}\n"
    return research_topic


def resolve_urls(urls_to_resolve: List[Any], id: int) -> Dict[str, str]:
    """
    Create a map of the vertex ai search urls (very long) to a short url with a unique id for each url.
    Ensures each original URL gets a consistent shortened form while maintaining uniqueness.
    """
    prefix = f"https://vertexaisearch.cloud.google.com/id/"
    urls = [
        site.web.uri for site in urls_to_resolve if site is not None and hasattr(site, 'web') and site.web is not None and hasattr(site.web, 'uri') and site.web.uri is not None
    ]

    # Dictionary that maps each unique URL to its first occurrence index
    resolved_map = {}
    for idx, url in enumerate(urls):
        if url not in resolved_map:
            resolved_map[url] = f"{prefix}{id}-{idx}"

    return resolved_map


def insert_citation_markers(text, citations_list):
    """
    Inserts citation markers into a text string based on start and end indices.

    Args:
        text (str): The original text string.
        citations_list (list): A list of dictionaries, where each dictionary
                               contains 'start_index', 'end_index', and
                               'segment_string' (the marker to insert).
                               Indices are assumed to be for the original text.

    Returns:
        str: The text with citation markers inserted.
    """
    # Sort citations by end_index in descending order.
    # If end_index is the same, secondary sort by start_index descending.
    # This ensures that insertions at the end of the string don't affect
    # the indices of earlier parts of the string that still need to be processed.
    sorted_citations = sorted(
        citations_list, key=lambda c: (c["end_index"], c["start_index"]), reverse=True
    )

    modified_text = text
    for citation_info in sorted_citations:
        # These indices refer to positions in the *original* text,
        # but since we iterate from the end, they remain valid for insertion
        # relative to the parts of the string already processed.
        end_idx = citation_info["end_index"]
        marker_to_insert = ""
        for segment in citation_info["segments"]:
            marker_to_insert += f" [{segment['label']}]({segment['short_url']})"
        # Insert the citation marker at the original end_idx position
        modified_text = (
            modified_text[:end_idx] + marker_to_insert + modified_text[end_idx:]
        )

    return modified_text


def get_citations(response, resolved_urls_map):
    """
    Extracts and formats citation information from a Gemini model's response.

    This function processes the grounding metadata provided in the response to
    construct a list of citation objects. Each citation object includes the
    start and end indices of the text segment it refers to, and a string
    containing formatted markdown links to the supporting web chunks.

    Args:
        response: The response object from the Gemini model, expected to have
                  a structure including `candidates[0].grounding_metadata`.
                  It also relies on a `resolved_map` being available in its
                  scope to map chunk URIs to resolved URLs.

    Returns:
        list: A list of dictionaries, where each dictionary represents a citation
              and has the following keys:
              - "start_index" (int): The starting character index of the cited
                                     segment in the original text. Defaults to 0
                                     if not specified.
              - "end_index" (int): The character index immediately after the
                                   end of the cited segment (exclusive).
              - "segments" (list[str]): A list of individual markdown-formatted
                                        links for each grounding chunk.
              - "segment_string" (str): A concatenated string of all markdown-
                                        formatted links for the citation.
              Returns an empty list if no valid candidates or grounding supports
              are found, or if essential data is missing.
    """
    citations = []

    # Ensure response and necessary nested structures are present
    if not response or not response.candidates:
        return citations

    candidate = response.candidates[0]
    if (
        not hasattr(candidate, "grounding_metadata")
        or not candidate.grounding_metadata
        or not hasattr(candidate.grounding_metadata, "grounding_supports")
    ):
        return citations

    for support in candidate.grounding_metadata.grounding_supports:
        citation = {}

        # Ensure segment information is present
        if not hasattr(support, "segment") or support.segment is None:
            continue  # Skip this support if segment info is missing

        start_index = (
            support.segment.start_index
            if support.segment.start_index is not None
            else 0
        )

        # Ensure end_index is present to form a valid segment
        if support.segment.end_index is None:
            continue  # Skip if end_index is missing, as it's crucial

        # Add 1 to end_index to make it an exclusive end for slicing/range purposes
        # (assuming the API provides an inclusive end_index)
        citation["start_index"] = start_index
        citation["end_index"] = support.segment.end_index

        citation["segments"] = []
        if (
            hasattr(support, "grounding_chunk_indices")
            and support.grounding_chunk_indices
        ):
            for ind in support.grounding_chunk_indices:
                try:
                    chunk = candidate.grounding_metadata.grounding_chunks[ind]
                    resolved_url = resolved_urls_map.get(chunk.web.uri, None)
                    citation["segments"].append(
                        {
                            "label": chunk.web.title.split(".")[:-1][0],
                            "short_url": resolved_url,
                            "value": chunk.web.uri,
                        }
                    )
                except (IndexError, AttributeError, NameError):
                    # Handle cases where chunk, web, uri, or resolved_map might be problematic
                    # For simplicity, we'll just skip adding this particular segment link
                    # In a production system, you might want to log this.
                    pass
        citations.append(citation)
    return citations




# Google Search API tool is used to get grounding metadata
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
    logger.info("GENERATING QUERIES FOR DEEP RESEARCH...")

    configurable = Configuration.from_runnable_config(config)
    user_config = state.get("user_config") or {}
    query_generator_model = (user_config.gemini_base_model if user_config and user_config.gemini_base_model is not None 
        else configurable.query_generator_model
    )

    # Determine the topic from the state, prioritizing the analysis result
    topic = state.get("topic_from_opinion_analysis") or state.get("user_provided_topic")
    if not topic:
        raise ValueError("No topic found in the state for deep research.")
    
    logger.info(ctext(f"Research topic: {ctext(topic, color='white', italic=True)}", color='white'))

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    llm = ChatGoogleGenerativeAI(
        model=query_generator_model,
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
    # logger.info("----CONTINUING TO WEB RESEARCH----\n")
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """
    Performs web research for a single query using the Google Search API tool.
    """
    logger.info(ctext(f"Performing web research for the query: {ctext(state['search_query'], color='white', italic=True)}", color='white'))

    configurable = Configuration.from_runnable_config(config)
    user_config = state.get("user_config") or {}
    web_search_model = (user_config.gemini_base_model if user_config and user_config.gemini_base_model is not None 
        else configurable.query_generator_model
    )
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )
    # Uses the google genai client as the langchain client doesn't return grounding metadata
    response = genai_client.models.generate_content(
        model=web_search_model,
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
    logger.info("REFLECTING ON RESEARCH RESULTS...")

    configurable = Configuration.from_runnable_config(config)
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    user_config = state.get("user_config") or {}
    reasoning_model = (user_config.gemini_reasoning_model if user_config and user_config.gemini_reasoning_model is not None 
        else configurable.reasoning_model
    )

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
    # logger.info("----EVALUATING RESEARCH----\n")
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        logger.info(ctext("Research is sufficient, finalizing answer...", color='white'))
        return "finalize_answer"
    else:
        logger.info(ctext("Research is not sufficient, continuing...", color='white'))
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
    configurable = Configuration.from_runnable_config(config)
    user_config = state.get("user_config") or {}
    reasoning_model = (user_config.gemini_reasoning_model if user_config and user_config.gemini_reasoning_model is not None 
        else configurable.reasoning_model
    )

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
        
    logger.info(f"DEEP RESEARCH REPORT COMPLETED:\n{ctext(response.split('\n')[0], color='white', italic=True)}\n...\n{ctext(response.split('\n')[-1], color='white', italic=True)}\n")
    
    return {
        "final_deep_research_report": response,
        "sources_gathered": unique_sources
    } 

