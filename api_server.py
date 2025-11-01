"""FastAPI server to serve portfolio data to the frontend."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.models import get_portfolio_history
from typing import List, Dict, Any

app = FastAPI(title="Trader AI API", version="1.0.0")

# Enable CORS for React frontend
# In production, use environment variable or allow all origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Trader AI API Server"}


@app.get("/api/portfolio/history", response_model=None)
def get_history(limit: int = None) -> List[Dict[str, Any]]:
    """
    Get portfolio history.
    
    Args:
        limit: Optional limit on number of records to return
    
    Returns:
        List of portfolio data points with timestamp, total, and available
    """
    return get_portfolio_history(limit=limit)


@app.get("/api/portfolio/latest", response_model=None)
def get_latest() -> Dict[str, Any]:
    """
    Get the latest portfolio data point.
    
    Returns:
        Latest portfolio data point
    """
    history = get_portfolio_history(limit=1)
    if history:
        # Return the last item (most recent)
        return history[-1]
    return {"timestamp": None, "total": 0, "available": 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

