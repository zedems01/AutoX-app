# Implementation Plan: AI Agent System for Content Generation & Publishing

This document outlines the step-by-step implementation plan for the new project, focusing on dynamic content generation, flexible publishing options, and robust Human-in-the-Loop (HiTL) capabilities. The entire backend will reside in the `x_automation_app/backend/new_app` directory.

---

## **Project Goal**

The system's primary goal is to generate various content types (articles, tweets, etc.) on a specific topic.

## **User Inputs & Workflow Configuration**

At the input stage, the user will configure the workflow via the frontend. These settings will be stored and passed through the `OverallState` to guide agent behavior.

*   **Automation Mode:** `is_autonomous_mode` (Boolean: `True` for full automation, `False` for HiTL).
*   **Output Destination:** `output_destination` (Enum: `PUBLISH_X`, `GET_OUTPUTS`).
*   **Topic Provision:** `has_user_provided_topic` (Boolean).
*   **Content Type & Parameters (if `output_destination` is `PUBLISH_X`):**
    *   `x_content_type` (Enum: `TWEET_THREAD`, `SINGLE_TWEET`)
    *   `content_length` (e.g., Enum: `SHORT`, `MEDIUM`, `LONG` or character count target)
    *   `brand_voice` (e.g., "professional and authoritative", "humorous and irreverent", "friendly and approachable")
    *   `target_audience` (e.g., "tech enthusiasts", "general public", "investors", "students")
*   **Dynamic Configuration (stored as environment variables and user-configurable):**
    *   `TRENDS_WOEID`
    *   `TRENDS_COUNT`
    *   API Keys (X, OpenAI/Gemini, Composio, AWS S3)
    *   User Credentials (Email, Password, Proxy for X login)

## **Workflow Overview (4 Scenarios)**

The system supports four distinct workflows based on user input:

