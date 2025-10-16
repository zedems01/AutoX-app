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
from .utils.schemas import ValidationResult, Trend, UserConfigSchema, UserDetails, ValidationAction
from .utils.json_encoder import CustomJSONEncoder
from langgraph.types import Send
from .config import settings

from .utils.logging_config import setup_logging, ctext, add_file_handler, remove_file_handler
logger = setup_logging()

# Prometheus monitoring
from prometheus_fastapi_instrumentator import Instrumentator
from .utils.metrics import (
    WORKFLOW_STARTS_TOTAL, WORKFLOW_COMPLETIONS_TOTAL, ACTIVE_WORKFLOWS,
    LOGIN_ATTEMPTS_TOTAL, SESSION_VALIDATIONS_TOTAL,
    TOPICS_SELECTED_TOTAL, CONTENT_DRAFTS_TOTAL, PUBLICATIONS_TOTAL,
    VALIDATION_REQUESTS_TOTAL, VALIDATION_RESPONSES_TOTAL,
    ACTIVE_WEBSOCKETS, WEBSOCKET_DISCONNECTIONS_TOTAL,
    ERRORS_TOTAL
)
from .utils.metrics_manager import metrics_manager


app = FastAPI(
    title="AutoX Backend",
    description="Manages the agentic workflow for content generation and publishing.",
    version="1.0.0",
)

# Initialize Prometheus metrics
# Instrumentator().instrument(app).expose(app, endpoint="/metrics")
instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app, endpoint="/metrics")

