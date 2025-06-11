from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="X Automation AI Agent System",
    version="1.0",
    description="Backend server for the multi-agent system.",
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow the Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="Health Check", tags=["Status"])
def health_check():
    """
    Endpoint to check if the server is running.
    """
    return {"status": "ok"}
