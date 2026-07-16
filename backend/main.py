"""
main.py
-------
FastAPI application entry point for the CareerCopilot AI backend.

Run with:
    uvicorn backend.main:app --reload --port 8000

Then run the frontend separately with:
    streamlit run frontend/app.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.db import init_db
from backend.api.routes import router

app = FastAPI(title="CareerCopilot AI Backend")

# Allow the Streamlit frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def startup_event():
    """Ensure all database tables exist before the app starts serving requests."""
    init_db()


@app.get("/")
def root():
    """Simple health-check endpoint."""
    return {"status": "CareerCopilot AI backend is running"}
