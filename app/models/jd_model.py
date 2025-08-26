from pydantic import BaseModel, Field
from typing import Optional, List


class JobInput(BaseModel):
    title: str
    experienceRange: str
    department: str
    subDepartment: Optional[str] = None

class JobTitleAISujjestInput(BaseModel):
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
    keyResponsibilities: Optional[List[str]] = None
    softSkills: Optional[List[str]] = None
    technicalSkills: Optional[List[str]] = None
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    niceToHave: Optional[List[str]] = None