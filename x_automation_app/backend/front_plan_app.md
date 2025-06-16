# Frontend Implementation Plan

This document outlines the detailed plan for building the frontend user interface for the X Automation project. It is designed to be a comprehensive guide for a frontend developer, providing all necessary context about the backend and a step-by-step implementation path.

---

## **Part 1: Backend Handoff & API Documentation**

This section details how the backend works and how to interact with it. The backend is a stateful, agentic workflow managed by FastAPI and LangGraph. The frontend's primary role is to start the workflow, receive real-time state updates via WebSockets, and provide user input when the workflow pauses for Human-in-the-Loop (HiTL) validation.

### **Core Concept: The Workflow State**

The entire system revolves around a single, central state object: `OverallState`. When a workflow is running, the frontend will receive the **entire `OverallState` object** over a WebSocket connection every time a step is completed.

**Your most important task is to listen for changes to this object and update the UI accordingly.** Do not manage the state yourself; simply reflect the state provided by the backend.

The key field to watch is `next_human_input_step`. When this field is not `null`, the backend is paused and waiting for you. The value of this field tells you exactly which UI to display to the user.

-   `"await_2fa_code"`: Show the 2FA code input form.
-   `"await_topic_selection"`: Show the topic selection UI.
-   `"await_content_validation"`: Show the content and image prompt validation UI.
-   `"await_image_validation"`: Show the generated image validation UI.

### **API Endpoints**

The backend exposes the following endpoints:

#### **Authentication**

1.  **Start Login**
    *   **Endpoint:** `POST /auth/start-login`
    *   **Purpose:** Initiates the 2FA login process with Twitter.
    *   **Request Body:**
        ```json
        {
          "email": "user@example.com",
          "password": "your_password",
          "proxy": "http://user:pass@ip:port"
        }
        ```
    *   **Success Response (200):** Returns a `thread_id` which you must save. This ID represents the entire workflow session.
        ```json
        {
          "thread_id": "a-unique-uuid-string",
          "login_data": { ... } // Opaque data object
        }
        ```
    *   **Error Response (400/500):** `{ "detail": "Error message..." }`

2.  **Complete Login**
    *   **Endpoint:** `POST /auth/complete-login`
    *   **Purpose:** Submits the 2FA code to complete authentication.
    *   **Request Body:**
        ```json
        {
          "thread_id": "the-uuid-from-start-login",
          "two_fa_code": "123456"
        }
        ```
    *   **Success Response (200):**
        ```json
        {
          "status": "success",
          "user_details": { ... } // Details about the logged-in user
        }
        ```
    *   **Error Response (400/404/500):** `{ "detail": "Error message..." }`

#### **Workflow Management**

3.  **Start Workflow**
    *   **Endpoint:** `POST /workflow/start`
    *   **Purpose:** Kicks off the main content generation process after login.
    *   **Request Body:**
        ```json
        {
          "thread_id": "the-uuid-from-start-login",
          "is_autonomous_mode": false,
          "output_destination": "GET_OUTPUTS", // or "PUBLISH_X"
          "has_user_provided_topic": true,
          "user_provided_topic": "The future of AI",
          "x_content_type": "TWEET_THREAD", // or "SINGLE_TWEET"
          "content_length": "SHORT",
          "brand_voice": "Informative and engaging",
          "target_audience": "Tech enthusiasts",
          "user_config": {
            "gemini_base_model": "",
            "gemini_reasoning_model": "",
            "openai_model": "",
            "trends_count": "",
            "trends_woeid": "",
            "max_tweets_to_retrieve": "",
            "tweets_language": "",
            "content_language": ""

          } // Optional: Override default agent settings
        }
        ```
    *   **Success Response (200):** Returns the `OverallState` after the graph has run and paused at the first interrupt point.
        ```json
        {
          // Full OverallState object
        }
        ```

