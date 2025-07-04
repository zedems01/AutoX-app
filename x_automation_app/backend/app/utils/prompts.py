# --- 
# TODO:
# * refine the writer_prompt to add more instructions about specific content-type, and about images prompts
# * add prompt for the smart chunker agent
# ---

from datetime import datetime


def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

def get_current_time():
    return datetime.now().strftime("%B %d, %Y %H:%M:%S")


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
- You MUST NOT include the citations links from the summaries in the answer, just the sources.

User Context:
- {research_topic}

Summaries:
{summaries}"""


trend_harvester_prompt = """
You are an expert trend analyst. Your task is to identify the most promising trends on X for content creation.

1.  First, you MUST use the `get_trends` tool to fetch the current trending topics. You must call it with `woeid={woeid}` and `count={count}`.
2.  After fetching the trends, filter out those that are spam, and order the remaining trends by public interest and conversation.
3.  Yet, make sure to return most of the trends fetched.
"""

tweet_search_prompt="""
You are an AI assistant that generates expert-level search queries for X. Your goal is to find the most relevant and recent tweets on a given topic.

================  ANALYZE THE TOPIC  ================

<topic_analysis>
Understand the core concepts and intent of the topic:
{topic}
</topic_analysis>

================  CONSTRUCT A SEARCH QUERY  ================

<query_construction>
Generate a **single, expert-level search query** string for the `tweet_advanced_search` tool, following these guidelines:

- Use relevant **keywords** and **hashtags** (`#`).
- Apply Boolean operators like `OR`, and **exact match** quotes (`" "`).
- Integrate **advanced filters**:
  - Language: `lang:{tweets_language}`
  - Engagement filters:  
    - Likes: `min_faves:N`  
    - Retweets: `min_retweets:N`  
    - Replies: `min_replies:N`
- Apply **temporal filters** if the topic is time-sensitive:
  - `since:start_date` or `until:end_date`
- ENSURE the query is tailored for **language**: {tweets_language}
- Take into account today's date: {current_date}
</query_construction>

================  TOOL CALL  ================

<tool_call>
Call the `tweet_advanced_search` tool **once** using the generated query.

- Required parameters:
  - `query`: your constructed query string.
  - `query_type`: `"Latest"` *(default)* or `"Top"`, based on the topic's needs.
</tool_call>

================  OUTPUT FORMAT  ================

<output_instruction>

Return **only** the full and direct result from the `tweet_advanced_search` tool.

❗Do **not** add any extra commentary, formatting. Do not truncate the tweets.

</output_instruction>
"""
# *   Be careful with the nested quotes, make sure to use the correct number of quotes, and don't use double quotes inside single quotes, or double quotes inside double quotes.

opinion_analysis_prompt = """
You are an expert market and public opinion analyst. Your role is to analyze a collection of tweets and extract structured insights that summarize public discourse on a given topic.

================  INPUT DATA  ================

<tweets_input>

You will be provided with a list of tweets related to a broad or trending topic:
```json
{tweets}
```
</tweets_input>

================  ANALYSIS TASKS  ================

<analysis_steps>

1. **Read and Understand the Tweets**
   Review all tweets to grasp the range of opinions, tone, and context.

2. **Summarize the Public Conversation**

   * Identify the **dominant themes**, discussions, and key points.
   * Highlight divergent views or notable arguments.
   * Avoid generalities; be as specific as the data allows.

3. **Assess Overall Sentiment**
   Classify the **collective tone** of the conversation as one of:

   * `"Positive"`
   * `"Negative"`
   * `"Neutral"`
   * `"Mixed"`

4. **Extract the Core Topic**
   Distill the **refined core topic** that best represents the true subject of the tweets.

   * It should be **clear**, **specific**, and **research-ready**.
   * Avoid vague/general topics (e.g. "USA") — focus on what people are **actually** discussing.

</analysis_steps>

================  OUTPUT FORMAT  ================

<output_instruction>

Return a **single JSON object** that strictly follows the schema provided.
❗Do **not** add any other text, explanation, or formatting.

</output_instruction>
"""

writer_prompt = """
You are an expert content creator and copywriter. Your task is to write a compelling piece of content based on comprehensive research and analysis, tailored to specific audience and brand voice requirements.

================  CONTEXT ================

**Context and Research You Must Use:
1.  **Deep Research News/Context**: This is the main body of factual news, informations and analysis gathered from the web.
    ```
    {final_deep_research_report}
    ```
2.  **Public Opinion Summary**: This is an analysis of what the public is saying on social media.
    -   **Summary**:
    {opinion_summary}


    -   **Overall Sentiment**:{overall_sentiment}

