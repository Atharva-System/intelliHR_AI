import re
import json
from typing import List, Dict, Any
from datetime import datetime
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
# Assuming these models exist in your environment
from app.models.batch_analyze_model import JobCandidateData, CandidateAnalysisResponse 
from config.Settings import settings, api_key
import google.generativeai as genai
from toon import encode, decode # Import TOON functions

# Configure the Gemini model
genai.configure(api_key=api_key)

# The core optimization is in the prompt and the use of toon.encode/decode.
# The prompt is modified to instruct the model to use the TOON format, 
# especially the token-efficient tabular array syntax for lists of objects.
def generate_batch_analysis(request: JobCandidateData) -> List[CandidateAnalysisResponse]:
    """
    Analyzes job candidates against job requirements using an LLM, 
    optimized with TOON for token efficiency.
    """
    llm = GoogleGenerativeAI(
        model=settings.model,
        google_api_key=api_key,
        temperature=settings.temperature,
        max_output_tokens=settings.max_output_tokens
    )

    # The raw_prompt is now tailored for TOON input and TOON output
    raw_prompt = """
    You are an expert AI recruiter and resume analyzer.

    Your task is to evaluate candidates against job requirements and produce a structured TOON response for each candidate that includes detailed AI insights, match scoring, and reasoning.

    ### Instructions:
    1. Analyze the candidate's profile (provided in TOON format) in relation to the job description (also in TOON format).
    2. Calculate a **matchScore** (0–100) representing overall job fit.
    3. Populate **aiInsights** fields based on the candidate's resume and job needs.
    4. Fill all fields using realistic, data-consistent values.
    5. Return **only valid TOON** — no markdown, no explanations, no extra text, and DO NOT wrap the output in any backticks (```).

    ### TOON Response Format (Strict Schema)
    Each analyzed candidate must follow this exact TOON schema. Use the compact tabular array format for lists of objects (e.g., skills[N]{...}:):

    job_id: <string>
    id: <string>
    firstName: <string>
    lastName: <string>
    email: <string>
    phone: <string>
    currentTitle: <string>
    experienceYears: <float>
    availability: <string>
    matchScore: <integer 0-100>

    # Skills Array (Tabular Format for Token Efficiency)
    skills[N]{name,level,yearsOfExperience,isVerified}:
    # Example Row: Python,Intermediate,3.5,True
    
    aiInsights:
      coreSkillsScore: <integer 0-100>
      experienceScore: <integer 0-100>
      culturalFitScore: <integer 0-100>
      
      # Strengths Array (Tabular Format)
      strengths[N]{category,point,impact,weight}:
      # Example Row: Leadership,Manages teams of 5+,High,0.9
      
      concerns[N]: <string>, <string>, ...
      uniqueQualities[N]: <string>, <string>, ...
      
      # Skill Matches Array (Tabular Format)
      skillMatches[N]{jobRequirement,candidateSkill,matchStrength,confidenceScore}:
      # Example Row: 5 years of Python,Python 7 years experience,Strong,0.95
      
      skillGaps[N]: <string>, <string>, ...
      recommendation: <string>
      confidenceLevel: <integer 0-100>
      reasoningSummary: <string>
      
    lastAnalyzedAt: <string (ISO datetime)>
    notes[N]: <string>, <string>, ...

    ### Data for Evaluation (Provided in TOON Format):
    Job Information:
    {job_toon}

    Candidate Information:
    {candidate_toon}

    ### Output:
    Return a **single candidate TOON object** following the schema above.
    """

    prompt = PromptTemplate.from_template(raw_prompt)
    chain = LLMChain(llm=llm, prompt=prompt)

    all_results: List[CandidateAnalysisResponse] = []

    for job in request.jobs or []:
        for candidate in request.candidates or []:
            # 1. ENCODE INPUT: Convert JSON structure (Pydantic dict) to TOON string
            job_toon = encode(job.dict(exclude_none=True))
            candidate_toon = encode(candidate.dict(exclude_none=True))

            # LLM Call: Send TOON strings for maximum token savings
            raw_output = chain.invoke({
                "job_toon": job_toon,
                "candidate_toon": candidate_toon
            })
            
            output_text = raw_output["text"] if isinstance(raw_output, dict) else raw_output
            
            # The LLM is instructed to return only TOON, so we can try to decode directly.
            # We keep the strip just in case of minimal whitespace.
            output_text = output_text.strip()

            try:
                # 2. DECODE OUTPUT: Convert TOON string back into a standard Python dictionary
                response: Dict[str, Any] = decode(output_text)
            except Exception as e:
                print(f"Error decoding TOON output for candidate {candidate.candidateId}: {e}")
                # Fallback: If TOON parsing fails, return an empty dictionary to proceed with defaults.
                response = {}

            # --- Post-Processing and Validation (mostly unchanged) ---
            
            # Fill mandatory fields or ensure type correctness, which is often required 
            # when the LLM's output structure is not 100% reliable, regardless of format.
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

            # Clean up nested fields for Pydantic models (crucial for type conversion)
            for s in response.get("skills", []):
                # Ensure fields have a value or a default
                s["level"] = s.get("level", "Intermediate")
                s["yearsOfExperience"] = s.get("yearsOfExperience", 0)
                s["isVerified"] = s.get("isVerified", False)

            for s in response.get("aiInsights", {}).get("strengths", []):
                try:
                    s["weight"] = float(s.get("weight", 0))
                except Exception:
                    s["weight"] = 0.5 # Default fallback

            # Convert the final dictionary back into the Pydantic response model
            all_results.append(CandidateAnalysisResponse(**response))

    filtered_results = [
        candidate for candidate in all_results
        if (candidate.matchScore or 0) >= (request.threshold or 0)
    ]

    return filtered_results