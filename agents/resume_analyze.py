import re
import json
from typing import List
from datetime import datetime
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.models.batch_analyze_model import JobCandidateData, CandidateAnalysisResponse
from config.Settings import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

def generate_batch_analysis(request: JobCandidateData) -> List[CandidateAnalysisResponse]:
    """Synchronous wrapper for async batch analysis"""
    return asyncio.run(generate_batch_analysis_async(request))


async def generate_batch_analysis_async(request: JobCandidateData) -> List[CandidateAnalysisResponse]:
    """Async batch analysis with concurrent processing"""
    max_concurrent = settings.batch_concurrent_limit
    llm = ChatOpenAI(
        model=settings.model,
        api_key=settings.openai_api_key,
        temperature=0,
        max_tokens=settings.max_output_tokens
    )

    raw_prompt = """
    You are an expert AI recruiter and resume analyzer.

    Your task is to evaluate ONE candidate against ONE job using STRICT SCORING RULES.
    You MUST calculate scores mathematically. Do NOT guess.

    ━━━━━━━━━━━
    SCORING RULES (MANDATORY)
    ━━━━━━━━━━━

    1. coreSkillsScore (0–100)
    - 90–100: Meets all required + most preferred skills
    - 70–89: Meets all required skills
    - 40–69: Missing some required skills
    - 0–39: Missing most required skills

    2. experienceScore (0–100)
    - 90–100: Experience exceeds requirement
    - 70–89: Meets requirement
    - 40–69: Slightly below requirement
    - 0–39: Well below requirement

    3. culturalFitScore (0–100)
    - Default to 60 if culture data is unclear
    - Adjust ±20 based on leadership, communication, adaptability

    ━━━━━━━━━━━
    FINAL SCORE FORMULA (STRICT)
    ━━━━━━━━━━━

    matchScore =
    (coreSkillsScore × 0.5) +
    (experienceScore × 0.3) +
    (culturalFitScore × 0.2)

    RULES:
    - matchScore MUST equal the formula result
    - Round all scores to nearest integer
    - Do NOT invent skills or experience
    - If data is missing, LOWER the score

    ━━━━━━━━━━━
    OUTPUT REQUIREMENTS
    ━━━━━━━━━━━

    Return ONLY valid JSON.
    No markdown. No explanations.

    ━━━━━━━━━━━
    JSON SCHEMA (STRICT)
    ━━━━━━━━━━━

    {{
    "job_id": "string",
    "id": "string",
    "firstName": "string",
    "lastName": "string",
    "email": "string",
    "phone": "string",
    "currentTitle": "string",
    "experienceYears": float,
    "skills": [
        {{
        "name": "string",
        "level": "string",
        "yearsOfExperience": 0,
        "isVerified": false
        }}
    ],
    "availability": "string",
    "matchScore": 0,
    "aiInsights": {{
        "coreSkillsScore": 0,
        "experienceScore": 0,
        "culturalFitScore": 0,
        "strengths": [
        {{
            "category": "string",
            "point": "string",
            "impact": "string",
            "weight": 0
        }}
        ],
        "concerns": ["string"],
        "uniqueQualities": ["string"],
        "skillMatches": [
        {{
            "jobRequirement": "string",
            "candidateSkill": "string",
            "matchStrength": "string",
            "confidenceScore": 0
        }}
        ],
        "skillGaps": ["string"],
        "recommendation": "string",
        "confidenceLevel": 0,
        "reasoningSummary": "string"
    }},
    "lastAnalyzedAt": "string (ISO datetime)",
    "notes": ["string"]
    }}

    ━━━━━━━━━━━
    DATA
    ━━━━━━━━━━━

    ### Data for Evaluation:
    Job Information:
    {job_json}

    Candidate Information:
    {candidate_json}

    """

    prompt = PromptTemplate.from_template(raw_prompt)

    # Create list of all job-candidate pairs to process
    tasks = []
    for job in request.jobs or []:
        for candidate in request.candidates or []:
            tasks.append((job, candidate, llm, prompt))

    logger.info(f"Processing {len(tasks)} job-candidate pairs concurrently (max {max_concurrent} at a time)")

    # Process tasks concurrently with semaphore for rate limiting
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single_analysis(job, candidate, llm, prompt):
        async with semaphore:
            try:
                return await asyncio.to_thread(_analyze_candidate_for_job, job, candidate, llm, prompt)
            except Exception as e:
                logger.error(f"Error processing candidate {getattr(candidate, 'candidateId', 'unknown')}: {str(e)}")
                return None

    # Run all tasks concurrently
    results = await asyncio.gather(
        *[process_single_analysis(job, candidate, llm, prompt) for job, candidate, llm, prompt in tasks],
        return_exceptions=True
    )

    # Filter out None and exception results
    all_results = [r for r in results if r is not None and isinstance(r, CandidateAnalysisResponse)]

    filtered_results = [
        candidate for candidate in all_results
        if (candidate.matchScore or 0) >= (request.threshold or 0)
    ]

    logger.info(f"Completed batch analysis: {len(all_results)} processed, {len(filtered_results)} passed threshold")
    return filtered_results


def _analyze_candidate_for_job(job, candidate, llm, prompt) -> CandidateAnalysisResponse:
    """Process a single candidate-job pair (runs in thread pool)"""
    try:
        # Create a new chain for each call to avoid shared state issues
        chain = LLMChain(llm=llm, prompt=prompt)

        job_json = json.dumps(job.dict(exclude_none=True), indent=2)
        candidate_json = json.dumps(candidate.dict(exclude_none=True), indent=2)

        raw_output = chain.invoke({"job_json": job_json, "candidate_json": candidate_json})
        output_text = raw_output["text"] if isinstance(raw_output, dict) else raw_output
        output_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)

        try:
            response = json.loads(output_text)
        except Exception:
            cleaned = re.search(r"\{.*\}", output_text, re.DOTALL)
            response = json.loads(cleaned.group(0)) if cleaned else {}

        response["job_id"] = job.job_id or ""
        response["id"] = response.get("id") or getattr(candidate, "candidateId", "") or ""
        response["firstName"] = response.get("firstName") or getattr(candidate, "name", "").split()[0] if getattr(candidate, "name", None) else ""
        response["lastName"] = response.get("lastName") or " ".join(getattr(candidate, "name", "").split()[1:]) if getattr(candidate, "name", None) else ""
        response["email"] = response.get("email") or getattr(candidate, "email", "") or ""
        response["phone"] = response.get("phone") or getattr(candidate, "phone", "") or ""
        response["currentTitle"] = response.get("currentTitle") or getattr(candidate, "currentTitle", "") or ""
        response["experienceYears"] = response.get("experienceYears") or getattr(candidate, "experience_year", 0) or 0
        response["availability"] = response.get("availability") or "2 weeks"
        response["lastAnalyzedAt"] = datetime.now().isoformat()
        response["notes"] = response.get("notes") or []

        for s in response.get("skills", []):
            if not isinstance(s.get("level"), str):
                s["level"] = "Intermediate"
            if not isinstance(s.get("yearsOfExperience"), (int, float)):
                s["yearsOfExperience"] = 0
            if "isVerified" not in s:
                s["isVerified"] = False

        for s in response.get("aiInsights", {}).get("strengths", []):
            try:
                s["weight"] = float(s.get("weight", 0))
            except Exception:
                s["weight"] = 0.5

        return CandidateAnalysisResponse(**response)
    except Exception as e:
        logger.error(f"Error in _analyze_candidate_for_job: {str(e)}")
        raise