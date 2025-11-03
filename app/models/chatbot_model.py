from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# -----------------------------
# Candidate Section
# -----------------------------
class WorkExperienceItem(BaseModel):
    company: str
    end_date: Optional[str] = None
    position: Optional[str] = None
    is_current: Optional[bool] = None
    start_date: Optional[str] = None

class AiAnalysis(BaseModel):
    good_point: Optional[str] = None
    key_strengths: Optional[List[str]] = None
    primary_domain: Optional[str] = None
    experience_year: Optional[float] = None
    experience_level: Optional[str] = None
    skill_diversity_score: Optional[int] = None
    career_progression_score: Optional[int] = None

class CandidateDataContext(BaseModel):
    candidateId: str
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    currentTitle: Optional[str] = None
    experienceLevel: Optional[str] = None
    experienceYear: Optional[Any] = None
    experienceRange: Optional[int] = None
    technicalSkills: Optional[List[str]] = None
    softSkills: Optional[List[str]] = None
    qualification: Optional[List[Any]] = None
    candidateTag: Optional[Any] = None
    aiAnalysis: Optional[AiAnalysis] = None
    workExperience: Optional[List[WorkExperienceItem]] = None
    linkedInUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None
    status: Optional[int] = None
    managerStatus: Optional[int] = None
    isHrShortlisted: bool = False

# -----------------------------
# Matching Section
# -----------------------------
class SkillItem(BaseModel):
    name: str
    level: Optional[str] = None
    isVerified: Optional[bool] = None
    yearsOfExperience: Optional[float] = None

class StrengthItem(BaseModel):
    point: str
    impact: str
    weight: float
    category: str

class SkillMatchItem(BaseModel):
    matchStrength: str
    candidateSkill: str
    jobRequirement: str
    confidenceScore: int

class AiInsights(BaseModel):
    concerns: Optional[List[str]] = None
    skillGaps: Optional[List[str]] = None
    strengths: Optional[List[StrengthItem]] = None
    skillMatches: Optional[List[SkillMatchItem]] = None
    recommendation: Optional[str] = None
    confidenceLevel: Optional[int] = None
    coreSkillsScore: Optional[int] = None
    experienceScore: Optional[int] = None
    uniqueQualities: Optional[List[str]] = None
    culturalFitScore: Optional[int] = None
    reasoningSummary: Optional[str] = None

class MatchDetails(BaseModel):
    Id: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[List[str]] = None
    phone: Optional[str] = None
    skills: Optional[List[SkillItem]] = None
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    aiInsights: Optional[AiInsights] = None
    matchScore: Optional[int] = None
    availability: Optional[str] = None
    currentTitle: Optional[str] = None
    isShortlisted: Optional[bool] = None
    lastAnalyzedAt: Optional[datetime] = None
    experienceYears: Optional[float] = None
    applicationStatus: Optional[str] = None

class AIMatchingDataContext(BaseModel):
    id: str
    jobId: str
    candidateId: str
    jobTitle: str
    overallMatchScore: Optional[float] = None
    technicalMatchScore: Optional[float] = None
    experienceMatchScore: Optional[float] = None
    softSkillsMatchScore: Optional[float] = None
    matchDetails: Optional[MatchDetails] = None
    aiInsights: Optional[AiInsights] = None
    createdOn: Optional[datetime] = None

# -----------------------------
# Combined Model for Request
# -----------------------------
class CandidateMatchingRequest(BaseModel):
    candidate: CandidateDataContext
    matchingData: AIMatchingDataContext


class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str