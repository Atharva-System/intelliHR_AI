from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# -----------------------------
# Candidate Section
# -----------------------------
class WorkExperienceItem(BaseModel):
    company: Optional[str] = None
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
    skill_diversity_score: Optional[float] = None
    career_progression_score: Optional[float] = None

class CandidateDataContext(BaseModel):
    candidateId: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    currentTitle: Optional[str] = None
    experienceLevel: Optional[str] = None
    experienceYear: Optional[Any] = None
    experienceRange: Optional[float] = None
    technicalSkills: Optional[List[str]] = None
    softSkills: Optional[List[str]] = None
    qualification: Optional[List[Any]] = None
    candidateTag: Optional[Any] = None
    aiAnalysis: Optional[AiAnalysis] = None
    workExperience: Optional[List[WorkExperienceItem]] = None
    linkedInUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None
    status: Optional[float] = None
    managerStatus: Optional[float] = None
    isHrShortlisted: Optional[bool] = False

# -----------------------------
# Matching Section
# -----------------------------
class SkillItem(BaseModel):
    name: Optional[str]
    level: Optional[str] = None
    isVerified: Optional[bool] = None
    yearsOfExperience: Optional[float] = None

class StrengthItem(BaseModel):
    point: Optional[str] = None
    impact: Optional[str] = None
    weight: Optional[float] = None
    category: Optional[str] = None

class SkillMatchItem(BaseModel):
    matchStrength: Optional[str] = None
    candidateSkill: Optional[str] = None
    jobRequirement: Optional[str] = None
    confidenceScore: Optional[float] = None

class AiInsights(BaseModel):
    concerns: Optional[List[str]] = None
    skillGaps: Optional[List[str]] = None
    strengths: Optional[List[StrengthItem]] = None
    skillMatches: Optional[List[SkillMatchItem]] = None
    recommendation: Optional[str] = None
    confidenceLevel: Optional[float] = None
    coreSkillsScore: Optional[float] = None
    experienceScore: Optional[float] = None
    uniqueQualities: Optional[List[str]] = None
    culturalFitScore: Optional[float] = None
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
    matchScore: Optional[float] = None
    availability: Optional[str] = None
    currentTitle: Optional[str] = None
    isShortlisted: Optional[bool] = None
    lastAnalyzedAt: Optional[datetime] = None
    experienceYears: Optional[float] = None
    applicationStatus: Optional[str] = None

class AIMatchingDataContext(BaseModel):
    id: Optional[str] = None
    jobId: Optional[str] = None
    candidateId: Optional[str] = None
    jobTitle: Optional[str] = None
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
    question: Optional[str] = None

class ChatResponse(BaseModel):
    answer: Optional[str] = None