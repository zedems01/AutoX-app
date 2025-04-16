from pydantic import BaseModel, Field
from typing import List

from langchain_community.tools.tavily_search import TavilySearchResults





class NewsResponse(BaseModel):
    "Schema for web news extraction."
    subject: str = Field(description="The subject of the news.")
    content: str = Field(description="The content of the news.")

class WebResponse(BaseModel):
    "Response schema for the web search agent."
    news: List[NewsResponse] = Field(description="The news articles extracted from the web.")



TAVILY_TOOL = TavilySearchResults(max_results=2)
