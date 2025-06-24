from .trend_harvester import trend_harvester_node
from .tweet_search import tweet_search_node
from .opinion_analysis import opinion_analysis_node
from .writer import writer_node
from .quality_assurance import quality_assurance_node
from .image_generator import image_generator_node
from .publicator import publicator_node
from .deep_research_nodes import (
    generate_query,
    continue_to_web_research,
    web_research,
    reflection,
    evaluate_research,
    finalize_answer,
)

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import OverallState


def await_topic_selection(state: OverallState) -> dict:
    """Node to await user selection of a topic."""
    return {
        "next_human_input_step": "await_topic_selection",
    }

def await_content_validation(state: OverallState) -> dict:
    """Node to await user validation of the generated content."""
    return {
        "next_human_input_step": "await_content_validation",
    }

def await_image_validation(state: OverallState) -> dict:
    """Node to await user validation of the generated images."""
    return {
        "next_human_input_step": "await_image_validation",
    }

def auto_select_topic(state: OverallState) -> dict:
    """Node to automatically select the top trending topic in autonomous mode."""
    if state.get("trending_topics"):
        selected_topic = state["trending_topics"][0]
        return {"selected_topic": selected_topic}
    return {}

# --- Conditional routing functions ---

def initial_routing(state: OverallState) -> str:
    """Determines the entry point of the workflow based on user input."""
    if state.get("has_user_provided_topic"):
        return "tweet_searcher"
    return "trend_harvester"

def route_after_trend_harvester(state: OverallState) -> str:
    """Routes after fetching trends based on automation mode."""
    if state.get("is_autonomous_mode"):
        return "auto_select_topic"
    return "await_topic_selection"

def route_after_qa(state: OverallState) -> str:
    """Routes after quality assurance based on automation mode and image prompt availability."""
    if not state.get("is_autonomous_mode"):
        return "await_content_validation"
    
    if state.get("final_image_prompts"):
        return "image_generator"
    return "publicator"

def route_after_image_generation(state: OverallState) -> str:
    """Routes after image generation based on automation mode and image availability."""
    if state.get("is_autonomous_mode") or not state.get("generated_images"):
        return "publicator"
    
    return "await_image_validation"

def route_after_validation(state: OverallState) -> str:
    """Routes after a user validation step, potentially looping back for revisions."""
    validation_result = state.get("validation_result") or {}
    action = validation_result.get("action", "approve")
    # The step that was validated is now stored in the validation_result
    last_step = validation_result.get("validated_step")

    if action == "reject":
        if last_step == "await_content_validation":
            return "writer"
        if last_step == "await_image_validation":
            return "image_generator"
    
    # Default to approve/edit and continue
    if last_step == "await_topic_selection":
        return "tweet_searcher"
    if last_step == "await_content_validation":
        if state.get("final_image_prompts"):
            return "image_generator"
        return "publicator"
    if last_step == "await_image_validation":
        return "publicator"

    return "END"


# Initialize the StateGraph
workflow = StateGraph(OverallState)
memory = MemorySaver()

workflow.add_node("trend_harvester", trend_harvester_node)
workflow.add_node("tweet_searcher", tweet_search_node)
workflow.add_node("opinion_analyzer", opinion_analysis_node)
workflow.add_node("query_generator", generate_query)
workflow.add_node("web_research", web_research)
workflow.add_node("reflection", reflection)
workflow.add_node("finalize_answer", finalize_answer)
workflow.add_node("writer", writer_node)
workflow.add_node("quality_assurer", quality_assurance_node)
workflow.add_node("image_generator", image_generator_node)
workflow.add_node("publicator", publicator_node)

# HiTL interrupt nodes
workflow.add_node("await_topic_selection", await_topic_selection)
workflow.add_node("await_content_validation", await_content_validation)
workflow.add_node("await_image_validation", await_image_validation)

# Autonomous node
workflow.add_node("auto_select_topic", auto_select_topic)


# Workflow Edges & Routing
workflow.set_conditional_entry_point(initial_routing)

workflow.add_conditional_edges("trend_harvester", route_after_trend_harvester)
workflow.add_edge("auto_select_topic", "tweet_searcher")

# Continuation from the HiTL topic selection
workflow.add_conditional_edges(
    "await_topic_selection", 
    route_after_validation, 
    {"tweet_searcher": "tweet_searcher"}
)

workflow.add_edge("tweet_searcher", "opinion_analyzer")
workflow.add_edge("opinion_analyzer", "query_generator")

# Deep Research Sub-Graph
workflow.add_conditional_edges(
    "query_generator", continue_to_web_research, ["web_research"]
)

workflow.add_edge("web_research", "reflection")
workflow.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)

workflow.add_edge("finalize_answer", "writer")

workflow.add_edge("writer", "quality_assurer")
workflow.add_conditional_edges("quality_assurer", route_after_qa)

# Continuation from the HiTL content validation
workflow.add_conditional_edges(
    "await_content_validation",
    route_after_validation,
    {"writer": "writer", "image_generator": "image_generator", "publicator": "publicator"},
)

workflow.add_conditional_edges("image_generator", route_after_image_generation)

# Continuation from the HiTL image validation
workflow.add_conditional_edges(
    "await_image_validation",
    route_after_validation,
    {"image_generator": "image_generator", "publicator": "publicator"},
)

workflow.add_edge("publicator", END)


graph = workflow.compile(
    checkpointer=memory,
    interrupt_after=[
        "await_topic_selection",
        "await_content_validation",
        "await_image_validation",
    ],
)



