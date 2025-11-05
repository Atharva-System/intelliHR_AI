import re
import json
from typing import List
from datetime import datetime
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from app.models.batch_analyze_model import JobCandidateData, CandidateAnalysisResponse
from config.Settings import  settings
from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)
def generate_batch_analysis(request: JobCandidateData) -> List[CandidateAnalysisResponse]:
    llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

    raw_prompt = """
    You are an expert AI recruiter and resume analyzer.

    Your task is to evaluate candidates against job requirements and produce a structured JSON response for each candidate that includes detailed AI insights, match scoring, and reasoning.

    ### Instructions:
    1. Analyze the candidate's profile in relation to the job description.
    2. Calculate a **matchScore** (0–100) representing overall job fit.
    3. Populate **aiInsights** fields based on the candidate's resume and job needs.
    4. Fill all fields using realistic, data-consistent values.
    5. Return **only valid JSON** — no markdown, no explanations, no extra text.

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

    ### Guidelines:
    - Use realistic data (no placeholders like "string").
    - Compute scores logically:
        - **matchScore** = weighted blend of skills, experience, and fit.
        - **coreSkillsScore**, **experienceScore**, and **culturalFitScore** reflect alignment.
    - Include 2–3 **strengths**, 1–2 **concerns**, and 2–3 **skillMatches** or **skillGaps**.
    - `lastAnalyzedAt` must be the current date-time in ISO 8601 format.
    - Include `job_id` from job data.
    - `availability` and `phone` come from candidate data.
    - Return **only JSON** — no text, markdown, or backticks.

    ### Data for Evaluation:
    Job Information:
    {job_json}

    Candidate Information:
    {candidate_json}

    ### Output:
    Return a **single candidate JSON object** following the schema above.
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

            all_results.append(CandidateAnalysisResponse(**response))

    filtered_results = [
        candidate for candidate in all_results
        if (candidate.matchScore or 0) >= (request.threshold or 0)
    ]

    return filtered_results