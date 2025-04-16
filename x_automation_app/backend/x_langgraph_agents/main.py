from langgraph.graph import StateGraph, START, END

from .agents import web_scraping_agent, web_search_agent, trends_analyst_agent, writer_agent, publication_node
from .tools.utils import WorkflowState



# --- Defining the overall graph structure: (nodes, edges, relations) ---
workflow = StateGraph(WorkflowState)

workflow.add_node("web_scraper", web_scraping_agent)
workflow.add_node("web_searcher", web_search_agent)
workflow.add_node("trends_analyst", trends_analyst_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("publish", publication_node)

workflow.add_edge(START, "web_scraper")
workflow.add_edge("web_scraper", "web_searcher")
workflow.add_edge("web_searcher", "trends_analyst")
workflow.add_edge("trends_analyst", "writer")
workflow.add_edge("writer", "publish")
workflow.add_edge("publish", END)

graph = workflow.compile()