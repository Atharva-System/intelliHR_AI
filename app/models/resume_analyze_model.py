from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


# ---------- Request Models ----------
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


# ---------- Response Models ----------
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