*   **I. HiTL + User Provides Topic:**
    1.  Topic received.
    2.  **Tweet Search Agent** (LLM-driven search query generation and pagination for fetching tweets on X).
    3.  Opinion Analysis Agent (assesses public opinion, extracts summary, sentiment, subject/topic).
    4.  Deep Research Agents (set of nodes for news and information search, using topic from Opinion Analysis or user-provided one).
    5.  Writer (writes content and image prompts).
    6.  Quality Assurance (checks, validates, and refines Writer's output).
    7.  HiTL 1 (User reviews content/prompts, validates or provides feedback for revision back to Writer).
    8.  **Image Generator** (LLM-driven image generation and iterative refinement based on prompts).
    9.  HiTL 2 (User reviews images, validates or provides feedback for regeneration back to Image Generator).
    10. Publicator (Conditional: if `GET_OUTPUTS`, returns Markdown; if `PUBLISH_X`, chunks content into threads/single tweets and posts to X).

*   **II. HiTL + User Does NOT Provide Topic:**
    1.  **Trend Harvester** (LLM-driven trend fetching and selection from X).
    2.  HiTL 0 (Present trending topics to user for selection).
    3.  **Tweet Search Agent** (LLM-driven search query generation and pagination for fetching tweets on X).
    4.  ... Rest proceeds as in Workflow I.

*   **III. Autonomous + User Provides Topic:**
    1.  Same as Workflow I, but all HiTL steps are skipped. Default actions are taken automatically. This includes:
        *   **Tweet Search Agent** (LLM-driven search query generation and pagination).
        *   **Image Generator** (LLM-driven image generation and refinement).

*   **IV. Autonomous + User Does NOT Provide Topic:**
    1.  **Trend Harvester** (LLM-driven trend fetching and selection from X).
    2.  System automatically selects the top-ranked topic (via autonomous node).
    3.  **Tweet Search Agent** (LLM-driven search query generation and pagination for fetching tweets on X).
    4.  ... Rest proceeds as in Workflow I, skipping HiTL nodes.

---

## **Phase 0: Project Setup & Core Foundation**

This phase establishes the new backend directory, sets up foundational components, and defines the central state.

*   [ ] **Step 0.1: New Backend Directory Setup**
    *   [x] Create the `x_automation_app/backend/new_app` directory.
    *   [x] Create the initial `main.py` for the FastAPI application
    *   [x] Set up basic health check endpoint (`/health`) and CORS configuration in `main.py`.
    *   [x] Copy all files related to the deep research set of agents in `new_app/agents/`. You should review them before continue.

*   [ ] **Step 0.2: Define Global State (`state.py`)**
    *   [x] Create `x_automation_app/backend/new_app/agents/state.py`.
    *   [ ] Complete the `OverallState` TypedDict, which will hold all data relevant to the workflow's progression. This will include:
        *   **Workflow Configuration:** `is_autonomous_mode: bool`, `output_destination: str`, `has_user_provided_topic: bool`, `x_content_type: Optional[str]`, `content_length: Optional[str]`, `content_tone: Optional[str]`.
        *   **Login & Session:** `login_data: Optional[str]`, `session: Optional[str]`, `user_details: Optional[dict]`.
        *   **Content Generation Data:** `trending_topics: List[Trend]`, `selected_topic: Optional[Trend]`, `user_provided_topic: Optional[str]`.
        *   **Advanced Search & Opinion Analysis Output:** `tweet_search_results: Optional[List[dict]]`, `opinion_summary: Optional[str]`, `overall_sentiment: Optional[str]`, `topic_from_opinion_analysis: Optional[str]`.
        *   **Deep Research Output:** `current_context: Optional[str]`, `search_query: Annotated[list, operator.add]`, `web_research_result: Annotated[list, operator.add]`, `sources_gathered: Annotated[list, operator.add]`, `initial_search_query_count: int`, `max_research_loops: int`, `research_loop_count: int`, `reasoning_model: str`.
        *   **Content & Image Drafts:** `content_draft: Optional[str]`, `image_prompts: List[str]`.
        *   **Final Output:** `final_content: Optional[str]`, `final_image_prompts: List[str]`, `generated_images: List[GeneratedImage]`, `publication_id: Optional[str]`.
        *   **HiTL & Meta-state:** `next_human_input_step: Optional[str]`, `validation_result: Optional[dict]`, `current_step: str`, `error_message: Optional[str]`, `messages: Annotated[list, add_messages]`.
    *   [x] Define `Trend` as `Pydantic BaseModel` class within `state.py` or `tools_and_schemas.py`.

*   [ ] **Step 0.3: Shared Tools & Schemas**
    *   [x] Create `x_automation_app/backend/new_app/agents/tools_and_schemas.py`.
    *   [x] Define common **Pydantic BaseModel classes** for structured outputs and tool outputs (e.g., `GeneratedImage`, `TweetDrafts`, TweetSearched, ...) and any shared Langchain tools here.
    *   [x] Define `GeneratedImage` as a `Pydantic BaseModel` with image_name, local_file_path, s3_url.

---

## **Phase 1: Core Service Layer Development**

This phase focuses on implementing the external API interactions, ensuring they are stateless and reusable.

*   [ ] **Step 1.1: Centralized Twitter Service (`twitter_service.py`)**
    *   [x] Create `x_automation_app/backend/new_app/services/twitter_service.py`.
    *   [ ] Refactor the existing `TwitterService` functions to be stateless. All authenticated methods will require `session` as an argument.
    *   [ ] Implement/Update the following functions:
        *   [x] `start_login(email: str, password: str, proxy: str) -> dict`: Executes the first 2FA login step, returns `login_data`.
        *   [x] `complete_login(login_data: str, two_fa_code: str, proxy: str) -> dict`: Executes the second 2FA login step, returns `session` token and `user_details`.
        *   [x] `get_trends(woeid: int, count: int) -> List[Trend]`: Fetches trending topics.
        *   [x] `tweet_advanced_search(query: str, query_type: str = "Latest", cursor: str = "") -> TweetAdvancedSearchResult`: This will fetch tweets related to a given query, supporting pagination (7 queries for ~100 tweets if `has_next_page` still true).
            *   **Endpoint Details:**
                ```python
                url = f"{base_url}/tweet/advanced_search"
                params = {
                    "query": "<string>",     # The query to search for.
                    "queryType": "Latest",  # Available options: Latest, Top
                    "cursor": ""             # The cursor to paginate through the results. First page is "".
                }
                headers = {"X-API-Key": api_key}
                # Response will include "tweets", "has_next_page", "next_cursor"
                ```
            *   **Supported Query Operators:**
                *   **Time:**
                    *   `since:YYYY-MM-DD`: On or after (inclusive) a specified date.
                    *   `until:YYYY-MM-DD`: Before (NOT inclusive) a specified date.
                    *   `since:YYYY-MM-DD_HH:MM:SS_UTC`: On or after (inclusive) a specified date and time in UTC.
                    *   `until:YYYY-MM-DD_HH:MM:SS_UTC`: Before (NOT inclusive) a specified date and time in UTC.
                    *   `since_time:unix_timestamp`: On or after a specified Unix timestamp in seconds.
                    *   `until_time:unix_timestamp`: Before a specified Unix timestamp in seconds.
                    *   `since_id:tweet_id`: After (NOT inclusive) a specified Snowflake ID.
                    *   `max_id:tweet_id`: At or before (inclusive) a specified Snowflake ID.
                    *   `within_time:Nd/Nh/Nm/Ns`: Search within the last N days/hours/minutes/seconds (e.g., `2d`, `3h`, `5m`, `30s`).
                *   **Engagement:**
                    *   `filter:has_engagement`: Has some engagement (replies, likes, retweets).
                    *   `min_retweets:N`: A minimum number of Retweets.
                    *   `min_faves:N`: A minimum number of Likes.
                    *   `min_replies:N`: A minimum number of replies.
                    *   `-min_retweets:N`: A maximum number of Retweets.
                    *   `-min_faves:N`: A maximum number of Likes.
                    *   `-min_replies:N`: A maximum number of replies.

        *   [x] `upload_image(session: str, image_url: str) -> str`: Uploads media from a presigned S3 URL to X, returns `media_id`.
        *   [x] `post_tweet(session: str, tweet_text: str, image_url: Optional[str]=None, in_reply_to_tweet_id: Optional[str]=None) -> str`: Publishes a single tweet and return the tweet ID.
        *   [x] `post_tweet_thread(session: str, tweet_texts: List[str], media_ids_per_tweet: Optional[List[str]] = None)`: Publishes a thread of tweets (implementation details for chunking will come later if `x_content_type` is `TWEET_THREAD`).

*   [ ] **Step 1.2: Image Generation Service (`image_service.py`)**
    *   [x] Create `x_automation_app/backend/new_app/services/image_service.py`.
    *   [x] Implement `generate_and_upload_image(prompt: str, image_name: str) -> GeneratedImage`. This function will:
        *   Generate image using OpenAI gpt-image-1.
        *   Save the image locally (e.g., `x_automation_app/backend/new_app/images/`).
        *   Upload to AWS S3.
        *   Generate a presigned S3 URL.
        *   Return a `GeneratedImage` object including `image_name`, `local_file_path`, and `s3_url`.

*   [ ] **Step 1.3: Notification Service (`notifications.py`)** (WILL BE DONE IN THE NEXT VERSION)
    *   [ ] Create `x_automation_app/backend/new_app/agents/notifications.py`.
    *   [ ] Implement `send_notification(subject: str, body: str)` using Composio Gmail.

---

## **Phase 2: Agent Development & Logic**

This phase involves creating each specialized agent (node) that will form the LangGraph workflow. Each agent will interact with the `OverallState`.

*   [x] **Step 2.1: Trend Harvester Agent (`trend_harvester.py`)**
    *   [x] Create `x_automation_app/backend/new_app/agents/trend_harvester.py`.
    *   [x] This agent will be defined using `langgraph.prebuilt.create_react_agent`.
    *   [x] It will have the `twitter_service.get_trends` function registered as a tool.
    *   [x] Implement `trend_harvester_node(state: OverallState) -> dict`. This node will:
        *   Call the `get_trends` tool.
        *   Use the LLM (configured via `create_react_agent`) to *reason* over the fetched trends and *select* a curated subset of the most promising trends for content generation.
        *   Update `state['trending_topics']` with this curated list.

*   [x] **Step 2.2: Tweet Search Agent (`tweet_search_agent.py`)**
    *   [x] Create `x_automation_app/backend/new_app/agents/tweet_search_agent.py`.
    *   [ ] This agent will be defined using `langgraph.prebuilt.create_react_agent`.
    *   [x] It will have the `twitter_service.tweet_advanced_search` function registered as a tool.
    *   [x] Implement `tweet_search_node(state: OverallState) -> dict`. This node will:
        *   Receive the search topic from `state['selected_topic']['name']` (if HiTL) or `state['topic_from_opinion_analysis']` (if autonomous).
        *   Use the LLM (configured via `create_react_agent`) to generate the `query` parameters for the `tweet_advanced_search` tool, potentially leveraging `queryType` (Latest/Top) and other operators (time, engagement).
        *   Provide a structured output schema for the LLM to ensure the generated parameters are correct.
        *   Execute the `twitter_service.tweet_advanced_search` tool call, handling pagination (making 7 queries or until `has_next_page` is false to collect ~100 tweets).
        *   Update `state['tweet_search_results']` with the collected tweets.

*   [x] **Step 2.3: Opinion Analysis Agent (`opinion_analysis_agent.py`)**
    *   [x] Create `x_automation_app/backend/new_app/agents/opinion_analysis_agent.py`.
    *   [ ] Implement `opinion_analysis_node(state: OverallState) -> dict`. This node will use a direct LLM call (not `create_react_agent`):
        *   Take `state['tweet_search_results']` as input.
        *   Use an LLM to analyze the tweets.
        *   Return `state['opinion_summary']`, `state['overall_sentiment']`, and `state['topic_from_opinion_analysis']`.

*   [ ] **Step 2.4: Deep Research Agents (Consolidated in `deep_researcher.py`)**
    *   [x] Create `x_automation_app/backend/new_app/agents/deep_researcher.py`.
    *   [x] Move and adapt the `generate_query`, `web_research`, `reflection`, `evaluate_research`, and `finalize_answer` nodes into this file. These nodes will use direct LLM calls and programmatic logic, with `web_research` directly calling the Google Search API (not `create_react_agent`).
    *   [ ] Ensure `generate_query` (the entry point for deep research) correctly takes input by **prioritizing `state['topic_from_opinion_analysis']` if it exists, otherwise falling back to `state['user_provided_topic']`**.
    *   [ ] Their output will update `state['final_deep_research_report']` and `state['sources_gathered']`.

*   [ ] **Step 2.5: Writer Agent (`writer_agent.py`)**
    *   [ ] Create `x_automation_app/backend/new_app/agents/writer_agent.py`.
    *   [ ] Implement `writer_node(state: OverallState, feedback: Optional[str] = None) -> dict`. This node will use a direct LLM call (not `create_react_agent`):
        *   Take `state['current_context']`, `state['opinion_summary']`, `state['overall_sentiment']`, workflow parameters (`content_length`, `brand_voice`, `target_audience`, `x_content_type`, etc.), and crucially, `feedback` (if provided from a `HiTL 1` rejection) as input.
        *   The LLM prompt will be specifically designed to **incorporate the `feedback`** when revising the `content_draft` and `image_prompts`.
        *   Use an LLM (e.g., Gemini-Pro) to generate the main content and a *list* of descriptive image prompts.
        *   Return `state['content_draft']` and `state['image_prompts']`.

*   [ ] **Step 2.6: Quality Assurance Agent (`quality_assurance_agent.py`)**
    *   [ ] Create `x_automation_app/backend/new_app/agents/quality_assurance_agent.py`.
    *   [ ] Implement `quality_assurance_node(state: OverallState) -> dict`. This node will use a direct LLM call (not `create_react_agent`):
        *   Take `state['content_draft']` and `state['image_prompts']` as input.
        *   Use an LLM to review, refine, and select the best version of the content and the best *list* of image prompts. It will perform changes if necessary, even in autonomous mode.
        *   Return `state['final_content']` and `state['final_image_prompts']`.

*   [ ] **Step 2.7: Image Generator Agent (`image_generator_agent.py`)**
    *   [ ] Create `x_automation_app/backend/new_app/agents/image_generator_agent.py`.
    *   [ ] This agent will be defined using `langgraph.prebuilt.create_react_agent`.
    *   [ ] It will have the `image_service.generate_and_upload_image` function registered as a tool.
    *   [ ] Implement `image_generator_node(state: OverallState, feedback: Optional[str] = None) -> dict`. This node will:
        *   Take `state['final_image_prompts']` as input (a list of prompts) and `feedback` (if provided from a `HiTL 2` rejection).
        *   Use the LLM (configured via `create_react_agent`) to *reason* on the image prompts and `feedback` to decide how many images to generate, and to iteratively call `image_service.generate_and_upload_image()` for each.
        *   It will also handle *reasoning with user feedback* to refine image prompts and regenerate images if the workflow loops back from `HiTL 2`.
        *   Collect and return a `List[GeneratedImage]` to update `state['generated_images']`.

*   [ ] **Step 2.8: Publicator Agent (`publicator_agent.py`)**
    *   [ ] Create `x_automation_app/backend/new_app/agents/publicator_agent.py`.
    *   [ ] Implement `publicator_node(state: OverallState) -> dict`. This node will use programmatic logic and direct service calls (not `create_react_agent`):
        *   Retrieve `session`, `final_content`, `generated_images` from `OverallState`.
        *   **Implement a helper utilities functions for tweet chunking:** Let the functions be in twitter_service.py for this deterministic logic.
        *   **Conditional Logic based on `state['output_destination']`:**
            *   **If `GET_OUTPUTS`:** Format `final_content` and `generated_images` (using `local_file_path` for local display or `s3_url` for direct link) into a Markdown string. Update `state['publication_id']` to indicate completion.
            *   **If `PUBLISH_X`:**
                *   Check `state['x_content_type']`.
                *   If `TWEET_THREAD`: Use the `tweet_chunking` utility to chunk `final_content` into tweets (280 char limit). Call `twitter_service.post_tweet_thread()`, attaching images if available.
                *   If `SINGLE_TWEET`: Ensure content is under 280 characters. Call `twitter_service.post_tweet()`, attaching images if available.
                *   Update `state['publication_id']` with the `rest_id` from the Twitter API response.
        *   Call `notifications.send_notification` upon successful completion.

---

## **Phase 3: Backend - Orchestration & API (The Conductor)**

This phase integrates all agents into the main LangGraph workflow and exposes the system via FastAPI endpoints.

*   [ ] **Step 3.1: Build the Orchestrator Graph (`orchestrator.py`)**
    *   [ ] Create `x_automation_app/backend/new_app/orchestrator.py`.
    *   [ ] Initialize the `StateGraph` with `OverallState` and a `Checkpointer` (using `InMemoryStore` for development).
    *   [ ] **Add all agent nodes:** `trend_harvester_node`, `tweet_search_node`, `opinion_analysis_node`, `generate_query` (from deep research), `web_research`, `reflection`, `evaluate_research`, `finalize_answer`, `writer_node`, `quality_assurance_node`, `image_generator_node`, `publicator_node`.
    *   [ ] **Implement explicit HiTL interrupt nodes:** (e.g., `await_topic_selection`, `await_content_validation`, `await_image_validation`). These nodes will set `state['next_human_input_step']` and will be `interrupt_after` points in the graph.
    *   [ ] **Implement Autonomous Default Action Nodes:** (e.g., `auto_select_topic` which selects the top trending topic in autonomous mode).
    *   [ ] **Define Comprehensive Workflow Edges & Routing:**
        *   **Initial Routing:** Based on `state['has_user_provided_topic']` and `state['is_autonomous_mode']`.
            *   If `state['has_user_provided_topic']` is `True`, route directly to `tweet_search_node` (Workflow I & III start here).
            *   If `state['has_user_provided_topic']` is `False`:
                *   If `state['is_autonomous_mode']` is `True`, route to `trend_harvester_node` then `auto_select_topic` (Workflow IV).
                *   If `state['is_autonomous_mode']` is `False`, route to `trend_harvester_node` then `await_topic_selection` (Workflow II).
        *   **HiTL vs. Autonomous Routing:** At each validation point, a conditional edge will check `state['is_autonomous_mode']`:
            *   If `False` (HiTL), route to the corresponding `await_X_validation` node.
            *   If `True` (Autonomous), bypass the interrupt node and route directly to the next agent or an `auto_X_action` node if a default selection/decision is needed.
        *   **Post-Validation Routing for Revisions (incorporating feedback):** After `await_X_validation`, conditional edges check `state['validation_result']['action']`. If "reject", the edge will route back to the appropriate previous agent (`writer_node` or `image_generator_node`), passing the user's feedback as a parameter. If "approve" or "edit", it routes forward.
        *   **Image Generation Routing:** After `quality_assurance_node`, a conditional edge checks if `state['final_image_prompts']` is not empty to route to `image_generator_node` or bypass directly to `publicator_node`.
    *   [ ] **(Optional) Graph Visualization:** Add utility to `orchestrator.py` to generate a Mermaid diagram or PNG of the graph.


*   [ ] **Step 3.2: FastAPI Endpoints for Frontend Interaction (`main.py`)**
    *   [ ] **3.2.1: Authentication Endpoints:**
        *   [ ] `POST /auth/start-login`: Receives `email`, `password`, `proxy`. Calls `twitter_service.start_login`. Stores `login_data` in the workflow state (accessed via `Checkpointer`) and sets `next_human_input_step = "await_2fa_code"`.
        *   [ ] `POST /auth/complete-login`: Receives `thread_id`, `two_fa_code`. Loads `login_data` from state, calls `twitter_service.complete_login`. Stores `session` and `user_details` in state. Resumes graph execution by invoking the `orchestrator.py` graph with the updated state.
    *   [ ] **3.2.2: Start Workflow Endpoint:**
        *   [ ] `POST /workflow/start`: Receives initial user inputs (topic, automation mode, output destination, content type params, etc.).
        *   [ ] Creates a unique `thread_id`.
        *   [ ] Initializes the `OverallState` with these inputs.
        *   [ ] Invokes the `orchestrator.py` graph with the initial state and `thread_id`. The graph will run until the first interrupt (HiTL 0 or the first agent if autonomous).
        *   [ ] Returns the full initial `OverallState` to the frontend.
    *   [ ] **3.2.3: Real-time Status Updates with WebSockets:**
        *   [ ] `WS /workflow/ws/{thread_id}`: Implement a WebSocket endpoint.
        *   [ ] Use LangGraph's `astream_events()` (or `astream()` combined with state updates) method to push real-time `OverallState` changes to the connected frontend client as the workflow progresses.
    *   [ ] **3.2.4: Standardized Validation Endpoint:**
        *   [ ] `POST /workflow/validate`: Receives `thread_id` and `validation_data` payload.
        *   [ ] `validation_data` structure: `{ "action": "approve" | "reject" | "edit", "data": { ... } }`.
        *   [ ] Loads the `OverallState` using `thread_id`.
        *   [ ] Updates `state['validation_result']` with `validation_data`. If action is "edit", it overwrites specific state fields (e.g., `state['final_content']`, `state['final_image_prompts']`).
        *   [ ] Resumes graph execution from the last interrupted point by invoking the `orchestrator.py` graph with the updated state.

*   [ ] **Step 3.3: The HiTL Interaction Pattern (Consistent Implementation)**
    *   This pattern will be consistently applied at all user validation points:
        1.  **Agent Executes:** An agent completes its task, saving its output to the `OverallState`.
        2.  **Graph Routes to Interrupt:** If `is_autonomous_mode` is `False`, the graph is routed to a dedicated interrupt node (e.g., `await_content_validation`), which sets `next_human_input_step` and pauses.
        3.  **Frontend Displays & User Validates:** The WebSocket pushes the updated state to the frontend, which renders the UI for user input. The user submits their decision via `POST /workflow/validate`.
        4.  **Backend Updates & Resumes:** The backend updates `validation_result` (and potentially other fields for edits) and resumes the graph.
        5.  **Graph Routes Based on Decision:** A conditional edge checks `validation_result` to route the workflow forward (to the next agent) or backward (to a previous agent for revision), passing feedback to the agent if applicable.

*   [ ] **Step 3.4: Robust Notification Integration**
    *   [ ] Integrate `notifications.send_notification` at critical points:
        *   Upon successful `Publicator` completion (already in Step 2.7).
        *   Within a `try...except` block wrapping the main graph invocation in API endpoints to catch unhandled errors and send failure notifications.
        *   Implement a simple mechanism (e.g., a periodic background task or a check within the `validate` endpoint) to send a notification if a workflow has been paused at a `next_human_input_step` for an extended period (e.g., > X hours), prompting the user to act.

---

## **Phase 4: Frontend Development & Integration**

(Brief placeholder as this is not the current focus, but acknowledge the need for UI)

*   [ ] **Step 4.1: User Input Form:** Develop UI to capture all initial workflow parameters (`is_autonomous_mode`, `output_destination`, `topic`, etc.).
*   [ ] **Step 4.2: Real-time Workflow Dashboard:** Implement a dashboard using WebSockets to display the current state of the workflow and real-time updates.
*   [ ] **Step 4.3: HiTL Validation UIs:** Create specific UI components for each HiTL step (e.g., Topic Selection, Content Validation, Image Validation) to display agent output and capture user feedback/decisions.
*   [ ] **Step 4.4: Authentication UI:** Develop UI for the 2FA login flow.

---

## **Phase 5: Testing, Deployment, and Documentation**

*   [ ] **Step 5.1: Backend Testing (TDD)**
*   [ ] **Step 5.2: Frontend Testing (TDD)**
*   [ ] **Step 5.3: Dockerization & Deployment**
*   [ ] **Step 5.4: Documentation**