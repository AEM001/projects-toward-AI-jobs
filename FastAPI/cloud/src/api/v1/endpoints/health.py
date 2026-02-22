from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Health"], summary="Health check endpoint")
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        - **status**: "healthy" if the service is operational
        - **timestamp**: Current server time in ISO format
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }