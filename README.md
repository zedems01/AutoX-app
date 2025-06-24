# AutoX 🚀

An autonomous AI agent team for real-time, trend-driven content creation.

<p style="text-align: center;">
  <img src="./x_automation_app/autoX-workflow-graph.png" alt="workflow images" width="700" />
</p>

## 🌟 About The Project

AutoX is a powerful, agent-based system that leverages real-time trends and news to automate the creation of diverse content. Whether you need a blog post, an article, or a social media update, this team of AI agents can handle the entire workflow—from initial research to final draft. It offers deep flexibility in adapting to any brand voice and can operate fully autonomously or with human oversight for fine-tuned control.

The system features a sleek, modern web interface built with **Next.js** and **Shadcn/UI**, allowing users to configure, launch, and monitor the agentic workflow in real time.

### Key Features

-   **📈 Real-Time Trend Analysis**: Capitalizes on breaking trends and news from X and the web to create timely, high-impact content.
-   **✍️ Multi-Format Content Generation**: More than just a tweet scheduler. Generate comprehensive blog posts, detailed articles, and engaging social media updates.
-   **🗣️ Dynamic Brand Voice Adaptation**: Define your brand's unique voice—witty, formal, technical—and the agents will adapt their writing style accordingly.
-   **🤖 Fully Autonomous or Human-Guided**: Run the workflow on complete autopilot or use the Human-in-the-Loop (HiTL) steps to review and refine content at key stages.
-   **🚀 Direct Publishing & Flexible Output**: Publish directly to X or receive the generated content and images to use on any platform like your blog, LinkedIn, or other social channels.
-   **📊 Live Progress Dashboard**: Monitor the entire multi-agent workflow in real-time through a detailed, user-friendly interface.
-   **🌐 Deep Research Capability**: Agents perform in-depth web research to ensure content is not just fast, but also factual and well-supported.

## 🏗️ Architecture

The project is a monorepo composed of a FastAPI backend and a Next.js frontend.

### Backend

-   **Framework**: **FastAPI** serves the REST API and WebSocket for real-time communication.
-   **Agentic Core**: **LangGraph** orchestrates the stateful, multi-agent workflow.
-   **Data Validation**: **Pydantic** ensures data integrity between the frontend, backend, and agent states.
-   **Dependencies**: Managed by **UV**.

### Frontend

-   **Framework**: **Next.js** (with the App Router).
-   **Language**: **TypeScript**.
-   **UI**: **Shadcn/UI** and **Tailwind CSS** for a modern, responsive interface.
-   **Form Management**: **React Hook Form** and **Zod** for robust, type-safe forms.
-   **State & Data Fetching**: **React Context** and **TanStack Query**.

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

-   Node.js and npm
-   Python 3.12+ and [UV](https://github.com/astral-sh/uv)

### 1. Backend Setup

First, set up and launch the backend server.

```bash
# 1. Navigate to the backend directory
cd x_automation_app/backend

# 2. Create and activate a virtual environment
uv venv
source .venv/bin/activate
# On Windows, use: .venv\Scripts\activate

# 3. Install dependencies
uv pip install -e .

# 4. Set up environment variables
# Copy the template to a new .env file
cp env.template .env

# 5. Edit the .env file with your credentials
```

You will need to provide the following in the `.env` file:
-   `GEMINI_API_KEY`: Mandatory for the deep research agent.
-   `OPENAI_API_KEY`: For the main content generation agents.
-   `X_API_KEY`: From a service like `twitterapi.io` for scraping.
-   `USER_PROXY`: A proxy is required for X login automation.
-   Optionally, provide AWS credentials for image uploads and LangSmith for tracing.

```bash
# 6. Launch the backend server
uvicorn app.main:app --reload
# The backend will be running at http://localhost:8000
```

### 2. Frontend Setup

In a separate terminal, set up and launch the frontend application.

```bash
# 1. Navigate to the frontend directory
cd x_automation_app/frontend

# 2. Install dependencies
npm install

# 3. Launch the frontend development server
npm run dev
```

The application will be accessible at **http://localhost:3000**.

## 🤖 The Agent Team

The workflow is composed of several specialized agents and nodes that collaborate to generate and publish content.

-   **🔎 Trend Harvester**: Identifies trending topics on X for a specified location.
-   **🐦 Tweet Searcher**: Gathers relevant, recent tweets for a given topic to understand public sentiment and talking points.
-   **🤔 Opinion Analyzer**: Analyzes the collected tweets to create a summary of public opinion and sentiment.
-   **✍️ Writer**: Drafts the final content (e.g., Tweet, Thread) based on the research and analysis.
-   **✨ Quality Assurer**: Reviews and refines the drafted content, generating image prompts if necessary.
-   **🎨 Image Generator**: Creates images based on the prompts from the QA agent.
-   **📢 Publicator**: Publishes the final content and images to X.
-   **🧠 Deep Research Sub-Graph**: An embedded workflow that performs deep web searches to create a comprehensive research report on a topic.
-   **🙋‍♂️ Human Validation Nodes**: These nodes pause the graph and await user input for topic selection, content approval, and image validation.

## Project Structure

```
x_automation_app/
├── backend/
│   ├── app/
│   │   ├── agents/      # Core agent logic and graph definition
│   │   ├── utils/       # Utilities for prompts, schemas, etc.
│   │   └── main.py      # FastAPI application entrypoint
│   └── pyproject.toml   # Backend dependencies
└── frontend/
    ├── src/
    │   ├── app/         # Next.js pages and routing
    │   ├── components/  # Reusable React components
    │   ├── contexts/    # Global state management (Auth, Workflow)
    │   └── lib/         # API client and utility functions
    └── package.json     # Frontend dependencies
```