import json
from typing import List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI

from app.models.jd_model import JobTitleAISuggestInput
from app.services.text_extract import pdf_to_text
from app.models.resume_analyze_model import (
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    AnalyzedCandidate,
    AISummary,
    SkillMatch,
    ExperienceMatch
)
from config.Settings import settings


key = settings.api_key
model = settings.model


from datetime import datetime


def resume_score(request: BatchAnalyzeRequest) -> List[BatchAnalyzeResponse]:
    """
    Takes a BatchAnalyzeRequest (jobs + candidates) and returns a BatchAnalyzeResponse.
    Uses LLM to evaluate each candidate against each job.
    """

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