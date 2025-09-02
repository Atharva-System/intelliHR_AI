from pydantic import BaseModel, Field
from typing import Optional, List


class JobInput(BaseModel):
    title: str
    experienceRange: str
    department: str
    subDepartment: Optional[str] = None

class JobTitleAISuggestInput(BaseModel):
    title: str
    experienceRange: str
    department: str
    subDepartment: Optional[str]
    keyResponsibilities: List[str]
    softSkills: List[str]
    technicalSkills: List[str]
    education: List[str]
    certifications: Optional[List[str]]
    niceToHave: Optional[List[str]]

class JobRefineInput(BaseModel):
    title: str
    experienceRange: str
    department: str
    subDepartment: Optional[str] = None
    keyResponsibilities: Optional[str] = None
    softSkills: Optional[str] = None
    technicalSkills: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    niceToHave: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    keyResponsibilities: List[str]
    softSkills: List[str]
    technicalSkills: List[str]
    education: List[str]
    certifications: Optional[List[str]] = None
    niceToHave: Optional[List[str]] = None

class TitleSuggestionResponse(BaseModel):
    title: List[str]

class ResumeExtractionResponse(BaseModel):
    status: str
    saved_files: List[str]
    extracted_data: List[dict]