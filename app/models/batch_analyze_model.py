from typing import List, Optional
from pydantic import BaseModel, EmailStr

class JobRequest(BaseModel):
    job_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    experience_level: Optional[str]
    technical_skills: Optional[List[str]]
    responsibilities: Optional[List[str]]
    softSkills: Optional[List[str]]
    qualification: Optional[List[str]]

class CandidateRequest(BaseModel):
    candidateId: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    location: Optional[str]
    experience_level: Optional[str]
    technical_skills: Optional[List[str]]
    softSkills: Optional[List[str]]
    qualification: Optional[List[str]]

class JobCandidateData(BaseModel):
    jobs: Optional[List[JobRequest]]
    candidates: Optional[List[CandidateRequest]]
    threshold: Optional[int] = 50

    
class Skill(BaseModel):
    name: Optional[str]
    level: Optional[str]
    yearsOfExperience: Optional[int]
    isVerified: Optional[bool]

class Strength(BaseModel):
    category: Optional[str]
    point: Optional[str]
    impact: Optional[str]
    weight: Optional[int]

class SkillMatch(BaseModel):
    jobRequirement: Optional[str]
    candidateSkill: Optional[str]
    matchStrength: Optional[str]
    confidenceScore: Optional[float]

class AIInsights(BaseModel):
    coreSkillsScore: Optional[float]
    experienceScore: Optional[float]
    culturalFitScore: Optional[float]
    strengths: Optional[List[Strength]]
    concerns: Optional[List[str]]
    uniqueQualities: Optional[List[str]]
    skillMatches: Optional[List[SkillMatch]]
    skillGaps: Optional[List[str]]
    recommendation: Optional[str]
    confidenceLevel: Optional[float]
    reasoningSummary: Optional[str]

class CandidateAnalysisResponse(BaseModel):
    id: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    currentTitle: Optional[str]
    experienceYears: Optional[int]
    skills: Optional[List[Skill]]
    availability: Optional[str]
    matchScore: Optional[float]
    aiInsights: Optional[AIInsights]
    lastAnalyzedAt: Optional[str]
    applicationStatus: Optional[str]
    isShortlisted: Optional[bool]
    notes: Optional[List[str]]

class Config:
        orm_mode = True