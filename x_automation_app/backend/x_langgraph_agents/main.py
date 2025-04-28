from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .agents import web_scraping_agent, web_search_agent, trends_analyst_agent, writer_agent
from .agents.web_scraping_agent import web_scraping_agent
from .agents.web_search_agent import web_search_agent
from .agents.trends_analyst_agent import trends_analyst_agent
from .agents.writer_agent import writer_agent
from .agents.human_feedback_nodes import topic_choice_node, publication_node

from .tools.utils import WorkflowState, print_stream



if __name__ == "__main__":
    # --- Defining the overall graph structure: (nodes, edges, relations) ---
    workflow = StateGraph(WorkflowState)

    workflow.add_node("web_scraper", web_scraping_agent)
    workflow.add_node("web_searcher", web_search_agent)
    workflow.add_node("trends_analyst", trends_analyst_agent)
    workflow.add_node("topic_validation", topic_choice_node)
    workflow.add_node("writer", writer_agent)
    workflow.add_node("publish", publication_node)

    workflow.add_edge(START, "web_scraper")
    workflow.add_edge("web_scraper", "web_searcher")
    workflow.add_edge("web_searcher", "trends_analyst")
    workflow.add_edge("trends_analyst", "topic_validation")
    workflow.add_edge("topic_validation", "writer")
    workflow.add_edge("writer", "publish")
    workflow.add_edge("publish", END)


    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    initial_input = {"messages": [("human", "Top 3 trendy topics in France")]}
    thread = {"configurable": {"thread_id": "1"}}

    print_stream(graph.stream(initial_input, config=thread, stream_mode="values"))