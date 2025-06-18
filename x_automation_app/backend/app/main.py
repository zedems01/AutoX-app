from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Optional
import json

from .agents.graph import graph
from .utils import x_utils
from .utils.x_utils import InvalidSessionError
from .agents.state import OverallState
from .utils.schemas import ValidationResult, Trend, UserConfigSchema, UserDetails
from .utils.json_encoder import CustomJSONEncoder
from langgraph.types import Send

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
    login_data: str # From start_login
    two_fa_code: str
    proxy: str

class StartWorkflowPayload(BaseModel):
    is_autonomous_mode: bool
    output_destination: Optional[str] = None
    has_user_provided_topic: bool
    user_provided_topic: Optional[str] = None
    x_content_type: Optional[str] = None
    content_length: Optional[str] = None
    brand_voice: Optional[str] = None
    target_audience: Optional[str] = None
    user_config: Optional[UserConfigSchema] = None

    # New optional fields for auth context
    session: Optional[str] = None
    user_details: Optional[UserDetails] = None
    proxy: Optional[str] = None

class ValidateSessionPayload(BaseModel):
    session: str
    proxy: str

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
    This is a stateless endpoint.
    """
    try:
        login_data = x_utils.start_login(
            email=payload.email, password=payload.password, proxy=payload.proxy
        )
        logger.info("Successfully started login process.")
        return {"login_data": login_data}
    except Exception as e:
        logger.error(f"Failed to start login: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to start login: {e}")


@app.post("/auth/complete-login", tags=["Authentication"])
async def complete_login(payload: CompleteLoginPayload):
    """
    Completes the 2FA login process using the code provided by the user.
    This is a stateless endpoint.
    """
    try:
        session_details = x_utils.complete_login(
            login_data=payload.login_data,
            two_fa_code=payload.two_fa_code,
            proxy=payload.proxy
        )
        logger.info("Successfully completed login process. Session initialized.")
        logger.info(f"Name: {session_details['user_details']['name']} \t Username: {session_details['user_details']['screen_name']}")

        return {
            "session": session_details["session"],
            "userDetails": session_details["user_details"],
            "proxy": payload.proxy,
        }

    except Exception as e:
        logger.error(f"Failed to complete login: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to complete login: {e}")


@app.post("/auth/validate-session", tags=["Authentication"])
async def validate_session(payload: ValidateSessionPayload):
    """
    Validates if a user's session is still active.
    """
    try:
        result = x_utils.verify_session(session=payload.session, proxy=payload.proxy)
        return result
    except InvalidSessionError as e:
        logger.warning(f"Session validation failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred during session validation: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# --- Step 3.2.2: Start Workflow Endpoint ---

@app.post("/workflow/start", tags=["Workflow"])
async def start_workflow(payload: StartWorkflowPayload, background_tasks: BackgroundTasks):
    """
    Starts the main content generation workflow with the user's specified settings.
    """
    logger.info(f"Payload received...Starting workflow with payload: {payload}\n")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Prepare the initial state from the payload
        initial_state: OverallState = {
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
            # Add auth context
            "session": payload.session,
            "user_details": payload.user_details,
            "proxy": payload.proxy,
            # Initialize all other fields to None or default values
            "login_data": None,
            "next_human_input_step": None,
            "messages": [],
            "trending_topics": None,
            "selected_topic": None,
            "tweet_search_results": None,
            "opinion_summary": None,
            "overall_sentiment": None,
            "topic_from_opinion_analysis": None,
            "final_deep_research_report": None,
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": 0,
            "max_research_loops": 3,  # Default value
            "research_loop_count": 0,
            "content_draft": None,
            "image_prompts": None,
            "final_content": None,
            "final_image_prompts": None,
            "generated_images": None,
            "publication_id": None,
            "validation_result": None,
            "error_message": None,
            "source_step": None,
        }

        # Run the graph invocation in the background
        background_tasks.add_task(graph.ainvoke, initial_state, config=config)

        # The frontend expects an `initial_state` object in the response.
        # We return the state we just constructed so the frontend can proceed.
        return {"thread_id": thread_id, "initial_state": initial_state}

    except Exception as e:
        logger.error(f"An error occurred during workflow execution: {e}")
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
            await websocket.send_text(json.dumps(initial_state.values, cls=CustomJSONEncoder))
        
        # Stream all v2 events to the frontend
        async for event in graph.astream_events(None, config, version="v2"):
            # Check if the event data contains a `Send` object, which is not serializable
            # and not needed by the frontend.
            data = event.get("data", {})
            if isinstance(data.get("chunk"), Send) or isinstance(data.get("output"), Send):
                continue  # Skip sending this event
            print(f"Sending event:\n{event}\n\n")
            await websocket.send_text(json.dumps(event, cls=CustomJSONEncoder))

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for thread: {thread_id}\n")
    except Exception as e:
        print(f"Error in WebSocket for thread {thread_id}: {e}\n")
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

        # Prepare the state update, converting Pydantic models to dicts
        update_data = {
            "validation_result": payload.validation_result.model_dump(exclude_unset=True)
        }
        print(f"Validation result:\n{payload.validation_result.model_dump(exclude_unset=True)}")

        # If the user is editing, overwrite the relevant part of the state
        if payload.validation_result.action == "edit":
            if payload.validation_result.data and payload.validation_result.data.extra_data:
                edit_data = payload.validation_result.data.extra_data
                if next_step == "await_topic_selection" and "selected_topic" in edit_data:
                    # The state for selected_topic expects a dict, not a Pydantic model
                    topic_model = Trend(**edit_data["selected_topic"])
                    update_data["selected_topic"] = topic_model.model_dump(exclude_unset=True)
                elif next_step == "await_content_validation":
                    if "final_content" in edit_data:
                        update_data["final_content"] = edit_data["final_content"]
                    if "final_image_prompts" in edit_data:
                        update_data["final_image_prompts"] = edit_data["final_image_prompts"]

        print(f"Trying to update the state...")
        # Update the state and resume the graph
        graph.update_state(config, update_data)
        final_state = await graph.ainvoke(None, config)

        return final_state

    except Exception as e:
        logger.error(f"Error during validation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during validation: {e}") 
    