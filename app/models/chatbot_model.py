from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# -----------------------------
# Nested Structures
# -----------------------------

class SkillItem(BaseModel):
    name: str
    level: Optional[str] = None
    rating: Optional[int] = None

class TechnicalSkills(BaseModel):
    skills: List[SkillItem]

class SoftSkills(BaseModel):
    skills: List[SkillItem]

class EducationItem(BaseModel):
    degree: str
    field: str
    institute: str
    year: int

class Qualification(BaseModel):
    education: List[EducationItem]

class CandidateTag(BaseModel):
    tags: List[str]

class AiAnalysis(BaseModel):
    summary: str
    keywords: List[str]

class WorkExperienceItem(BaseModel):
    companyName: str
    title: str
    duration: str

class WorkExperience(BaseModel):
    companies: List[WorkExperienceItem]

# -----------------------------
# Candidate Data Model
# -----------------------------
class CandidateDataContext(BaseModel):
    candidateId: str
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    currentTitle: Optional[str] = None
    experienceLevel: Optional[str] = None
    experienceYear: Optional[int] = None
    experienceRange: Optional[int] = None
    technicalSkills: Optional[TechnicalSkills] = None
    softSkills: Optional[SoftSkills] = None
    qualification: Optional[Qualification] = None
    candidateTag: Optional[CandidateTag] = None
    aiAnalysis: Optional[AiAnalysis] = None
    workExperience: Optional[WorkExperience] = None
    linkedInUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None
    status: Optional[int] = None
    managerStatus: Optional[int] = None
    isHrShortlisted: bool = False

# -----------------------------
# Matching Data Model
# -----------------------------
class MatchedSkill(BaseModel):
    skill: str
    score: float

class MatchDetails(BaseModel):
    matchedSkills: List[MatchedSkill]
    unmatchedSkills: List[str]

class AiInsights(BaseModel):
    summary: str
    suggestedRole: str
    recommendation: str

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