from pydantic import BaseModel
from typing import List

class FeedbackItem(BaseModel):
    id: str
    content: str
    keywords: List[str]

class FeedbackResponse(BaseModel):
    aiRecommendation: str
    concerns: List[str]
    confidenceScore: int
    nextSteps: List[str]
    overallAssessment: str
    strengths: List[str]
    suggestedRating: int
