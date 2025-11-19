from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class JobDescriptionOutline(BaseModel):
    keyResponsibilities: Optional[List[str]] = Field(..., description="List of key responsibilities")
    softSkills: Optional[List[str]] = Field(..., description="List of soft skills")
    technicalSkills: Optional[List[str]] = Field(..., description="List of technical skills")
    education: Optional[List[str]] = Field(..., description="Educational qualifications")
    certifications: Optional[List[str]] = Field(None, description="List of certifications (optional)")
    niceToHave: Optional[List[str]] = Field(None, description="List of nice-to-have skills (optional)")

class JobDescriptionTitleAISuggest(BaseModel):
    title: Optional[List[str]] = Field(..., description="list of title")

class EnhancekeyResponsibilities(BaseModel):
    keyResponsibilities: Optional[List[str]] = Field(..., description="List of key responsibilities")

class EnhancesoftSkills(BaseModel):
    softSkills: Optional[List[str]] = Field(..., description="List of soft skills")

class EnhancetechnicalSkills(BaseModel):
    technicalSkills: Optional[List[str]] = Field(..., description="List of technical skills")  # Fixed typo

class Enhanceeducation(BaseModel):
    education: Optional[List[str]] = Field(..., description="Educational qualifications")

class Enhancecertifications(BaseModel):
    certifications: Optional[List[str]] = Field(None, description="List of certifications (optional)")

class EnhanceniceToHave(BaseModel):
    niceToHave: Optional[List[str]] = Field(None, description="List of nice-to-have skills (optional)")


class PersonalInfo(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class WorkExperience(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None


class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class Skills(BaseModel):
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None


class AIAnalysis(BaseModel):
    experience_level: Optional[str] = None
    experience_year: Optional[float] = None
    primary_domain: Optional[str] = None
    key_strengths: Optional[List[str]] = None
    career_progression_score: Optional[int] = None
    skill_diversity_score: Optional[int] = None
    good_point: Optional[str] = None


class CandidateAllInOne(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    work_experience: Optional[List[WorkExperience]] = None
    education: Optional[List[Education]] = None
    skills: Optional[Skills] = None
    ai_analysis: Optional[AIAnalysis] = None
    tags: Optional[List[str]] = []


class AskAI(BaseModel):
    response: str

class FeedbackResponse(BaseModel):
    aiRecommendation: Optional[str] = Field(..., description="Final recommendation like yes/no/maybe")
    concerns: Optional[List[str]] = Field(..., description="List of concerns about the candidate")
    confidenceScore: Optional[int] = Field(..., description="Confidence score (0-100)")
    nextSteps: Optional[List[str]] = Field(..., description="List of next steps to take")
    overallAssessment: Optional[str] = Field(..., description="Overall summary assessment of the candidate")
    strengths: Optional[List[str]] = Field(..., description="List of strengths identified")
    suggestedRating: Optional[int] = Field(..., description="Suggested rating on a scale (e.g. 1-5)")

class JobDescriptionInput(BaseModel):
    title: Optional[str]
    experienceRange: Optional[str]
    job_description: Optional[str]
    key_responsibility: Optional[List[str]]
    technical_skill: Optional[List[str]]
    soft_skill: Optional[List[str]]
    education: Optional[List[str]]
    nice_to_have: Optional[List[str]]


class JobTagsOutput(BaseModel):
    tags: Optional[List[str]]