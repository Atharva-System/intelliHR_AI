from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RecommendationEnum(str, Enum):
    STRONG_HIRE = "strong_hire"
    HIRE = "hire"
    MAYBE = "maybe"
    NO_HIRE = "no_hire"


class InterviewSummaryRequest(BaseModel):
    """Input model for interview evaluation"""
    technicalSkills: Optional[str] = None
    communicationCollaboration: Optional[str] = None
    culturalFitValues: Optional[str] = None
    problemSolvingCriticalThinking: Optional[str] = None
    keyStrengthsHighlights: Optional[str] = None
    additionalObservations: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Output model for interview evaluation"""
    recommendation: RecommendationEnum = Field(..., description="Final hiring recommendation")
    confidenceScore: int = Field(..., ge=1, le=100, description="Confidence score from 1-100")