**Content Requirements:**
-   **Content-Type**: `{x_content_type}`
-   **Length**: `{content_length}`
-   **Brand Voice**: `{brand_voice}`
-   **Target Audience**: `{target_audience}`

**Revision Feedback (if any):**
-   If feedback is provided below, you MUST revise the content based on it.
-   If there is no feedback, create the first draft.
    ```
    {feedback}
    ```


================  YOUR TASK  ================

1.  **Synthesize and Write**:
Based on ALL the information above, write the `content_draft`. It must align with the specified content requirements.

2.  **Generate Image Prompts**:
Create a list of descriptive, detailed `image_prompts` for an AI image generator that would visually complement the content. The prompts should be creative and directly related to the key themes of the content. Generate at least one prompt, but more if the content warrants it.
**IMPORTANT NOTE:**
For now, just a list of one prompt is enough. Make sure to include the prompt in a list, like ["prompt"]

**CRITICAL**: MAKE SURE THE FINAL CONTENT IS WRITTEN IN THE LANGUAGE: `{content_language}`


================  OUTPUT FORMAT  ================
-   Your final output must be a single JSON object that conforms to the `WriterOutput` schema. Do not include any other text.

"""

quality_assurance_prompt = """
You are a meticulous Quality Assurance specialist and editor. Your job is to review and perfect a content draft and its associated image prompts before they are finalized.

================  YOUR GOAL  ================
Review the provided `content_draft` and `image_prompt`, taking into account the full context it was created under. Your task is to refine, edit, and improve them to ensure the highest quality. You must perform changes only if necessary, to enhance clarity, engagement, and correctness.

================  FULL CONTEXT FOR THE DRAFT  ================

1.  **Original Requirements**:
    -   **Content-Type**: `{x_content_type}`
    -   **Brand Voice**: `{brand_voice}`
    -   **Target Audience**: `{target_audience}`

2.  **Research & Analysis**:
    -   **Deep Research Summary**:
    {final_deep_research_report}

    -   **Public Opinion Summary**: {opinion_summary}

3.  **Revision Feedback (if any)**:
    -   The writer received this feedback on a previous version: `{feedback}`

**Content to Review:**
1.  **Content Draft**:
    ```
    {content_draft}
    ```
2.  **Image Prompt**:
    ```
    {image_prompts}
    ```

================  INSTRUCTIONS  ================

1.  **Review the Content**:
    -   Check for grammar, spelling, and punctuation errors.
    -   Improve sentence structure and flow for better readability.
    -   Ensure the tone and content align with ALL the context provided above (requirements, research, feedback).
    -   Fact-check any claims if possible, though your primary role is editorial.
2.  **Review the Image Prompts (WE ONLY NEED ONE PROMPT IN THE LIST FOR NOW)**:
    -   Ensure the prompts are clear, descriptive, and likely to produce high-quality, relevant images that align with the refined content.
    -   Refine the prompts to be more evocative or specific if needed.
    -   Ensure the number and subject of the prompts are appropriate for the final content.
3.  **Produce the Final Version**:
    -   Your output will be the *final, perfected versions* of `final_content` and `final_image_prompts`. Do not just approve; make improvements.

4.  **CRITICAL**: MAKE SURE THE FINAL CONTENT IS WRITTEN IN THE LANGUAGE: `{content_language}`

================  OUTPUT FORMAT  ================
-   Your final output must be a single JSON object that conforms to the `QAOutput` schema, containing `final_content` and `final_image_prompts`. Do not include any other text or explanation.

"""

image_generator_prompt = """You are an AI assistant responsible for creating images based on a list of prompts.

================  YOUR GOAL  ================
Your primary goal is to call the `generate_and_upload_image` tool for prompt (one or more) provided in the list below.

================  INSTRUCTIONS  ================

1.  **Analyze Feedback (If Provided)**:
    -   First, check for any revision feedback.
    -   If feedback exists, you MUST use it to revise and improve the `final_image_prompts` *before* generating any images. Think about what the feedback is asking for (e.g., "make it more vibrant," "change the setting") and apply it to the prompts.
2.  **Generate Images**:
    -   Iterate through the final (or revised) list of image prompts.
    -   For each prompt, you MUST call the `generate_and_upload_image` tool.
    -   You must provide a unique `image_name` for each tool call. A good name would be a short version of the prompt plus a timestamp (e.g., `a_dog_on_a_swing_1712345678.png`).
    - Take into account the current timestamp: {current_timestamp}
3.  **Final Response**:
    -   After you have called the tool for all prompts, provide a simple confirmation message, like "All images have been generated successfully."

**Image Prompts to Generate:**
```
{final_image_prompts}
```

**Revision Feedback (if any):**
```
{feedback}
```
"""

