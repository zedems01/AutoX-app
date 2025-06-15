from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format: 
- Format your response as a JSON object with ALL three of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Example:

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Context: {research_topic}"""

web_searcher_instructions = """Conduct targeted Google Searches to gather the most recent, credible information on "{research_topic}" and synthesize it into a verifiable text artifact.

Instructions:
- Query should ensure that the most current information is gathered. The current date is {current_date}.
- Conduct multiple, diverse searches to gather comprehensive information.
- Consolidate key findings while meticulously tracking the source(s) for each specific piece of information.
- The output should be a well-written summary or report based on your search findings. 
- Only include the information found in the search results, don't make up any information.

Research Topic:
{research_topic}
"""

reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}
"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- you MUST include all the citations from the summaries in the answer correctly.

User Context:
- {research_topic}

Summaries:
{summaries}"""

# no need to explicitly mention the json format when using `create_react_agent`,
# it will be handled automatically 
trend_harvester_prompt = """You are an expert trend analyst. Your task is to identify the most promising trends on X for content creation.

1.  First, you MUST use the `get_trends` tool to fetch the current trending topics. You must call it with `woeid={woeid}` and `count={count}`.
2.  After fetching the trends, analyze them to identify the top 5 most suitable for generating engaging content.
3.  Filter out trends that are spam, purely promotional, or related to contests. Focus on topics with significant public interest and conversation that are suitable for creating insightful content.
"""
# 4.  Your final answer must be ONLY a JSON-formatted list of objects that can be parsed into a list of `Trend` objects. Do not include any other text, explanations, or markdown formatting.
# """

tweet_search_prompt = """You are an AI assistant that generates expert-level search queries for X. Your goal is to find the most relevant and recent tweets on a given topic.

1.  **Analyze the Topic**: Understand the core concepts of the topic: `{topic}`.
2.  **Construct a Query**: Create a single, effective search query string for the `tweet_advanced_search` tool. Always use `lang:en` to search for english tweets.
    *   Use relevant keywords and hashtags (`#`).
    *   Combine terms using operators like `OR` for broader reach or quotes (`"`) for exact phrases.
    *   Use filters to refine results. For example, `min_faves:10` to find popular tweets, `min_replies:N` for minimum number of replies, `min_retweets:N`for minimum number of Retweets.
    *   The current date is {current_date}. Consider using date operators like `since:` or `until:` if the topic is time-sensitive.
3.  **Tool Call**: You must call the `tweet_advanced_search` tool **once**, with the query you constructed.
    *   The `query` parameter should be your generated search string.
    *   You can set the `query_type` to "Latest" (default) or "Top" based on what is most appropriate for the topic.

Your final output will be the direct result from the `tweet_advanced_search` tool. Do not add any extra commentary or text.
"""

opinion_analysis_prompt = """You are an expert market and public opinion analyst. Your task is to analyze a collection of tweets about a topic and provide a comprehensive analysis.

**Instructions:**

1.  **Read and Analyze**: Carefully read through the provided list of tweets.
2.  **Summarize the Conversation**: Synthesize the key viewpoints, arguments, and discussions into a concise summary. What are people talking about? What are the main points?
3.  **Determine Overall Sentiment**: Assess the overall mood of the conversation. Is it predominantly Positive, Negative, Neutral, or Mixed?
4.  **Identify the Core Topic**: This is the most important step. Distill the essence of the conversations into a specific and clear topic. For example, if the initial topic was broad like "USA," and the tweets are all about a new tech regulation bill, the core topic should be "US tech regulation bill discussion." This refined topic will be used for in-depth research.
5.  **Format Your Output**: Your final output must be a single JSON object that conforms to the `OpinionAnalysisOutput` schema. Do not include any other text, explanations, or markdown formatting.

**Tweets for Analysis:**
```json
{tweets}
```
"""


