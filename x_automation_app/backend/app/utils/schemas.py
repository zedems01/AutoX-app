from typing import List, Optional, Dict, Any, TypedDict
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class UserDetails(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None

class ValidationAction(str, Enum):
    """Enumeration for validation actions."""
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"

class ValidationData(BaseModel):
    """
    Data payload for validation, which can contain feedback or other information.
    """
    feedback: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    """
    Defines the structure for the result of a human-in-the-loop validation step.
    """
    action: ValidationAction
    data: Optional[ValidationData] = None


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
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_generated: bool
    image_name: str
    local_file_path: str
    s3_url: str


class ImageGeneratorOutput(BaseModel):
    """
    Represents the output of the image generator agent.
    """
    images: List[GeneratedImage]


class Trend(BaseModel):
    """
    Represents a trending topic on X.
    """
    name: str = Field(description="The name of the trend.")
    rank: Optional[int] = Field(default=None, description="The rank of the trend.")
    tweet_count: Optional[str] = Field(default=None, description="The number of tweets associated with the trend.")

class TrendResponse(BaseModel):
    """
    Represents a response from the trend harvester agent.
    """
    trends: List[Trend]

class TweetQuery(BaseModel):
    """
    Represents a tweet query.
    """
    query: str


class TweetAuthor(BaseModel):
    """
    Represents a tweet author.
    """
    userName: str
    name: str
    # isVerified: bool
    # followers: int
    # following: int

class TweetSearched(BaseModel):
    """
    Represents a single tweet searched.
    """
    text: str
    # source: str
    retweetCount: int
    replyCount: int
    likeCount: int
    # quoteCount: int
    viewCount: int
    createdAt: str
    # lang: str
    # isReply: bool
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


class TweetChunk(BaseModel):
    """
    Represents a single tweet within a thread.
    """
    text: str = Field(..., description="The content of the tweet chunk.")
    image_path: Optional[str] = Field(None, description="The local path to an image to be attached to this specific tweet.")

class ThreadPlan(BaseModel):
    """
    Represents the entire thread structure as planned by the agent.
    """
    thread: List[TweetChunk] = Field(..., description="A list of TweetChunk objects, in the order they should be posted.")


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


class WriterOutput(BaseModel):
    """
    Schema for the output of the writer agent.
    """
    content_draft: str = Field(..., description="The main content draft, written according to the specified parameters.")
    image_prompts: list[str] = Field(..., description="A list of one or more descriptive prompts for generating accompanying images.")


class QAOutput(BaseModel):
    """
    Schema for the output of the quality assurance agent.
    """
    final_content: str = Field(..., description="The final, approved version of the content, ready for publication.")
    final_image_prompts: list[str] = Field(..., description="The final, approved list of image prompts.")


class UserConfigSchema(BaseModel):
    """
    Schema for user-configurable workflow parameters, overriding default environment settings.
    """
    gemini_model: Optional[str] = Field(None, description="Preferred Gemini model if used.")
    openai_model: Optional[str] = Field(None, description="Preferred OpenAI model if used.")
    openrouter_model: Optional[str] = Field(None, description="Preferred OpenRouter model.")
    trends_count: Optional[int] = Field(None, description="Number of trends to fetch.")
    trends_woeid: Optional[int] = Field(None, description="Where On Earth ID for trend fetching.")
    max_tweets_to_retrieve: Optional[int] = Field(None, description="Maximum number of tweets to retrieve in search.")
    tweets_language: Optional[str] = Field(None, description="Language for tweet search results.")
    content_language: Optional[str] = Field(None, description="Language for generated content.")


