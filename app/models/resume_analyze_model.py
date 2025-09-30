from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class JobRequirement(BaseModel):
    job_id: str
    title: str
    description: str
    experience_level: str
    technical_skills: List[str]
    responsibilities: List[str] = []
    softSkills: List[str] = []
    qualification: list[str, Any] = {}

class CandidateResume(BaseModel):
    candidate_id: str
    resumeBase64: str

class BatchAnalyzeResumeRequest(BaseModel):
    jobs: JobRequirement
    candidates: List[CandidateResume]
    threshold: int

class SkillDetail(BaseModel):
    name: str
    level: str
    yearsOfExperience: int
    isVerified: bool = False

class StrengthPoint(BaseModel):
    category: str
    point: str
    impact: str
    weight: int

class SkillMatchDetail(BaseModel):
    jobRequirement: str
    candidateSkill: str
    matchStrength: str
    confidenceScore: int

class AIInsights(BaseModel):
    coreSkillsScore: int
    experienceScore: int
    culturalFitScore: int
    strengths: List[StrengthPoint]
    concerns: List[str] = []
    uniqueQualities: List[str] = []
    skillMatches: List[SkillMatchDetail]
    skillGaps: List[str] = []
    recommendation: str
    confidenceLevel: int
    reasoningSummary: str

class AnalyzedCandidateResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    phone: str
    currentTitle: str
    experienceYears: int
    skills: List[SkillDetail]
    availability: str = "unknown"
    matchScore: int
    aiInsights: AIInsights
    lastAnalyzedAt: str
    applicationStatus: str = "screening"
    isShortlisted: bool = False
    notes: List[str] = []

class Job(BaseModel):
    job_id: str
    title: str
    description: str
    department: str
    experience_level: str
    technical_skills: List[str]

class PersonalInfo(BaseModel):
    full_name: str
    email: str
    location: str

class CandidateSkills(BaseModel):
    technical_skills: List[str]
    soft_skills: Optional[List[str]] = None

class CandidateAIAnalysis(BaseModel):
    experience_level: str
    primary_domain: Optional[str] = None

class ParsedData(BaseModel):
    personal_info: PersonalInfo
    skills: CandidateSkills
    ai_analysis: CandidateAIAnalysis

class Candidate(BaseModel):
    candidate_id: str
    name: str
    email: str
    location: str
    experience_level: str
    technical_skills: List[str]
    application_status: str
    parsed_data: ParsedData

class Options(BaseModel):
    minimum_score: int
    include_skill_analysis: bool

class BatchAnalyzeRequest(BaseModel):
    jobs: List[Job]
    candidates: List[Candidate]
    options: Options

class SkillMatch(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    skill_gap_percentage: int

class ExperienceMatch(BaseModel):
    years_requirement_met: bool
    experience_level_fit: str

class AISummary(BaseModel):
    score: int
    overall_match: str
    skill_match: SkillMatch
    experience_match: ExperienceMatch

class AnalyzedCandidate(BaseModel):
    candidate_id: str
    name: str
    email: str
    ai_score: int
    ai_summary: AISummary
    location: Optional[str] = ""
    experience_level: Optional[str] = ""
    primary_domain: Optional[str] = ""
    application_status: str
    analyzed_at: datetime

class BatchAnalyzeResponse(BaseModel):
    job_id: str
    job_title: str
    candidates: List[AnalyzedCandidate]
    analyzed_at: datetime
    total_sourced_candidates: int
    matching_candidates: int
    average_score: int
    
class JobAiQuestion(BaseModel):
    job_id: str
    title: str
    description: str
    experience_level: str
    technical_skills: List[str]
    responsibilities: List[str]
    softSkills: List[str]
    qualification: List[str]


class CandidateAiQuestion(BaseModel):
    candidateId: str
    experience_level: str
    technical_skills: List[str]
    softSkills: List[str]

class AIQuestionRequest(BaseModel):
    jobs: JobAiQuestion
    candidates: CandidateAiQuestion

class ExperienceMatch(BaseModel):
    years_requirement_met: bool
    experience_level_fit: str

class SkillMatch(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    skill_gap_percentage: int

class Summary(BaseModel):
    experience_match: ExperienceMatch
    overall_match: str
    skill_match: SkillMatch

class Advice(BaseModel):
    interview_focus_areas: List[str]
    next_steps: List[str]
    questions_to_ask: List[str]

class AIQuestionResponse(BaseModel):
    ai_score: int
    summary: Summary
    advice: Advice