# CORS Config
origins = [
    "http://localhost:3000",  # Next.js frontend
    "https://autox.achillengues.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Payloads ---
class LoginPayload(BaseModel):
    user_name: str
    email: str
    password: str
    proxy: str
    totp_secret: str

class DemoLoginPayload(BaseModel):
    token: str

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

    session: Optional[str] = None
    user_details: Optional[UserDetails] = None
    proxy: Optional[str] = None

class ValidateSessionPayload(BaseModel):
    session: str
    proxy: str

class ValidationPayload(BaseModel):
    thread_id: str
    validation_result: ValidationResult

class StopWorkflowPayload(BaseModel):
    thread_id: str

@app.get("/health", summary="Health Check", tags=["Status"])
def health_check():
    """
    Endpoint to check if the server is running.
    """
    return {"status": "oki doki"}

@app.post("/metrics/reset", summary="Reset Metrics", tags=["Status"])
def reset_metrics():
    """
    Reset all metrics to zero. Useful for debugging and testing.
    """
    metrics_manager.reset_metrics()
    return {"status": "metrics reset successfully"}

@app.get("/metrics/status", summary="Get Metrics Status", tags=["Status"])
def get_metrics_status():
    """
    Get current status of active metrics for debugging.
    """
    return {
        "active_workflows_count": metrics_manager.get_active_workflows_count(),
        "active_websockets_count": metrics_manager.get_active_websockets_count(),
        "active_workflows_actual": ACTIVE_WORKFLOWS._value._value,
        "active_websockets_actual": ACTIVE_WEBSOCKETS._value._value,
        "stale_workflows": list(metrics_manager.get_stale_workflows(max_age_seconds=300))  # 5 minutes
    }


# --- Authentication Endpoints ---

@app.post("/auth/login", tags=["Authentication"])
async def login(payload: LoginPayload):
    """
    Handles the user login process.
    """
    logger.info(f"STARTING LOGIN...")

    try:
        session_details = x_utils.login_v2(
            user_name=payload.user_name,
            email=payload.email,
            password=payload.password,
            proxy=payload.proxy,
            totp_secret=payload.totp_secret
        )
        username = ctext(session_details['user_details']['user_name'], italic=True)
        logger.info(ctext(f"Successfully completed login process. Session initialized for user {username}", color='white'))

        # Track successful login
        LOGIN_ATTEMPTS_TOTAL.labels(login_type="normal", status="success").inc()

        return {
            "session": session_details["session_cookie"],
            "userDetails": session_details["user_details"],
            "proxy": payload.proxy,
        }

    except Exception as e:
        logger.error(f"Failed to complete login: {e}")
        LOGIN_ATTEMPTS_TOTAL.labels(login_type="normal", status="failure").inc()
        raise HTTPException(status_code=400, detail=f"Failed to complete login: {e}")


@app.post("/auth/demo-login", tags=["Authentication"])
async def demo_login(payload: DemoLoginPayload):
    """
    Handles the demo user login process using environment variables,
    secured by a secret token.
    """
    logger.info("STARTING DEMO LOGIN...")

    # --- Security Check ---
    if not settings.DEMO_TOKEN:
        logger.error("Demo token is not configured on the server.")
        raise HTTPException(
            status_code=500,
            detail="Demo login is not configured correctly on the server."
        )

    if payload.token != settings.DEMO_TOKEN:
        logger.warning("Invalid demo token received.")
        raise HTTPException(
            status_code=403,
            detail="Invalid token."
        )

    required_creds = [
        settings.TEST_USER_NAME,
        settings.TEST_USER_EMAIL,
        settings.TEST_USER_PASSWORD,
        settings.TEST_USER_PROXY,
        settings.TEST_USER_TOTP_SECRET
    ]

    if not all(required_creds):
        logger.error("Demo user credentials are not fully configured on the server.")
        raise HTTPException(
            status_code=500,
            detail="Demo login is not configured correctly on the server."
        )

    try:
        session_details = x_utils.login_v2(
            user_name=settings.TEST_USER_NAME,
            email=settings.TEST_USER_EMAIL,
            password=settings.TEST_USER_PASSWORD,
            proxy=settings.TEST_USER_PROXY,
            totp_secret=settings.TEST_USER_TOTP_SECRET
        )
        username = ctext(session_details['user_details']['user_name'], italic=True)
        logger.info(ctext(f"Successfully completed demo login. Session initialized for user {username}", color='white'))

        # Track successful demo login
        LOGIN_ATTEMPTS_TOTAL.labels(login_type="demo", status="success").inc()

        return {
            "session": session_details["session_cookie"],
            "userDetails": session_details["user_details"],
            "proxy": settings.TEST_USER_PROXY,
        }

    except Exception as e:
        logger.error(f"Failed to complete demo login: {e}")
        LOGIN_ATTEMPTS_TOTAL.labels(login_type="demo", status="failure").inc()
        raise HTTPException(status_code=500, detail=f"Failed to complete demo login: {e}")


@app.post("/auth/validate-session", tags=["Authentication"])
async def validate_session(payload: ValidateSessionPayload):
    """
    Validates if a session is still active.
    """
    try:
        result = x_utils.verify_session(login_cookies=payload.session, proxy=payload.proxy)
        SESSION_VALIDATIONS_TOTAL.labels(status="valid").inc()
        return result
    except InvalidSessionError as e:
        logger.warning(f"Session validation failed: {e}")
        SESSION_VALIDATIONS_TOTAL.labels(status="invalid").inc()
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred during session validation: {e}")
        SESSION_VALIDATIONS_TOTAL.labels(status="error").inc()
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


# --- Start Workflow Endpoint ---

@app.post("/workflow/start", tags=["Workflow"])
async def start_workflow(payload: StartWorkflowPayload):
    """
    Starts the main content generation workflow with the user's specified settings.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    add_file_handler(thread_id)

    logger.info(f"STARTING WORKFLOW... --- thread_id: {ctext(thread_id, color='white', italic=True)}")

    # Track workflow start using metrics manager
    metrics_manager.start_workflow(thread_id)
    WORKFLOW_STARTS_TOTAL.labels(
        autonomous_mode=str(payload.is_autonomous_mode),
        output_destination=payload.output_destination or "DRAFT",
        content_type=payload.x_content_type or "unknown"
    ).inc()

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
            "max_research_loops": 3,
            "research_loop_count": 0,
            "content_draft": None,
            "image_prompts": None,
            "final_content": None,
            "final_image_prompts": None,
            "generated_images": None,
            "publication_id": None,
            "validation_result": None,
            "error_message": None,
        }

        # Save the initial state and start the graph by the first WebSocket connection.
        graph.update_state(config, initial_state)
        autonomous_mode = True if initial_state["is_autonomous_mode"] else False
        publish_x = True if initial_state["output_destination"] == "PUBLISH_X" else False
        logger.info(ctext(f"Graph successfully updated with initial state:\nAutonomous mode: {autonomous_mode}\nPublish to X: {publish_x}\nContent type: {initial_state['x_content_type']}\nContent length: {initial_state['content_length']}\n", color='white'))

        # Returning the state just constructed so the frontend can proceed.
        return {"thread_id": thread_id, "initial_state": initial_state}

    except Exception as e:
        logger.error(f"An error occurred during workflow execution: {e}")
        metrics_manager.stop_workflow(thread_id)
        WORKFLOW_COMPLETIONS_TOTAL.labels(
            status="error",
            autonomous_mode=str(payload.is_autonomous_mode)
        ).inc()
        ERRORS_TOTAL.labels(error_type=type(e).__name__, component="workflow_start").inc()
        raise HTTPException(status_code=500, detail=f"An error occurred during workflow execution: {e}")


# --- Real-time Status Updates with WebSockets ---

@app.websocket("/workflow/ws/{thread_id}")
async def workflow_ws(websocket: WebSocket, thread_id: str):
    """
    Handles WebSocket connections for real-time workflow status updates.
    """
    await websocket.accept()
    metrics_manager.start_websocket(thread_id)
    
    config = {"configurable": {"thread_id": thread_id}}
    ALLOWED_EVENTS = ["on_chain_start", "on_chain_end"]
    ALLOWED_NAMES = [
        "trend_harvester", "tweet_searcher", "opinion_analyzer", 
        "query_generator", "web_research", "reflection", "finalize_answer", 
        "writer", "quality_assurer", "image_generator", "publicator",
        "await_topic_selection", "await_content_validation",
        "await_image_validation"
    ]

    try:
        # Get the current state and send it to the client
        current_state = graph.get_state(config)
        if current_state:
            await websocket.send_text(json.dumps(current_state.values, cls=CustomJSONEncoder))
        
        # Streaming events to the frontend
        async for event in graph.astream_events(None, config, version="v2"):
            data = event.get("data", {})
            if isinstance(data.get("input"), Send) or isinstance(data.get("output"), Send):
                continue  # not sending this event
            if event.get("event") in ALLOWED_EVENTS and event.get("name") in ALLOWED_NAMES:
                await websocket.send_text(json.dumps(event, cls=CustomJSONEncoder))

        # Sending the final state.
        final_state_of_run = graph.get_state(config)
        if final_state_of_run:
            await websocket.send_text(json.dumps(final_state_of_run.values, cls=CustomJSONEncoder))
            
            # Track workflow completion
            error_msg = final_state_of_run.values.get("error_message")
            status = "error" if error_msg else "success"
            autonomous = final_state_of_run.values.get("is_autonomous_mode", False)
            
            WORKFLOW_COMPLETIONS_TOTAL.labels(
                status=status,
                autonomous_mode=str(autonomous)
            ).inc()
            metrics_manager.stop_workflow(thread_id)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for thread: {thread_id}\n")
        metrics_manager.stop_websocket(thread_id)
        metrics_manager.stop_workflow(thread_id)
        WEBSOCKET_DISCONNECTIONS_TOTAL.labels(reason="client").inc()
        remove_file_handler(thread_id)
    except Exception as e:
        # print(f"Error in WebSocket for thread {thread_id}: {e}\n")
        metrics_manager.stop_websocket(thread_id)
        metrics_manager.stop_workflow(thread_id)
        WEBSOCKET_DISCONNECTIONS_TOTAL.labels(reason="error").inc()
        ERRORS_TOTAL.labels(error_type=type(e).__name__, component="websocket").inc()
        await websocket.close(code=1011, reason=str(e))


# --- Standardized HiTL Validation Endpoint ---

@app.post("/workflow/validate", tags=["Workflow"])
async def validate_step(payload: ValidationPayload):
    """
    Receives user validation, updates the state, and resumes the workflow.
    """
    logger.info("VALIDATION STEP")
    config = {"configurable": {"thread_id": payload.thread_id}}

    try:
        current_state = graph.get_state(config)
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow thread not found.")

        # Specific step that is awaiting validation
        next_step = current_state.values.get("next_human_input_step")
        if not next_step:
            raise HTTPException(status_code=400, detail="No human input is currently awaited for this workflow.")
        
        # Track validation response
        VALIDATION_RESPONSES_TOTAL.labels(
            validation_step=next_step,
            action=payload.validation_result.action.value
        ).inc()
        
        # Storing which step was validated in the result itself, then clearing the
        # human input step to signal to the frontend that the step is "in progress".
        update_data = {
            "validation_result": payload.validation_result.model_dump(exclude_unset=True)
        }
        update_data["validation_result"]["validated_step"] = next_step
        update_data["next_human_input_step"] = None

        # Overwrite the relevant part of the state if editing or approving with data
        if payload.validation_result.action in [ValidationAction.APPROVE, ValidationAction.EDIT]:
            if payload.validation_result.data and payload.validation_result.data.extra_data:
                edit_data = payload.validation_result.data.extra_data
                if next_step == "await_topic_selection" and "selected_topic" in edit_data:
                    # The state for selected_topic expects a dict, not a Pydantic model
                    topic_model = Trend(**edit_data["selected_topic"])
                    update_data["selected_topic"] = topic_model.model_dump(exclude_unset=True)
                    logger.info(ctext(f"The user approved the topic: '{ctext(update_data['selected_topic']['name'], italic=True)}'", color='white'))

                elif next_step == "await_content_validation":
                    logger.info(ctext(f"The user edited then approved the generated content.", color='white'))
                    if "final_content" in edit_data:
                        update_data["final_content"] = edit_data["final_content"]
                    if "final_image_prompts" in edit_data:
                        update_data["final_image_prompts"] = edit_data["final_image_prompts"]
            else:
                logger.info(ctext(f"The user approved the generated content.", color='white'))
        
        elif payload.validation_result.action == ValidationAction.REJECT:
            if payload.validation_result.data and payload.validation_result.data.feedback:
                feedback = payload.validation_result.data.feedback
                logger.info(ctext(f"The user rejected the generated content with the following feedback: '{ctext(feedback, italic=True, color='white')}'.", color='red'))

        graph.update_state(config, update_data)
        logger.info(ctext("Graph successfully updated with validation data.\n", color='white'))


        # Return the updated state so the frontend can re-render and open a new WebSocket
        updated_state = graph.get_state(config)
        return updated_state.values

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during validation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during validation: {e}")


# --- Stop Workflow Endpoint ---

@app.post("/workflow/stop", tags=["Workflow"])
async def stop_workflow(payload: StopWorkflowPayload):
    """
    Stops a running workflow and updates metrics.
    """
    logger.info(f"STOPPING WORKFLOW... --- thread_id: {ctext(payload.thread_id, color='white', italic=True)}")
    
    config = {"configurable": {"thread_id": payload.thread_id}}

    try:
        # Check if workflow exists
        current_state = graph.get_state(config)
        if not current_state:
            raise HTTPException(status_code=404, detail="Workflow thread not found.")

        # Mark the workflow as stopped by updating the state
        update_data = {
            "current_step": "STOPPED",
            "error_message": "Workflow was stopped by user"
        }
        graph.update_state(config, update_data)
        
        # Update metrics using metrics manager
        autonomous = current_state.values.get("is_autonomous_mode", False)
        WORKFLOW_COMPLETIONS_TOTAL.labels(
            status="stopped",
            autonomous_mode=str(autonomous)
        ).inc()
        metrics_manager.stop_workflow(payload.thread_id)
        
        # Clean up file handler
        remove_file_handler(payload.thread_id)
        
        logger.info(ctext(f"Workflow {payload.thread_id} successfully stopped.", color='white'))
        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while stopping the workflow: {e}")
