from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

from .agents.graph import app, memory
from .services import twitter_service
from .agents.state import OverallState

# --- FastAPI App Initialization ---
api = FastAPI(
    title="X Automation Backend",
    description="Manages the agentic workflow for content generation and publishing.",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow the Next.js frontend
]

# --- CORS Configuration ---
api.add_middleware(
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

# --- Health Check Endpoint ---
@app.get("/health", summary="Health Check", tags=["Status"])
def health_check():
    """
    Endpoint to check if the server is running.
    """
    return {"status": "ok"}

# --- Step 3.2.1: Authentication Endpoints ---

@api.post("/auth/start-login", tags=["Authentication"])
async def start_login(payload: StartLoginPayload):
    """
    Starts the 2FA login process for Twitter.
    Creates a new workflow thread and returns the thread_id.
    """
    try:
        login_data = twitter_service.start_login(
            email=payload.email, password=payload.password, proxy=payload.proxy
        )
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
    
    app.update_state(config, initial_state)

    return {"thread_id": thread_id, "login_data": login_data}


@api.post("/auth/complete-login", tags=["Authentication"])
async def complete_login(payload: CompleteLoginPayload):
    """
    Completes the 2FA login process using the code provided by the user.
    Stores the session in the workflow state.
    """
    config = {"configurable": {"thread_id": payload.thread_id}}
    
    try:
        current_state = app.get_state(config)
        login_data = current_state.values.get("login_data")
        proxy = current_state.values.get("proxy")

        if not login_data or not proxy:
            raise HTTPException(status_code=404, detail="Login session not found or incomplete. Please start login again.")

        session_details = twitter_service.complete_login(
            login_data=login_data, two_fa_code=payload.two_fa_code, proxy=proxy
        )
        
        updated_state = {
            "session": session_details,
            "user_details": session_details.get("user_details"),
            "next_human_input_step": None, # Clear the step
        }
        
        app.update_state(config, updated_state)

        return {"status": "success", "user_details": session_details.get("user_details")}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to complete login: {e}") 