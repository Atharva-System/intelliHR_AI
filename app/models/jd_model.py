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
