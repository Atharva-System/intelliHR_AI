from pydantic import BaseModel, Field
from typing import Optional, List


class JobDescriptionOutline(BaseModel):
    keyResponsibilities: List[str] = Field(..., description="List of key responsibilities")
    softSkills: List[str] = Field(..., description="List of soft skills")
    technicalSkills: List[str] = Field(..., description="List of technical skills")
    education: List[str] = Field(..., description="Educational qualifications")
    certifications: Optional[List[str]] = Field(None, description="List of certifications (optional)")
    niceToHave: Optional[List[str]] = Field(None, description="List of nice-to-have skills (optional)")
