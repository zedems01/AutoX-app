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


class GeneratedImage(BaseModel):
    """
    Represents a generated image with its metadata.
    """
    image_name: str
    local_file_path: str
    s3_url: str


class Trend(BaseModel):
    """
    Represents a trending topic on X.
    """
    name: str = Field(description="The name of the trend.")
    rank: Optional[int] = Field(description="The rank of the trend.")
    tweet_count: Optional[str] = Field(description="The number of tweets associated with the trend.")

class TrendResponse(BaseModel):
    """
    Represents a response from the trend harvester agent.
    """
    trends: List[Trend]


class TweetAuthor(BaseModel):
    """
    Represents a tweet author.
    """
    userName: str
    name: str
    isVerified: bool
    followers: int
    following: int

class TweetSearched(BaseModel):
    """
    Represents a single tweet searched.
    """
    text: str
    source: str
    retweetCount: int
    replyCount: int
    likeCount: int
    quoteCount: int
    viewCount: int
    createdAt: str
    lang: str
    isReply: bool
    author: TweetAuthor

class TweetSearchResponse(BaseModel):
    """
    Represents a response from the tweet search agent.
    """
    tweets: List[TweetSearched]

class TweetDrafts(BaseModel):
    """
    A list of tweet drafts, intended to be posted as a thread.
    """
    drafts: List[str]


class TweetAdvancedSearchParameters(BaseModel):
    """
    Parameters for the tweet_advanced_search tool.
    """
    query: str = Field(..., description="The search query for tweets, including any operators.")
    query_type: str = Field("Latest", description="Type of search. Can be 'Latest' or 'Top'.")


class OpinionAnalysisOutput(BaseModel):
    """
    Schema for the output of the opinion analysis agent.
    """
    opinion_summary: str = Field(..., description="A concise summary of the public's opinion, viewpoints, and discussions found in the tweets.")
    overall_sentiment: str = Field(..., description="The overall sentiment of the conversation (e.g., 'Positive', 'Negative', 'Neutral', 'Mixed').")
    topic_from_opinion_analysis: str = Field(..., description="The specific, refined topic or subject of the conversation, suitable for deep research.")