4.  **WebSocket for Real-time Updates**
    *   **Endpoint:** `WS /workflow/ws/{thread_id}`
    *   **Purpose:** Streams real-time updates of the `OverallState`.
    *   **Usage:** After a successful login, connect to this endpoint using the `thread_id`. The backend will immediately push the current state. Thereafter, every time a node in the workflow finishes, a new, complete `OverallState` object will be pushed. Listen for these messages to drive all UI updates.

5.  **Submit Validation**
    *   **Endpoint:** `POST /workflow/validate`
    *   **Purpose:** Submits the user's decision during a HiTL step to resume the workflow.
    *   **Request Body:**
        ```json
        {
          "thread_id": "the-uuid-from-start-login",
          "validation_result": {
            "action": "approve" // or "reject" or "edit"
            "data": {
              "feedback": "This isn't quite right, please revise.", // for "reject"
              "extra_data": { // for "edit"
                "final_content": "This is my edited version of the content."
              }
            }
          }
        }
        ```
    *   **Success Response (200):** Returns the final state of the workflow after it has run to the next interrupt (or to completion).
        ```json
        {
          // Full OverallState object
        }
        ```

---

## **Part 2: Frontend Implementation**

### **Phase 4.0: Project Setup & Foundation**

*   [ ] **Step 4.0.1: Initialize Next.js Project:** Set up a new Next.js 14+ project using the App Router (`npx create-next-app@latest`).
*   [ ] **Step 4.0.2: Install Dependencies:**
    ```bash
    npm install tailwindcss-animate lucide-react @radix-ui/react-slot class-variance-authority clsx
    npm install @tanstack/react-query react-hook-form @hookform/resolvers zod sonner next-themes
    ```
*   [ ] **Step 4.0.3: Setup Shadcn UI:** Initialize Shadcn UI, which provides our component library.
    ```bash
    npx shadcn-ui@latest init
    ```
*   [ ] **Step 4.0.4: Define Project Structure:**
    - `app/`: Main routing.
    - `components/`:
        - `ui/`: (auto-generated by Shadcn)
        - `shared/`: Custom shared components (`ThemeToggle`, `PageHeader`).
        - `workflow/`: Components for specific workflow steps (`TopicSelection`, `ContentValidation`).
    - `lib/`:
        - `api.ts`: Functions for calling the backend API.
        - `utils.ts`: General utility functions.
    - `hooks/`:
        - `use-workflow.ts`: The primary hook for managing the WebSocket connection and state.
    - `contexts/`:
        - `WorkflowProvider.tsx`: Manages the global state, including `thread_id`.
    - `types/`:
        - `index.ts`: TypeScript definitions for `OverallState` and all API payloads.

### **Phase 4.1: Core UI & Services**

*   [ ] **Step 4.1.1: Main Layout & Theming:**
    - Create a root layout (`app/layout.tsx`) with a header and main content area.
    - Implement a Bright/Dark theme toggle using `next-themes`.
    - Add the `<Toaster />` component from `sonner` to the layout for notifications.
*   [ ] **Step 4.1.2: API Service Layer (`lib/api.ts`):**
    - Create typed functions for each backend endpoint (`startLogin`, `completeLogin`, etc.). These will be called by TanStack Query's `useMutation`.
*   [ ] **Step 4.1.3: Global State & WebSocket (`contexts/WorkflowProvider.tsx` & `hooks/use-workflow.ts`):**
    - Create a `WorkflowContext` to store the `thread_id` and the latest `OverallState`.
    - Create a `useWorkflow` hook that establishes the WebSocket connection and updates the context with new state messages. This hook will be the primary data source for the workflow dashboard.

### **Phase 4.2: Authentication UI**

*   [ ] **Step 4.2.1: Login Page (`app/login/page.tsx`):**
    - Build a login form using Shadcn components (`Input`, `Button`, `Card`).
    - Use `useMutation` (TanStack Query) to call the `startLogin` API function.
    - On success, store the `thread_id` in the `WorkflowContext` and navigate to the 2FA page.
    - Show loading states on the button and display errors using `sonner` toasts.
