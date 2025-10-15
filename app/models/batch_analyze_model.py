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
    job_tag: Optional[List[str]]

class CandidateRequest(BaseModel):
    candidateId: Optional[str]
    currentTitle: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    location: Optional[str]
    experience_level: Optional[str]
    experience_year: Optional[float]=None
    technical_skills: Optional[List[str]]
    softSkills: Optional[List[str]]
    qualification: Optional[List[str]]
    candidate_tag: Optional[List[str]]

class JobCandidateData(BaseModel):
    jobs: Optional[List[JobRequest]]
    candidates: Optional[List[CandidateRequest]]
    threshold: Optional[int] = 50

    
class Strength(BaseModel):
    category: Optional[str] = None
    point: Optional[str] = None
    impact: Optional[str] = None
    weight: Optional[float] = 0.0  

class SkillMatch(BaseModel):
    jobRequirement: Optional[str] = None
    candidateSkill: Optional[str] = None
    matchStrength: Optional[str] = None
    confidenceScore: Optional[float] = 0.0

class AIInsights(BaseModel):
    coreSkillsScore: Optional[float] = 0.0
    experienceScore: Optional[float] = 0.0
    culturalFitScore: Optional[float] = 0.0
    strengths: Optional[List[Strength]] = []
    concerns: Optional[List[str]] = []
    uniqueQualities: Optional[List[str]] = []
    skillMatches: Optional[List[SkillMatch]] = []
    skillGaps: Optional[List[str]] = []
    recommendation: Optional[str] = None
    confidenceLevel: Optional[float] = 0.0
    reasoningSummary: Optional[str] = None

class CandidateAnalysisResponse(BaseModel):
    id: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    currentTitle: Optional[str] = None
    experienceYears: Optional[float] = None
    skills: Optional[List[dict]] = []
    availability: Optional[str] = None
    matchScore: Optional[float] = 0.0
    aiInsights: Optional[AIInsights] = AIInsights()
    lastAnalyzedAt: Optional[str] = None
    applicationStatus: Optional[str] = "screening"
    isShortlisted: Optional[bool] = False
    notes: Optional[List[str]] = []