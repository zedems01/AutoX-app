from trend_harvester import trend_harvester_node
from tweet_search_agent import tweet_search_node
from opinion_analysis_agent import opinion_analysis_node
from writer_agent import writer_node
from quality_assurance_agent import quality_assurance_node
from image_generator_agent import image_generator_node
from publicator_agent import publicator_node
from deep_researcher import (
    generate_query,
    continue_to_web_research,
    web_research,
    reflection,
    evaluate_research,
    finalize_answer,
)

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .state import OverallState

# Step 3.1.4: Implement explicit HiTL interrupt nodes
def await_topic_selection(state: OverallState) -> dict:
    """Node to await user selection of a topic."""
    state['next_human_input_step'] = "await_topic_selection"
    return {"next_human_input_step": "await_topic_selection"}

def await_content_validation(state: OverallState) -> dict:
    """Node to await user validation of the generated content."""
    state['next_human_input_step'] = "await_content_validation"
    return {"next_human_input_step": "await_content_validation"}

def await_image_validation(state: OverallState) -> dict:
    """Node to await user validation of the generated images."""
    state['next_human_input_step'] = "await_image_validation"
    return {"next_human_input_step": "await_image_validation"}

# Step 3.1.2: Initialize the StateGraph
workflow = StateGraph(OverallState)
memory = MemorySaver()

# Add nodes to the graph
workflow.add_node("trend_harvester", trend_harvester_node)
workflow.add_node("tweet_searcher", tweet_search_node)
workflow.add_node("opinion_analyzer", opinion_analysis_node)
workflow.add_node("deep_research_query_generator", generate_query)
workflow.add_node("deep_research_web_searcher", web_research)
workflow.add_node("deep_research_reflector", reflection)
workflow.add_node("deep_research_finalizer", finalize_answer)
workflow.add_node("writer", writer_node)
workflow.add_node("quality_assurer", quality_assurance_node)
workflow.add_node("image_generator", image_generator_node)
workflow.add_node("publicator", publicator_node)

# Add HiTL interrupt nodes
workflow.add_node("await_topic_selection", await_topic_selection)
workflow.add_node("await_content_validation", await_content_validation)
workflow.add_node("await_image_validation", await_image_validation)

# Set interrupt points for HiTL
workflow.interrupt = ["await_topic_selection", "await_content_validation", "await_image_validation"]


