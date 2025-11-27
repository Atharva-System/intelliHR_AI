from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class JobRequirement(BaseModel):
    job_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    experience_level: Optional[str] = None
    technical_skills: Optional[List[str]]=None
    responsibilities: Optional[List[str]]=None
    softSkills: Optional[List[str]]=None
    qualification: Optional[list[str, Any]] = {}

class CandidateResume(BaseModel):
    candidate_id: Optional[str] = None
    resumeBase64: Optional[str] = None

class BatchAnalyzeResumeRequest(BaseModel):
    jobs: JobRequirement
    candidates: List[CandidateResume]
    threshold: Optional[int]=None

class SkillDetail(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    isVerified: Optional[bool] = False

class StrengthPoint(BaseModel):
    category: Optional[str]= None
    point: Optional[str]= None
    impact: Optional[str]= None
    weight: Optional[int]= None

class SkillMatchDetail(BaseModel):
    jobRequirement: Optional[str]= None
    candidateSkill: Optional[str]= None
    matchStrength: Optional[str]= None
    confidenceScore: Optional[int]= None

class AIInsights(BaseModel):
    coreSkillsScore: Optional[int]= None
    experienceScore: Optional[int]= None
    culturalFitScore: Optional[int]= None
    strengths: List[StrengthPoint]
    concerns: Optional[List[str]]=None
    uniqueQualities: Optional[List[str]]=None
    skillMatches: List[SkillMatchDetail]
    skillGaps: Optional[List[str]]=None
    recommendation: Optional[str] = None
    confidenceLevel: Optional[int]= None
    reasoningSummary: Optional[str] = None

class AnalyzedCandidateResponse(BaseModel):
    id: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    currentTitle: Optional[str] = None
    experienceYears: Optional[int]= None
    skills: List[SkillDetail]
    availability: Optional[str] = "unknown"
    matchScore: Optional[int]= None
    aiInsights: AIInsights
    lastAnalyzedAt: Optional[str] = None
    applicationStatus: Optional[str] = "screening"
    isShortlisted: Optional[bool] = False
    notes: Optional[List[str]]=None

class Job(BaseModel):
    job_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    experience_level: Optional[str] = None
    technical_skills: Optional[List[str]]=None

class PersonalInfo(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None

class CandidateSkills(BaseModel):
    technical_skills: Optional[List[str]]=None
    soft_skills: Optional[List[str]] = None

class CandidateAIAnalysis(BaseModel):
    experience_level: Optional[str] = None
    primary_domain: Optional[str] = None

class ParsedData(BaseModel):
    personal_info: PersonalInfo
    skills: CandidateSkills
    ai_analysis: CandidateAIAnalysis

class Candidate(BaseModel):
    candidate_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    technical_skills: Optional[List[str]]=None
    application_status: Optional[str] = None
    parsed_data: ParsedData

class Options(BaseModel):
    minimum_score: Optional[int]= None
    include_skill_analysis: Optional[bool]=None

class BatchAnalyzeRequest(BaseModel):
    jobs: List[Job]
    candidates: List[Candidate]
    options: Options

class SkillMatch(BaseModel):
    matched_skills: Optional[List[str]]=None
    missing_skills: Optional[List[str]]=None
    skill_gap_percentage: Optional[int]= None

class ExperienceMatch(BaseModel):
    years_requirement_met: Optional[bool]=None
    experience_level_fit: Optional[str]=None

class AISummary(BaseModel):
    score: Optional[int]= None
    overall_match: Optional[str]=None
    skill_match: SkillMatch
    experience_match: ExperienceMatch

class AnalyzedCandidate(BaseModel):
    candidate_id: Optional[str]=None
    name: Optional[str]=None
    email: Optional[str]=None
    ai_score: Optional[int]= None
    ai_summary: AISummary
    location: Optional[str] = None
    experience_level: Optional[str] = None
    primary_domain: Optional[str] = None
    application_status: Optional[str]=None
    analyzed_at: Optional[datetime]=None

class BatchAnalyzeResponse(BaseModel):
    job_id: Optional[str]=None
    job_title: Optional[str]=None
    candidates: List[AnalyzedCandidate]
    analyzed_at: Optional[datetime]=None
    total_sourced_candidates: Optional[int]= None
    matching_candidates: Optional[int]= None
    average_score: Optional[int]= None
    
class JobAiQuestion(BaseModel):
    job_id: Optional[str]=None
    title: Optional[str]=None
    description: Optional[str]=None
    experience_level: Optional[str]=None
    technical_skills: Optional[List[str]]=None
    responsibilities: Optional[List[str]]=None
    softSkills: Optional[List[str]]=None
    qualification: Optional[List[str]]=None


class CandidateAiQuestion(BaseModel):
    candidateId: Optional[str]=None
    experience_level: Optional[str]=None
    technical_skills: Optional[List[str]]=None
    softSkills: Optional[List[str]]=None

class AIQuestionRequest(BaseModel):
    jobs: JobAiQuestion
    candidates: CandidateAiQuestion

class ExperienceMatch(BaseModel):
    years_requirement_met: Optional[bool]=None
    experience_level_fit: Optional[str]=None

class SkillMatch(BaseModel):
    matched_skills: Optional[List[str]]=None
    missing_skills: Optional[List[str]]=None
    skill_gap_percentage: Optional[int]= None

class Summary(BaseModel):
    experience_match: ExperienceMatch
    overall_match: Optional[str]=None
    skill_match: SkillMatch

class Advice(BaseModel):
    interview_focus_areas: Optional[List[str]]=None
    next_steps: Optional[List[str]]=None
    questions_to_ask: Optional[List[str]]=None

class AIQuestionResponse(BaseModel):
    ai_score: Optional[int]= None
    summary: Summary
    advice: Advice

from pydantic import BaseModel
from typing import Optional, List

class AIPromptQuestionRequest(BaseModel):
    prompt: Optional[str] = None

class AIPromptQuestionResponse(BaseModel):
    questions_to_ask: Optional[List[str]] = None