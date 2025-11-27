from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.models.feedback_model import EnhanceFeedbackRequest, EnhanceFeedbackResponse
from agents.ai_feedback import enhance_feedback

router = APIRouter()

@router.post("/evaluate-feedback", response_model=EnhanceFeedbackResponse)
def analyze_feedback(feedback:EnhanceFeedbackRequest):
    try:
        response = enhance_feedback(feedback)
        return response
    except Exception as e:
        logging.error(f"Error evaluating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to evaluate feedback")


