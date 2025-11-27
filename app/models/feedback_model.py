from pydantic import BaseModel
from typing import List, Optional



class FeedbackItem(BaseModel):
    id: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[List[str]] = None


class FeedbackResponse(BaseModel):
    aiRecommendation: Optional[str] = None
    concerns: Optional[List[str]] = None
    confidenceScore: Optional[int] = None
    nextSteps: Optional[List[str]] = None
    overallAssessment: Optional[str] = None
    strengths: Optional[List[str]] = None
    suggestedRating: Optional[int] = None




class EnhanceFeedbackRequest(BaseModel):
    text: Optional[str] = None
    context: Optional[str] = None
    action: Optional[str] = None


class EnhanceFeedbackResponse(BaseModel):
    enhanced: Optional[str] = None