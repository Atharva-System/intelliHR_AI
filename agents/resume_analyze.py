import json
from typing import List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
import base64
import tempfile
import os
import re

from pydantic import BaseModel

from app.models.jd_model import JobTitleAISuggestInput
from app.services.text_extract import pdf_to_text
from app.models.resume_analyze_model import (
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    AnalyzedCandidate,
    AISummary,
    SkillMatch,
    ExperienceMatch,
    BatchAnalyzeResumeRequest,
    AnalyzedCandidateResponse,
    SkillDetail,
    AIInsights,
    StrengthPoint,
    SkillMatchDetail
)
from config.Settings import settings
from agents.resume_extractor import resume_info

from datetime import datetime

key = settings.api_key
model = settings.model

def detect_file_type_from_bytes(file_bytes: bytes) -> str:
    if not file_bytes or len(file_bytes) < 8:
        return ""

    if file_bytes.startswith(b"%PDF-"):
        return "application/pdf"

    if file_bytes[:8] == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
        return "application/msword"

    if file_bytes[:2] == b"PK":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return ""

def extract_resume_from_base64(resume_base64: str, candidate_id: str) -> dict:
    try:
        # Remove data URI prefix if present
        resume_base64 = resume_base64.split(",", 1)[-1] if resume_base64.startswith("data:") else resume_base64
        # Check for valid base64 characters
        if not re.match(r'^[A-Za-z0-9+/=]+$', resume_base64):
            raise ValueError(f"Invalid base64 characters for candidate {candidate_id}")

        resume_data = base64.b64decode(resume_base64, validate=True)
        
        # Detect file type
        detected_mime = detect_file_type_from_bytes(resume_data)
        if detected_mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            suffix = '.docx'
        elif detected_mime == "application/msword":
            suffix = '.doc'
        elif detected_mime == "application/pdf":
            suffix = '.pdf'
        else:
            raise ValueError(f"Unsupported file type for candidate {candidate_id}: {detected_mime}")

        # Create temporary file with appropriate suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(resume_data)
            temp_file_path = temp_file.name
        
        try:
            extracted_data = resume_info(temp_file_path)
            return extracted_data
        finally:
            os.unlink(temp_file_path)
            
    except base64.binascii.Error as e:
        print(f"Error decoding base64 for candidate {candidate_id}: {str(e)}")
        return {}
    except Exception as e:
        print(f"Error extracting resume for candidate {candidate_id}: {str(e)}")
        return {}

