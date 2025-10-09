import re
import json
from typing import List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from app.models.resume_analyze_model import BatchAnalyzeRequest, BatchAnalyzeResponse, AnalyzedCandidate, AISummary, SkillMatch, ExperienceMatch, Job, Candidate
from config.Settings import settings
from datetime import datetime

def generate_batch_analysis(request: BatchAnalyzeRequest) -> List[BatchAnalyzeResponse]:
    llm = GoogleGenerativeAI(
        model=settings.model,
        google_api_key=settings.api_key,
        temperature=0.2,
        max_output_tokens=5000
    )


    prompt = (
        "You are an expert AI resume analyzer.\n"
        "For each job in the request, match all candidates and generate a response in the following format:\n"
        "- job_id: str\n"
        "- job_title: str\n"
        "- candidates: List of analyzed candidates (see below)\n"
        "- analyzed_at: datetime (ISO format)\n"
        "- total_sourced_candidates: int\n"
        "- matching_candidates: int (ai_score > options.minimum_score)\n"
        "- average_score: int\n"
        "Each analyzed candidate must have:\n"
        "- candidate_id: str\n"
        "- name: str\n"
        "- email: str\n"
        "- ai_score: int\n"
        "- ai_summary: {{ score: int, overall_match: str, skill_match: {{ matched_skills: [str], missing_skills: [str], skill_gap_percentage: int }}, experience_match: {{ years_requirement_met: bool, experience_level_fit: str }} }}\n"
        "- location: str\n"
        "- experience_level: str\n"
        "- primary_domain: str\n"
        "- application_status: str\n"
        "- analyzed_at: datetime (ISO format)\n"
        "Instructions:\n"
        "- For each job, loop through all candidates and match them.\n"
        "- Calculate ai_score based on skill and experience match.\n"
        "- Only return the JSON object(s) in the specified format, no markdown, no explanations.\n"
        "- Use request.options.minimum_score to filter matching_candidates.\n"
        "- Use request.jobs and request.candidates fields for matching.\n"
        "- Return a list of BatchAnalyzeResponse objects, one per job.\n"
        "Request Data:\n{input_json}"
    )

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            input_variables=["input_json"],
            template=prompt
        )
    )

    input_json = json.dumps(request.dict(), indent=2)
    raw_output = chain.invoke({"input_json": input_json})
    output_text = raw_output["text"] if isinstance(raw_output, dict) else raw_output
    output_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)
    response_data = json.loads(output_text)

    if isinstance(response_data, dict):
        response_data = [response_data]

    # Filter candidates by minimum_score and update matching_candidates/average_score
    min_score = request.options.minimum_score if hasattr(request.options, "minimum_score") else 0
    filtered_responses = []
    for resp in response_data:
        candidates = resp.get("candidates", [])
        filtered_candidates = [c for c in candidates if c.get("ai_score", 0) >= min_score]
        resp["candidates"] = filtered_candidates
        resp["matching_candidates"] = len(filtered_candidates)
        if filtered_candidates:
            resp["average_score"] = int(sum(c.get("ai_score", 0) for c in filtered_candidates) / len(filtered_candidates))
        else:
            resp["average_score"] = 0
        filtered_responses.append(BatchAnalyzeResponse(**resp))
    return filtered_responses
