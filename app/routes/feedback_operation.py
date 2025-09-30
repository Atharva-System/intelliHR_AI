from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.models.feedback_model import FeedbackItem, FeedbackResponse
from agents.ai_feedback import evaluate_feedback

router = APIRouter()

@router.post("/evaluate-feedback", response_model=FeedbackResponse)
def analyze_feedback(feedback: list[FeedbackItem]):
    try:
        response = evaluate_feedback(feedback)
        return response
    except Exception as e:
        logging.error(f"Error evaluating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to evaluate feedback")


