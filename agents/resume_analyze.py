import re
import json
from typing import List
from datetime import datetime
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from app.models.batch_analyze_model import JobCandidateData, CandidateAnalysisResponse
from config.Settings import settings

def map_experience_level(years: float) -> str:
    if years <= 1:
        return "Entry Level"
    elif 1 < years <= 3:
        return "Junior"
    elif 3 < years <= 5:
        return "Mid Level"
    elif 5 < years <= 7:
        return "Mid-Senior Level"
    elif 7 < years <= 10:
        return "Senior"
    else:
        return "Lead"

def generate_batch_analysis(request: JobCandidateData) -> List[CandidateAnalysisResponse]:
    llm = GoogleGenerativeAI(
        model=settings.model,
        google_api_key=settings.api_key,
        temperature=0.2,
        max_output_tokens=5000
    )

    raw_prompt = """
    You are an expert AI recruiter and resume analyzer.

    Your task is to evaluate candidates against job requirements and produce a structured JSON response for each candidate that includes detailed AI insights, match scoring, and reasoning.

    ### Instructions:
    1. Analyze the candidate’s profile in relation to the job description.
    2. Perform **qualification validation**:
        - If the job specifies a minimum qualification (e.g., "Bachelor's degree") and the candidate's qualification does **not** meet it, set **all scores** (matchScore, coreSkillsScore, experienceScore, culturalFitScore) to 0.
        - Add a concern explaining why scores are 0, e.g., "Candidate does not meet the minimum qualification requirement."
    3. Perform **experience validation**:
        - If the job specifies a minimum experience (e.g., 5 years), and the candidate’s experienceYears is **less than required**, set **experienceScore** and overall **matchScore** to 0.
        - Add a concern explaining why experience is insufficient, e.g., "Candidate has 3 years experience; minimum required is 5 years."
    4. Perform **data anomaly check**:
        - If you identify any unusual, unexpected, or suspicious word, field, or value in the candidate data (e.g., missing phone, malformed email, inconsistent experience), **do not modify any other field**.
        - Instead, **add a concern** describing what was identified, e.g., "Candidate phone number format is unusual."
    5. If candidate meets qualification and experience, compute all scores normally.
    6. Populate **aiInsights** fields based on the candidate’s resume and job needs.
    7. Return **only valid JSON** — no markdown, no explanations, no extra text.

    ### JSON Response Format (Strict Schema)
    Each analyzed candidate must follow this exact JSON schema:

    {{
    "job_id": "string",
    "id": "string",
    "firstName": "string",
    "lastName": "string",
    "email": "string",
    "phone": "string",
    "currentTitle": "string",
    "experienceYears": 0,
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

    ### Guidelines:
    - Use realistic data (no placeholders like “string”).
    - Compute scores logically:
        - **matchScore** = weighted blend of skills, experience, and fit.
        - **coreSkillsScore**, **experienceScore**, and **culturalFitScore** reflect alignment.
    - Include **strengths**, **concerns**, **skillMatches** or **skillGaps**.
    - `lastAnalyzedAt` must be the current date-time in ISO 8601 format.
    - Include `job_id` from job data.
    - `availability` and number come from candidate data.
    - `applicationStatus` should be one of: “screening”, “interview”, “rejected”, or “hired”.
    - Return **only JSON** — no text, markdown, or backticks.

    ### Data for Evaluation:
    Job Information:
    {job_json}

    Candidate Information:
    {candidate_json}

    ### Output:
    Return a **single candidate JSON object** following the schema above, applying qualification, experience, and data anomaly validations.
    """

    prompt = PromptTemplate.from_template(raw_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)
    all_results = []

    for job in request.jobs or []:
        for candidate in request.candidates or []:
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
            response["availability"] = response.get("availability") or getattr(candidate, "availability", "") or ""
            response["phone"] = response.get("phone") or getattr(candidate, "phone", "") or ""
            response["currentTitle"] = response.get("currentTitle") or getattr(candidate, "currentTitle", "") or ""
            response["lastAnalyzedAt"] = datetime.now().isoformat()
            experience_years = response.get("experienceYears", 0)
            response["experienceYears"] = map_experience_level(experience_years)
            response["notes"] = response.get("notes") or []

            for s in response.get("skills", []):
                if not isinstance(s.get("level"), str):
                    s["level"] = "Intermediate"

            for s in response.get("aiInsights", {}).get("strengths", []):
                try:
                    s["weight"] = float(s.get("weight", 0))
                except Exception:
                    s["weight"] = 0.5

            all_results.append(CandidateAnalysisResponse(**response))

    filtered_results = [
        candidate for candidate in all_results
        if (candidate.matchScore or 0) >= (request.threshold or 0)
    ]
    print(all_results)
    return filtered_results
