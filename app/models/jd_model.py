from pydantic import BaseModel, Field
from typing import Optional, List


class JobInput(BaseModel):
    title: Optional[str] = None
    experienceRange: Optional[str] = None
    department: Optional[str] = None
    subDepartment: Optional[str] = None

class JobTitleAISuggestInput(BaseModel):
    title: Optional[str] = None
    experienceRange: Optional[str] = None
    department: Optional[str] = None
    subDepartment: Optional[str]= None
    keyResponsibilities:Optional[List[str]]= None
    softSkills:Optional[List[str]]= None
    technicalSkills: Optional[List[str]]= None
    education: Optional[List[str]]= None
    certifications: Optional[List[str]]= None
    niceToHave:Optional[List[str]]= None

class JobRefineInput(BaseModel):
    title: Optional[str] = None
    experienceRange: Optional[str] = None
    department: Optional[str] = None
    subDepartment: Optional[str] = None
    keyResponsibilities: Optional[str] = None
    softSkills: Optional[str] = None
    technicalSkills: Optional[str] = None
    education: Optional[str] = None
    certifications: Optional[str] = None
    niceToHave: Optional[str] = None

class JobDescriptionResponse(BaseModel):
    keyResponsibilities: Optional[List[str]]= None
    softSkills: Optional[List[str]]= None
    technicalSkills: Optional[List[str]]= None
    education: Optional[List[str]]= None
    certifications: Optional[List[str]] = None
    niceToHave: Optional[List[str]] = None

class TitleSuggestionResponse(BaseModel):
    title: Optional[List[str]]= None

class ResumeExtractionResponse(BaseModel):
    status: Optional[str]= None
    saved_files: Optional[List[str]]= None
    extracted_data: Optional[List[dict]]= None