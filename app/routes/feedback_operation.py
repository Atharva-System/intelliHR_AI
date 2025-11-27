from fastapi import APIRouter, HTTPException
from typing import List
import logging
from app.models.feedback_model import EnhanceFeedbackRequest, EnhanceFeedbackResponse
from agents.ai_feedback import enhance_feedback
from app.models.evaluation_model import InterviewSummaryRequest, EvaluationResponse
from agents.evaluation_agent import evaluate_interview

router = APIRouter()

@router.post("/evaluate-feedback", response_model=EnhanceFeedbackResponse)
def analyze_feedback(feedback:EnhanceFeedbackRequest):
    try:
        response = enhance_feedback(feedback)
        return response
    except Exception as e:
        logging.error(f"Error evaluating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to evaluate feedback")

@router.post("/evaluate-interview", response_model=EvaluationResponse)
def evaluate_interview_feedback(request: InterviewSummaryRequest):
    try:
        response = evaluate_interview(request)
        return response
    except Exception as e:
        logging.error(f"Error evaluating interview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to evaluate interview")
