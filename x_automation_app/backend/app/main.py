from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Optional

from .agents.graph import graph
from .utils import x_utils
from .agents.state import OverallState
from .utils.schemas import ValidationResult, Trend, UserConfigSchema

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- FastAPI App Initialization ---
app = FastAPI(
    title="AutoX Backend",
    description="Manages the agentic workflow for content generation and publishing.",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow the Next.js frontend
]

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Payloads ---
class StartLoginPayload(BaseModel):
    email: str
    password: str
    proxy: str

class CompleteLoginPayload(BaseModel):
    thread_id: str
    two_fa_code: str

class StartWorkflowPayload(BaseModel):
    thread_id: str
    is_autonomous_mode: bool
    output_destination: Optional[str] = None
    has_user_provided_topic: bool
    user_provided_topic: Optional[str] = None
    x_content_type: Optional[str] = None
    content_length: Optional[str] = None
    brand_voice: Optional[str] = None
    target_audience: Optional[str] = None
    user_config: Optional[UserConfigSchema] = None

class ValidationPayload(BaseModel):
    thread_id: str
    validation_result: ValidationResult

# --- Health Check Endpoint ---
@app.get("/health", summary="Health Check", tags=["Status"])
def health_check():
    """
    Endpoint to check if the server is running.
    """
    return {"status": "ok"}

# --- Step 3.2.1: Authentication Endpoints ---

@app.post("/auth/start-login", tags=["Authentication"])
async def start_login(payload: StartLoginPayload):
    """
    Starts the 2FA login process for Twitter.
    Creates a new workflow thread and returns the thread_id.
    """
    try:
        login_data = x_utils.start_login(
            email=payload.email, password=payload.password, proxy=payload.proxy
        )
        # login_data = "test"
        logger.info(f"Successfully started login process.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to start login: {e}")

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state: OverallState = {
        "login_data": login_data,
        "proxy": payload.proxy,
        "next_human_input_step": "await_2fa_code",
        "messages": [],
        # Initialize all other fields to None or default values
        "is_autonomous_mode": False,
        "output_destination": None,
        "has_user_provided_topic": False,
        "x_content_type": None,
        "content_length": None,
        "brand_voice": None,
        "target_audience": None,
        "user_config": None,
        "session": None,
        "user_details": None,
        "trending_topics": None,
        "selected_topic": None,
        "user_provided_topic": None,
        "tweet_search_results": None,
        "opinion_summary": None,
        "overall_sentiment": None,
        "topic_from_opinion_analysis": None,
        "final_deep_research_report": None,
        "search_query": [],
        "web_research_result": [],
        "sources_gathered": [],
        "initial_search_query_count": 0,
        "max_research_loops": 0,
        "research_loop_count": 0,
        "content_draft": None,
        "image_prompts": None,
        "final_content": None,
        "final_image_prompts": None,
        "generated_images": None,
        "publication_id": None,
        "validation_result": None,
        "current_step": "login",
        "error_message": None,
    }
    
    graph.update_state(config, initial_state)
    logger.info(f"Successfully updated the state.")

    return {"thread_id": thread_id, "login_data": login_data}


@app.post("/auth/complete-login", tags=["Authentication"])
async def complete_login(payload: CompleteLoginPayload):
    """
    Completes the 2FA login process using the code provided by the user.
    Stores the session in the workflow state.
    """
    config = {"configurable": {"thread_id": payload.thread_id}}
    
    try:
        current_state = graph.get_state(config)
        login_data = current_state.values.get("login_data")
        proxy = current_state.values.get("proxy")

        if not login_data or not proxy:
            raise HTTPException(status_code=404, detail="Login session not found or incomplete. Please start login again.")

        session_details = x_utils.complete_login(
            login_data=login_data, two_fa_code=payload.two_fa_code, proxy=proxy
        )
        logger.info(f"Successfully completed login process. Session initialized.")
        logger.info(f"Name: {session_details['user_details']['name']} \t Username: {session_details['user_details']['screen_name']}")
        logger.info(f"Session: {session_details['session']}")

        updated_state = {
            "session": session_details["session"],
            "user_details": session_details["user_details"],
            "next_human_input_step": None, # Clear the step
        }
        
        graph.update_state(config, updated_state)
        logger.info(f"Successfully updated the state.")

        return {"status": "success", "user_details": session_details.get("user_details")}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to complete login: {e}")


