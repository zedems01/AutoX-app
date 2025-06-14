from typing import List, Optional
from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="A list of search queries to be used for web research."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )


class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    follow_up_queries: List[str] = Field(
        description="A list of follow-up queries to address the knowledge gap."
    )


class SearchResult(BaseModel):
    """A search result from a web search."""
    is_last_search: bool = Field(
        description="A boolean flag to indicate if this is the last search result."
    )


class TweetDraft(BaseModel):
    """Represents a single generated tweet draft."""
    text: str = Field(description="The full text of the tweet, under 280 characters.")
    image_prompt: Optional[str] = Field(description="A concise, descriptive prompt for an AI image generator, or null if no image is needed.")


class TweetDrafts(BaseModel):
    """A list of generated tweet drafts."""
    drafts: List[TweetDraft]


class FinalTweet(BaseModel):
    """Represents the final, selected tweet and image prompt after quality assurance."""
    final_tweet: str = Field(description="The text of the single best tweet, selected and refined.")
    final_image_prompt: Optional[str] = Field(description="The finalized, high-quality image prompt, or null if no image is needed.")
