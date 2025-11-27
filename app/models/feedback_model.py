from pydantic import BaseModel
from typing import List, Optional

class EnhanceFeedbackRequest(BaseModel):
    text: Optional[str] = None
    context: Optional[str] = None
    action: Optional[str] = None


class EnhanceFeedbackResponse(BaseModel):
    enhanced: Optional[str] = None