# --- Step 3.2.2: Start Workflow Endpoint ---

@app.post("/workflow/start", tags=["Workflow"])
async def start_workflow(payload: StartWorkflowPayload):
    """
    Starts the main content generation workflow with the user's specified settings.
    """
    config = {"configurable": {"thread_id": payload.thread_id}}

    try:
        # Check if the session exists from the login step
        current_state = graph.get_state(config)
        if not current_state or not current_state.values.get("session"):
            raise HTTPException(status_code=404, detail="Active session not found. Please log in first.")

        # Prepare the state update from the payload
        workflow_inputs = {
            "is_autonomous_mode": payload.is_autonomous_mode,
            "output_destination": payload.output_destination,
            "has_user_provided_topic": payload.has_user_provided_topic,
            "user_provided_topic": payload.user_provided_topic,
            "x_content_type": payload.x_content_type,
            "content_length": payload.content_length,
            "brand_voice": payload.brand_voice,
            "target_audience": payload.target_audience,
            "user_config": payload.user_config,
            "current_step": "workflow_started",
        }

        # Update the state with the new workflow configuration
        graph.update_state(config, workflow_inputs)

        # Invoke the graph to run until the first interrupt
        final_state = await graph.ainvoke(None, config)

        return final_state

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during workflow execution: {e}")


# --- Step 3.2.3: Real-time Status Updates with WebSockets ---

@app.websocket("/workflow/ws/{thread_id}")
async def workflow_ws(websocket: WebSocket, thread_id: str):
    """
    Handles WebSocket connections for real-time workflow status updates.
    """
    await websocket.accept()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Send the initial state as soon as the client connects
        initial_state = graph.get_state(config)
        if initial_state:
            await websocket.send_json(initial_state.values)
        
        # Stream updates as the graph executes
        async for event in graph.astream_events(None, config, version="v1"):
            # After any node finishes, the state is potentially updated.
            # We'll get the latest state and send it to the client.
            if event["event"] == "on_chain_end":
                current_state = graph.get_state(config)
                if current_state:
                    await websocket.send_json(current_state.values)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for thread: {thread_id}")
    except Exception as e:
        print(f"Error in WebSocket for thread {thread_id}: {e}")
        await websocket.close(code=1011, reason=str(e))


# --- Step 3.2.4: Standardized Validation Endpoint ---

@app.post("/workflow/validate", tags=["Workflow"])
async def validate_step(payload: ValidationPayload):
    """
    Receives user validation, updates the state, and resumes the workflow.
    """
    config = {"configurable": {"thread_id": payload.thread_id}}

    try:
        current_state = graph.get_state(config)
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow thread not found.")

        # Get the specific step that is awaiting validation
        next_step = current_state.values.get("next_human_input_step")
        if not next_step:
            raise HTTPException(status_code=400, detail="No human input is currently awaited for this workflow.")

        # Prepare the state update
        update_data = {"validation_result": payload.validation_result}

        # If the user is editing, overwrite the relevant part of the state
        if payload.validation_result.action == "edit":
            edit_data = payload.validation_result.data.extra_data
            if next_step == "await_topic_selection" and "selected_topic" in edit_data:
                 # Ensure the topic is in the correct Pydantic model format
                update_data["selected_topic"] = Trend(**edit_data["selected_topic"])
            elif next_step == "await_content_validation":
                if "final_content" in edit_data:
                    update_data["final_content"] = edit_data["final_content"]
                if "final_image_prompts" in edit_data:
                    update_data["final_image_prompts"] = edit_data["final_image_prompts"]
            # Add other edit cases as needed

        # Update the state and resume the graph
        graph.update_state(config, update_data)
        final_state = await graph.ainvoke(None, config)

        return final_state

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during validation: {e}") 
    