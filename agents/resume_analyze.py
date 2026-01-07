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

    raw_prompt = """
    You are an expert AI recruiter analyzing candidate-job fit across all industries and roles.

    Evaluate this ONE candidate against this ONE job with precision and nuance.
    DIFFERENTIATE between candidates - avoid identical scores unless truly equivalent.

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    UNIVERSAL SCORING FRAMEWORK
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ## 1. SKILLS MATCH SCORE (0-100) — Weight: 50%

    Analyze technical/domain skills AND soft skills:

    **Technical/Domain Skills (70% of this score):**
    - Count total required skills in job description
    - Match each against candidate's skills (exact or close equivalent)
    - Formula: (Matched Skills / Total Required Skills) × 70
    - Bonus: +5 points per additional relevant skill not required
    - Penalty: -10 points if missing critical/must-have skill

    **Soft Skills (30% of this score):**
    - Leadership, communication, teamwork, problem-solving
    - Match against job requirements
    - Formula: (Matched Soft Skills / Required Soft Skills) × 30

    **Scoring Bands:**
    - 90-100: All required skills + relevant extras, strong proficiency
    - 80-89: All required skills with good proficiency
    - 70-79: Most required skills (80%+), minor gaps
    - 60-69: Moderate skills match (60-80%), notable gaps
    - 50-59: Partial match (40-60%), significant gaps
    - Below 50: Poor match, major skill gaps

    ## 2. EXPERIENCE SCORE (0-100) — Weight: 30%

    Evaluate relevant work experience:

    **Years of Experience:**
    - Compare candidate years vs job requirement
    - Exact match = 70 base points
    - Add/subtract 5 points per year above/below requirement
    - Cap: minimum 30, maximum 95

    **Experience Relevance (+30 points max):**
    - Same role/title: +15 points
    - Same industry: +10 points
    - Similar role/related industry: +5 points
    - Career progression (promotions): +5 points
    - Large company/enterprise experience (if relevant): +5 points

    **Scoring Bands:**
    - 90-100: Exceeds requirement significantly, highly relevant
    - 80-89: Exceeds requirement, very relevant background
    - 70-79: Meets requirement with relevant experience
    - 60-69: Slightly below requirement but compensated by relevance
    - 50-59: Below requirement, limited relevance
    - Below 50: Significantly underqualified

    ## 3. CULTURAL FIT SCORE (0-100) — Weight: 20%

    Assess alignment and adaptability:

    **DO NOT default to 60** - analyze based on evidence:

    **Evaluate from resume/profile (score 40-85):**
    - Work style indicators: +10 if matches job (remote, collaborative, etc.)
    - Career stability: +10 if appropriate job tenure, -10 if many short stints
    - Growth mindset: +10 if shows learning/upskilling
    - Role alignment: +10 if career trajectory matches this role
    - Communication quality: +5 if well-written, professional resume

    **Base Score:** 50 (neutral)
    **Add/Subtract:** Based on above factors

    **Scoring Bands:**
    - 75-85: Excellent alignment, strong cultural indicators
    - 65-74: Good fit, positive indicators
    - 55-64: Adequate fit, neutral indicators
    - 45-54: Questionable fit, some concerns
    - Below 45: Poor fit, red flags

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    FINAL MATCH SCORE CALCULATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    matchScore =
        (coreSkillsScore × 0.50) +
        (experienceScore × 0.30) +
        (culturalFitScore × 0.20)

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    CRITICAL RULES
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    1. Calculate each component independently and precisely
    2. Use specific evidence from candidate data
    3. DIFFERENTIATE similar candidates by at least 2-4 points
    4. Be realistic - use full 0-100 range, not just 70-90
    5. Missing data = LOWER scores (don't assume)
    6. Round component scores to 1 decimal, final matchScore to integer
    7. Write reasoningSummary for recruiters - make it actionable and decision-focused:
       - NO formulas, NO calculations, NO math - use plain professional English
       - Start with overall fit: "Strong match" / "Good fit with gaps" / "Partial match"
       - List key matched skills/experience that align with job requirements
       - Highlight critical gaps or missing qualifications
       - Mention unique strengths or standout qualities
       - End with clear hiring recommendation: "Recommended for interview" / "Consider for phone screen" / "May need additional training" / "Not recommended at this time"
       - Keep it concise (3-5 sentences max) but informative

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

    prompt_template = PromptTemplate.from_template(raw_prompt)

    # Create list of all job-candidate pairs to process
    tasks = []
    for job in request.jobs or []:
        for candidate in request.candidates or []:
            tasks.append((job, candidate, prompt_template))

    logger.info(f"Processing {len(tasks)} job-candidate pairs concurrently (max {max_concurrent} at a time)")

    # Process tasks concurrently with semaphore for rate limiting
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_single_analysis(job, candidate, prompt_template):
        async with semaphore:
            try:
                return await asyncio.to_thread(_analyze_candidate_for_job, job, candidate, prompt_template)
            except Exception as e:
                logger.error(f"Error processing candidate {getattr(candidate, 'candidateId', 'unknown')}: {str(e)}")
                return None

    # Run all tasks concurrently
    results = await asyncio.gather(
        *[process_single_analysis(job, candidate, prompt_template) for job, candidate, prompt_template in tasks],
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


def _analyze_candidate_for_job(job, candidate, prompt_template) -> CandidateAnalysisResponse:
    """Process a single candidate-job pair (runs in thread pool)"""
    try:
        # Create completely fresh LLM and chain for each call - no shared state
        llm = ChatOpenAI(
            model=settings.model,
            api_key=settings.openai_api_key,
            temperature=0.2,  # Slight variation for nuanced scoring
            max_tokens=settings.max_output_tokens
        )
        chain = LLMChain(llm=llm, prompt=prompt_template)

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