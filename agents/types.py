from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class JobDescriptionOutline(BaseModel):
    keyResponsibilities: List[str] = Field(..., description="List of key responsibilities")
    softSkills: List[str] = Field(..., description="List of soft skills")
    technicalSkills: List[str] = Field(..., description="List of technical skills")
    education: List[str] = Field(..., description="Educational qualifications")
    certifications: Optional[List[str]] = Field(None, description="List of certifications (optional)")
    niceToHave: Optional[List[str]] = Field(None, description="List of nice-to-have skills (optional)")

class JobDescriptionTitleAISujjest(BaseModel):
    title: List[str] = Field(..., description="list of title")

class EnhancekeyResponsibilities(BaseModel):
    keyResponsibilities: List[str] = Field(..., description="List of key responsibilities")

class EnhancesoftSkills(BaseModel):
    softSkills: List[str] = Field(..., description="List of soft skills")

class EnhancetechnicalSkills(BaseModel):
    technicalSkills: List[str] = Field(..., description="List of technical skills")  # Fixed typo

class Enhanceeducation(BaseModel):
    education: List[str] = Field(..., description="Educational qualifications")

class Enhancecertifications(BaseModel):
    certifications: Optional[List[str]] = Field(None, description="List of certifications (optional)")

class EnhanceniceToHave(BaseModel):
    niceToHave: Optional[List[str]] = Field(None, description="List of nice-to-have skills (optional)")


class CandidateAllInOne(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    technologies: Optional[List[str]] = None
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    primary_domain: Optional[str] = None
    key_strengths: Optional[List[str]] = None
    career_progression_score: Optional[int] = None
    skill_diversity_score: Optional[int] = None
    good_point: Optional[str]=None