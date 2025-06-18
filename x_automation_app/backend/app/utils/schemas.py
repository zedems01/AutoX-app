from typing import List, Optional, Dict, Any, TypedDict
from pydantic import BaseModel, Field
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
    # Allows for other potential data fields during validation
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
    image_name: str
    local_file_path: str
    s3_url: str

    class Config:
        arbitrary_types_allowed = True

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


class WriterOutput(BaseModel):
    """
    Schema for the output of the writer agent.
    """
    content_draft: str = Field(..., description="The main content draft, written according to the specified parameters.")
    image_prompts: list[str] = Field(..., description="A list of descriptive prompts for generating accompanying images.")


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
    gemini_base_model: Optional[str] = Field(..., description="Preferred Gemini base model for general tasks.")
    gemini_reasoning_model: Optional[str] = Field(..., description="Preferred Gemini reasoning model for complex tasks.")
    openai_model: Optional[str] = Field(..., description="Preferred OpenAI model if used.")
    trends_count: Optional[int] = Field(..., description="Number of trends to fetch.")
    trends_woeid: Optional[int] = Field(..., description="Where On Earth ID for trend fetching.")
    max_tweets_to_retrieve: Optional[int] = Field(..., description="Maximum number of tweets to retrieve in search.")
    tweets_language: Optional[str] = Field(..., description="Language for tweet search results.")
    content_language: Optional[str] = Field(..., description="Language for generated content.")


# class OverallState(TypedDict):
#     # From login
#     login_data: Optional[str]
#     # State management
#     messages: List
#     validation_result: Optional[ValidationResult]
#     current_step: str
#     source_step: Optional[str]
#     next_human_input_step: Optional[
#         "await_2fa_code" | "await_topic_selection" | "await_content_validation" | "await_image_validation" | None
#     ]
#     error_message: Optional[str]

