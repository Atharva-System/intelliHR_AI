from typing import List, Optional
from pydantic import BaseModel, EmailStr


class Job(BaseModel):
    job_id: str
    title: str
    description: str
    experience_level: str
    technical_skills: List[str]
    responsibilities: List[str]
    softSkills: List[str]
    qualification: List[str]


class Candidate(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None
    number: Optional[str] = None  
    currentTitle: Optional[str] = None
    experienceYears: int
    skills: List[str]
    availability: Optional[str] = None 


class JobCandidateData(BaseModel):
    jobs: List[Job]
    candidates: List[Candidate]




class Skill(BaseModel):
    name: str
    level: Optional[str] = ""  
    yearsOfExperience: int
    isVerified: bool


class Strength(BaseModel):
    category: str
    point: str
    impact: str
    weight: float  


class SkillMatch(BaseModel):
    jobRequirement: str
    candidateSkill: str
    matchStrength: str
    confidenceScore: float


class AIInsights(BaseModel):
    coreSkillsScore: float
    experienceScore: float
    culturalFitScore: float
    strengths: List[Strength]
    concerns: List[str]
    uniqueQualities: List[str]
    skillMatches: List[SkillMatch]
    skillGaps: List[str]
    recommendation: str
    confidenceLevel: float
    reasoningSummary: str


class BatchAnalyzeCandidateResponse(BaseModel):
    job_id: str
    id: str
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None
    number: Optional[str] = None  
    currentTitle: Optional[str] = None
    experienceYears: int
    skills: List[Skill]
    availability: Optional[str] = None
    matchScore: float
    aiInsights: AIInsights
    lastAnalyzedAt: str
    notes: List[str]