*   [ ] **Step 4.2.2: 2FA Page (`app/login/2fa/page.tsx`):**
    - Build a form for the 2FA code, using Shadcn's `InputOTP` for a great user experience.
    - Use `useMutation` to call `completeLogin`.
    - On success, navigate to the main workflow configuration page.

### **Phase 4.3: Workflow Setup & Dashboard**

*   [ ] **Step 4.3.1: Workflow Configuration Form (`app/page.tsx`):**
    - Build a comprehensive form for all `StartWorkflowPayload` parameters. Use Shadcn `Switch`, `RadioGroup`, `Select`, `Input`, and `Textarea` components.
    - Use `useMutation` to call the `startWorkflow` API function.
    - On success, navigate the user to the main dashboard: `/workflow/{thread_id}`.
*   [ ] **Step 4.3.2: Workflow Dashboard (`app/workflow/[threadId]/page.tsx`):**
    - This is the main view for monitoring and interacting with an active workflow.
    - Use the `useWorkflow` hook to get the latest state.
    - Display a "Current Status" component based on `state.current_step`.
    - **Conditionally render the correct HiTL component based on `state.next_human_input_step`**.

### **Phase 4.4: Human-in-the-Loop (HiTL) UI Components**

*   [ ] **Step 4.4.1: Topic Selection (`components/workflow/TopicSelection.tsx`):**
    - Receives `trending_topics` from the dashboard.
    - Displays topics in a `Table` with a `RadioGroup` in the first column for selection.
    - Has an "Approve" button that calls the `validateStep` mutation.
*   [ ] **Step 4.4.2: Content Validation (`components/workflow/ContentValidation.tsx`):**
    - Receives `final_content` and `final_image_prompts`.
    - Displays content in a `Textarea` to allow for edits.
    - Provides "Approve", "Reject", and "Save & Approve" buttons.
    - Clicking "Reject" opens a `Dialog` to enter feedback.
*   [ ] **Step 4.4.3: Image Validation (`components/workflow/ImageValidation.tsx`):**
    - Receives `generated_images`.
    - Renders the images in a grid.
    - Provides "Approve" and "Reject" buttons. The reject button could allow feedback for regeneration.

---

## **Part 3: How to Launch the Backend**

To develop the frontend, you will need to run the backend server locally. Follow these steps:

### **1. Setup Your Environment**

*   **Navigate to the Backend Directory:**
    Open your terminal and change into the backend directory:
    ```bash
    cd x_automation_app/backend
    ```

*   **Install Dependencies:**
    This project uses `uv` for package management. If you haven't already, install the required packages from within the `x_automation_app/backend` directory:
    ```bash
    uv pip install fastapi "uvicorn[standard]" python-dotenv pydantic langgraph langchain-google-genai google-genai "openai<2.0.0"
    ```

*   **Create Your `.env` File:**
    In the `x_automation_app/backend` directory, create a file named `.env`. You will need to populate it with your secret keys and credentials. Use the following template:
    ```env
    # LLM Provider API Keys (Gemini is mandatory)
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

    # twitterapi.io API Credentials
    X_API_KEY="YOUR_X_API_KEY_FROM_TWITTERAPI.IO"
    USER_PROXY="http://username:password@ip:port" # From a service like Webshare

    # Your X (Twitter) Credentials
    USER_EMAIL="YOUR_X_EMAIL"
    USER_PASSWORD="YOUR_X_PASSWORD"

    # AWS S3 Settings for Image Storage
    AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_ACCESS_KEY"
    AWS_DEFAULT_REGION="us-east-1"
    BUCKET_NAME="your-s3-bucket-name"

    # LangSmith API Keys for Tracing (Optional)
    LANGSMITH_TRACING="false"
    LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
    LANGSMITH_API_KEY=""
    LANGSMITH_PROJECT=""
    ```

### **2. Run the Server**

Once your environment is set up, run the following command from the `x_automation_app/backend` directory:

```bash
uvicorn new_app.main:app --reload
```

The API server will start, typically on `http://127.0.0.1:8000`. You can now access the API endpoints and connect your frontend application. The auto-generated documentation will be available at `http://127.0.0.1:8000/docs`.
