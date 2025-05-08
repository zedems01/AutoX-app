from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .agents import web_scraping_agent, web_search_agent, trends_analyst_agent, writer_agent
from .agents.web_scraping_agent import web_scraping_agent, complete_auto_node
from .agents.web_search_agent import web_search_agent
from .agents.trends_analyst_agent import trends_analyst_agent
from .agents.writer_agent import writer_agent
from .agents.human_feedback_nodes import trend_feedback_node, tweet_validation_node
from .agents.publication_node import publication_node

from .tools.utils import WorkflowState, print_stream, router_trend_choice, router_tweet_validation



if __name__ == "__main__":
    # --- Defining the overall graph structure: (nodes, edges, relations) ---
    workflow = StateGraph(WorkflowState)
    workflow.add_node("auto_level", complete_auto_node)
    workflow.add_node("scraper", web_scraping_agent)
    workflow.add_node("web_agent", web_search_agent)
    workflow.add_node("trends_analyst", trends_analyst_agent)
    workflow.add_node("trend_feedback_node", trend_feedback_node)
    workflow.add_node("writer", writer_agent)
    workflow.add_node("tweet_feedback_node", tweet_validation_node)
    workflow.add_node("publication_node", publication_node)

    workflow.add_edge(START, "auto_level")
    workflow.add_edge("auto_level", "scraper")
    workflow.add_edge("scraper", "web_agent")
    workflow.add_edge("web_agent", "trends_analyst")
    workflow.add_conditional_edges("trends_analyst", router_trend_choice)
    # workflow.add_edge("trend_feedback_node", "writer")
    # workflow.add_edge("trend_feedback_node", "scraper")
    workflow.add_conditional_edges("writer", router_tweet_validation)
    # workflow.add_edge("tweet_feedback_node", "writer")
    # workflow.add_edge("tweet_feedback_node", "publication_node")
    workflow.add_edge("publication_node", END)

    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    initial_input = {"messages": [("human", "Top 3 trending topics in France")]}
    thread = {"configurable": {"thread_id": "1"}}

    print_stream(graph.stream(initial_input, config=thread, stream_mode="values"))