def resume_score_from_base64(request: BatchAnalyzeResumeRequest) -> List[AnalyzedCandidateResponse]:
    llm = GoogleGenerativeAI(
        model=model,
        google_api_key=key,
        temperature=0.2,
        max_output_tokens=5000
    )

    class AISummaryEnhanced(BaseModel):
        score: int
        overall_match: str
        core_skills_score: int
        experience_score: int
        cultural_fit_score: int
        strengths: List[dict]
        skill_matches: List[dict]
        skill_gaps: List[str]
        recommendation: str
        reasoning_summary: str

    parser = PydanticOutputParser(pydantic_object=AISummaryEnhanced)

    prompt = PromptTemplate(
        template="""
        You are a professional recruiter. Evaluate this candidate's resume against the job description.
        Provide a comprehensive analysis with specific metrics.

        Job Requirement:
        Title: {job_title}
        Experience Level: {experience_level}
        Description: {job_description}
        Technical Skills Required: {technical_skills}
        Responsibilities: {responsibilities}
        Soft Skills: {soft_skills}

        Resume Data:
        {resume_data}

        Return **strict JSON** with the following format:

        {format_instructions}

        IMPORTANT: For skill_matches, each item must have these exact field names:
        - jobRequirement: string (the required skill from job description)
        - candidateSkill: string (the matching skill from candidate's resume)  
        - matchStrength: string (exact, strong, partial, weak, none)
        - confidenceScore: integer (0-100)

        Key evaluation criteria:
        - Score (0-100): Overall match percentage
        - Core skills score (0-100): Match on technical skills
        - Experience score (0-100): Match on experience level and years
        - Cultural fit score (0-100): Match on soft skills and company culture
        - Strengths: Specific strengths with category, point, impact, and weight (1-10)
        - Skill matches: Detailed skill-by-skill matching with exact field names as specified
        - Skill gaps: Missing required skills
        - Recommendation: "highly-recommended", "recommended", "consider", "not-recommended"
        """,
        input_variables=["job_title", "experience_level", "job_description", 
                        "technical_skills", "responsibilities", "soft_skills", "resume_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    results: List[AnalyzedCandidateResponse] = []

    for candidate in request.candidates:
        try:
            print(f"Extracting resume for candidate {candidate.candidate_id}")
            resume_data = extract_resume_from_base64(candidate.resumeBase64, candidate.candidate_id)
            
            if not resume_data:
                default_candidate = create_default_candidate_response(candidate.candidate_id)
                results.append(default_candidate)
                continue

            resume_text = format_resume_data_for_llm(resume_data)

            response = chain.invoke({
                "job_title": request.jobs.title,
                "experience_level": request.jobs.experience_level,
                "job_description": request.jobs.description,
                "technical_skills": ", ".join(request.jobs.technical_skills),
                "responsibilities": ", ".join(request.jobs.responsibilities),
                "soft_skills": ", ".join(request.jobs.softSkills),
                "resume_data": resume_text
            })

            print("LLM raw output:", response["text"])

            try:
                ai_summary = parser.parse(response["text"])
                analyzed_candidate = create_analyzed_candidate_response(
                    candidate.candidate_id, resume_data, ai_summary
                )
                results.append(analyzed_candidate)

            except Exception as e:
                print("Parsing failed, trying manual extraction:", str(e))
                analyzed_candidate = parse_llm_output_manually(response["text"], candidate.candidate_id, resume_data)
                results.append(analyzed_candidate)

        except Exception as e:
            print(f"Error processing candidate {candidate.candidate_id}: {str(e)}")
            default_candidate = create_default_candidate_response(candidate.candidate_id)
            results.append(default_candidate)

    return results

def parse_llm_output_manually(llm_output: str, candidate_id: str, resume_data: dict) -> AnalyzedCandidateResponse:
    """Manually parse LLM output when automatic parsing fails"""
    try:
        import re
        import json
        
        json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
        else:
            data = {}
        
        score = data.get('score', 0)
        overall_match = data.get('overall_match', 'Analysis completed')
        
        skill_matches = []
        for match in data.get('skill_matches', []):
            skill_matches.append(SkillMatchDetail(
                jobRequirement=match.get('jobRequirement') or match.get('skill', 'Unknown requirement'),
                candidateSkill=match.get('candidateSkill') or match.get('details', 'Unknown skill'),
                matchStrength=match.get('matchStrength') or match.get('match', 'partial'),
                confidenceScore=match.get('confidenceScore') or 50
            ))
        
        strengths = []
        for strength in data.get('strengths', []):
            strengths.append(StrengthPoint(
                category=strength.get('category', 'Technical Skills'),
                point=strength.get('point', ''),
                impact=strength.get('impact', ''),
                weight=strength.get('weight', 5)
            ))
        
        ai_insights = AIInsights(
            coreSkillsScore=data.get('core_skills_score', score),
            experienceScore=data.get('experience_score', score),
            culturalFitScore=data.get('cultural_fit_score', score),
            strengths=strengths,
            concerns=data.get('skill_gaps', []),
            uniqueQualities=[],
            skillMatches=skill_matches,
            skillGaps=data.get('skill_gaps', []),
            recommendation=data.get('recommendation', 'consider'),
            confidenceLevel=score,
            reasoningSummary=data.get('reasoning_summary', overall_match)
        )
        
        personal_info = resume_data.get('personal_info', {})
        name_parts = personal_info.get('full_name', 'Unknown Unknown').split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        
        skills_list = []
        technical_skills = resume_data.get('skills', {}).get('technical_skills', [])
        for skill in technical_skills[:10]:
            skills_list.append(SkillDetail(
                name=skill,
                level="intermediate",
                yearsOfExperience=2,
                isVerified=False
            ))
        
        return AnalyzedCandidateResponse(
            id=candidate_id,
            firstName=first_name,
            lastName=last_name,
            email=personal_info.get('email', ''),
            phone=personal_info.get('phone', ''),
            currentTitle=extract_current_title(resume_data),
            experienceYears=calculate_experience_years(resume_data),
            skills=skills_list,
            matchScore=score,
            aiInsights=ai_insights,
            lastAnalyzedAt=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        print(f"Manual parsing also failed: {str(e)}")
        return create_default_candidate_response(candidate_id, resume_data)

def format_resume_data_for_llm(resume_data: dict) -> str:
    text_parts = []
    
    if resume_data.get('personal_info'):
        pi = resume_data['personal_info']
        text_parts.append(f"Name: {pi.get('full_name', 'N/A')}")
        text_parts.append(f"Email: {pi.get('email', 'N/A')}")
        text_parts.append(f"Phone: {pi.get('phone', 'N/A')}")
        text_parts.append(f"Location: {pi.get('location', 'N/A')}")
    
    if resume_data.get('work_experience'):
        text_parts.append("\nWork Experience:")
        for exp in resume_data['work_experience']:
            text_parts.append(f"- {exp.get('position', 'N/A')} at {exp.get('company', 'N/A')}")
            if exp.get('technologies'):
                text_parts.append(f"  Technologies: {', '.join(exp['technologies'])}")
    
    if resume_data.get('skills'):
        skills = resume_data['skills']
        if skills.get('technical_skills'):
            text_parts.append(f"\nTechnical Skills: {', '.join(skills['technical_skills'])}")
        if skills.get('soft_skills'):
            text_parts.append(f"Soft Skills: {', '.join(skills['soft_skills'])}")
    
    if resume_data.get('education'):
        text_parts.append("\nEducation:")
        for edu in resume_data['education']:
            text_parts.append(f"- {edu.get('degree', 'N/A')} from {edu.get('institution', 'N/A')}")
    
    if resume_data.get('ai_analysis'):
        ai = resume_data['ai_analysis']
        text_parts.append(f"\nAI Analysis: Experience Level: {ai.get('experience_level', 'N/A')}")
        text_parts.append(f"Primary Domain: {ai.get('primary_domain', 'N/A')}")
    
    return "\n".join(text_parts)

def create_analyzed_candidate_response(candidate_id: str, resume_data: dict, ai_summary: any) -> AnalyzedCandidateResponse:
    personal_info = resume_data.get('personal_info', {})
    name_parts = personal_info.get('full_name', 'Unknown Unknown').split(' ', 1)
    first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
    last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
    
    skills_list = []
    technical_skills = resume_data.get('skills', {}).get('technical_skills', [])
    for skill in technical_skills[:10]:
        skills_list.append(SkillDetail(
            name=skill,
            level="intermediate",
            yearsOfExperience=2,
            isVerified=False
        ))
    
    skill_matches = []
    for match in getattr(ai_summary, 'skill_matches', []):
        skill_matches.append(SkillMatchDetail(
            jobRequirement=match.get('jobRequirement', 'Unknown'),
            candidateSkill=match.get('candidateSkill', 'Unknown'),
            matchStrength=match.get('matchStrength', 'partial'),
            confidenceScore=match.get('confidenceScore', 50)
        ))
    
    ai_insights = AIInsights(
        coreSkillsScore=getattr(ai_summary, 'core_skills_score', ai_summary.score),
        experienceScore=getattr(ai_summary, 'experience_score', ai_summary.score),
        culturalFitScore=getattr(ai_summary, 'cultural_fit_score', ai_summary.score),
        strengths=[StrengthPoint(**strength) for strength in getattr(ai_summary, 'strengths', [])],
        concerns=[],
        uniqueQualities=[],
        skillMatches=skill_matches,
        skillGaps=getattr(ai_summary, 'skill_gaps', []),
        recommendation=getattr(ai_summary, 'recommendation', 'consider'),
        confidenceLevel=ai_summary.score,
        reasoningSummary=getattr(ai_summary, 'reasoning_summary', ai_summary.overall_match)
    )
    
    return AnalyzedCandidateResponse(
        id=candidate_id,
        firstName=first_name,
        lastName=last_name,
        email=personal_info.get('email', ''),
        phone=personal_info.get('phone', ''),
        currentTitle=extract_current_title(resume_data),
        experienceYears=calculate_experience_years(resume_data),
        skills=skills_list,
        matchScore=ai_summary.score,
        aiInsights=ai_insights,
        lastAnalyzedAt=datetime.utcnow().isoformat()
    )

def create_default_candidate_response(candidate_id: str, resume_data: dict = None) -> AnalyzedCandidateResponse:
    if resume_data and resume_data.get('personal_info'):
        personal_info = resume_data['personal_info']
        name_parts = personal_info.get('full_name', 'Unknown Unknown').split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        email = personal_info.get('email', '')
        phone = personal_info.get('phone', '')
    else:
        first_name, last_name, email, phone = "Unknown", "Unknown", "", ""
    
    return AnalyzedCandidateResponse(
        id=candidate_id,
        firstName=first_name,
        lastName=last_name,
        email=email,
        phone=phone,
        currentTitle="Unknown",
        experienceYears=0,
        skills=[],
        matchScore=0,
        aiInsights=AIInsights(
            coreSkillsScore=0,
            experienceScore=0,
            culturalFitScore=0,
            strengths=[],
            concerns=["Resume extraction failed"],
            uniqueQualities=[],
            skillMatches=[],
            skillGaps=[],
            recommendation="not-recommended",
            confidenceLevel=0,
            reasoningSummary="Unable to analyze resume due to processing error"
        ),
        lastAnalyzedAt=datetime.utcnow().isoformat()
    )

def extract_current_title(resume_data: dict) -> str:
    if resume_data.get('work_experience'):
        latest_exp = resume_data['work_experience'][0]
        return latest_exp.get('position', 'Unknown')
    return 'Unknown'

def calculate_experience_years(resume_data: dict) -> int:
    if resume_data.get('work_experience'):
        return len(resume_data['work_experience']) * 2
    return 0

def resume_score(request: BatchAnalyzeRequest) -> List[BatchAnalyzeResponse]:
    llm = GoogleGenerativeAI(
        model=model,
        google_api_key=key,
        temperature=0.2,
        max_output_tokens=5000
    )

    parser = PydanticOutputParser(pydantic_object=AISummary)

    prompt = PromptTemplate(
        template="""
        You are a professional recruiter. Evaluate this candidate's resume against the job description.
        If the resume looks AI-generated, mention that in the reason.

        Job Requirement:
        {requirement_data}

        Resume:
        {resume_data}

        Return **strict JSON** with the following format:

        {format_instructions}

        - "score": integer (0–100)
        - "overall_match": string summary
        - "skill_match": matched_skills (list), missing_skills (list), skill_gap_percentage (0–100)
        - "experience_match": years_requirement_met (bool), experience_level_fit (string)
        """,
        input_variables=["requirement_data", "resume_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    results: List[BatchAnalyzeResponse] = []

    for job in request.jobs:
        analyzed_candidates: list[AnalyzedCandidate] = []
        for candidate in request.candidates:

            resume_text = " ".join(candidate.technical_skills)
            requirement_text = job.description + " " + " ".join(job.technical_skills)

            response = chain.invoke({
                "requirement_data": requirement_text,
                "resume_data": resume_text
            })

            print("LLM raw output:", response["text"])

            try:
                ai_summary: AISummary = parser.parse(response["text"])
                ai_score = ai_summary.score
            except Exception as e:
                print("Parsing failed:", str(e))
                ai_summary = AISummary(
                    overall_match="Could not parse",
                    skill_match=SkillMatch(
                        matched_skills=[],
                        missing_skills=[],
                        skill_gap_percentage=100
                    ),
                    experience_match=ExperienceMatch(
                        years_requirement_met=False,
                        experience_level_fit="unknown"
                    ),
                    score=0
                )
                ai_score = 0

            analyzed_candidates.append(AnalyzedCandidate(
                candidate_id=candidate.candidate_id,
                name=candidate.name,
                email=candidate.email,
                ai_score=ai_score,
                ai_summary=ai_summary,
                location=candidate.location,
                experience_level=candidate.experience_level,
                primary_domain=candidate.parsed_data.ai_analysis.primary_domain if candidate.parsed_data.ai_analysis else "",
                application_status=candidate.application_status,
                analyzed_at=datetime.utcnow()
            ))

        response_obj = BatchAnalyzeResponse(
            job_id=job.job_id,
            job_title=job.title,
            candidates=analyzed_candidates,
            analyzed_at=datetime.utcnow(),
            total_sourced_candidates=len(request.candidates),
            matching_candidates=len([c for c in analyzed_candidates if c.ai_score >= request.options.minimum_score]),
            average_score=int(sum(c.ai_score for c in analyzed_candidates) / len(analyzed_candidates)) if analyzed_candidates else 0
        )
        results.append(response_obj)

    return results