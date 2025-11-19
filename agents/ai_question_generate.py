import re
from pydantic import BaseModel
from typing import List, Dict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import json
from app.models.resume_analyze_model import AIQuestionRequest, AIQuestionResponse
from config.Settings import settings
from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)


def escape_prompt(text: str) -> str:
    """
    Escapes all { } except for {input_data}
    which LangChain should keep as a variable.
    """
    text = text.replace("{", "{{").replace("}", "}}")
    text = text.replace("{{input_data}}", "{input_data}")
    return text


def generate_interview_questions(request: AIQuestionRequest) -> AIQuestionResponse:
    llm = GoogleGenerativeAI(
        model=settings.model,
        google_api_key=api_key,
        temperature=settings.temperature,
        max_output_tokens=settings.max_output_tokens
    )
    
    
    original_prompt = """
    You are a professional technical interviewer conducting a structured analysis.

    **CRITICAL RULES:**
    1. ONLY use technologies and skills mentioned in the Job Requirements
    2. ONLY ask questions related to the candidate's actual technical skills
    3. DO NOT introduce technologies not present in either the job or candidate profile
    4. Questions must be relevant to BOTH the job role AND candidate's experience
    5. Generate interview questions based FIRST on the candidate's skills and experience, and THEN ensure they align with the job requirements
    6. This analysis works for ALL domains - technology, healthcare, finance, marketing, engineering, etc.
    7. Questions must be short
    **JOB AND CANDIDATE DATA:**
    {input_data}

    **YOUR TASK:**
    Generate a JSON response analyzing the candidate's fit for this specific job role.

    **ANALYSIS GUIDELINES:**

    1. **ai_score** (0-100): Calculate based on:
    - Percentage of matched skills from job requirements
    - Experience level alignment
    - Overall suitability for the role

    2. **summary.experience_match**:
    - years_requirement_met: true if candidate's experience level meets or exceeds job requirement, false otherwise
    - experience_level_fit: Rate as "excellent" (exceeds requirements), "good" (meets requirements), "fair" (close to requirements), or "poor" (below requirements)

    3. **summary.skill_match**:
    - matched_skills: List ONLY skills that appear in BOTH job technical_skills AND candidate technical_skills (exact or semantically similar matches)
    - missing_skills: List ONLY job technical_skills that are NOT in candidate technical_skills
    - skill_gap_percentage: Calculate as (count of missing_skills / count of total job technical_skills) * 100

    4. **summary.overall_match**: 
    - Write 1-2 sentences summarizing the candidate's fit for this specific role
    - Mention key matched skills and significant gaps

    5. **advice.interview_focus_areas**: 
    - List 3-5 specific areas to focus on during the interview
    - ONLY mention skills, experiences, or competencies that exist in the candidate's profile
    - Focus on verifying depth and practical application of matched skills
    - If there are transferable skills, mention how to assess them

    6. **advice.next_steps**:
    - Provide 2-4 actionable next steps for the interviewer or hiring process
    - Be specific and practical for this role and candidate combination

    7. **advice.questions_to_ask**:
    - Generate 10-12 interview questions
    - Questions must be based FIRST on the candidate's skills, experience, and competencies
    - Then filter to ensure each question ALSO aligns with the job requirements
    - Do NOT ask about missing skills or technologies the candidate doesn't have
    - Include questions that assess both technical depth and practical application
    - Include scenario-based questions relevant to the job responsibilities
    - Make questions open-ended and interview-ready

    **VALIDATION CHECKLIST (Internal - Do Not Output):**
    Before generating questions, verify:
    - Is this skill in the candidate's technical_skills list? → If NO, don't ask about it
    - Does this question relate to the job requirements or responsibilities? → If NO, don't include it
    - Can the candidate answer this based on their stated experience? → If NO, rephrase or remove it

    **OUTPUT FORMAT:**
    Return ONLY a valid JSON object with this exact structure (no additional text, markdown, or code blocks):
    {
        "ai_score": <integer 0-100>,
        "summary": {
            "experience_match": {
                "years_requirement_met": <boolean>,
                "experience_level_fit": "<string>"
            }},
            "overall_match": "<string>",
            "skill_match": {
                "matched_skills": ["<skill1>", "<skill2>", ...],
                "missing_skills": ["<skill1>", "<skill2>", ...],
                "skill_gap_percentage": <integer>
            }
        },
        "advice": {
            "interview_focus_areas": ["<area1>", "<area2>", "<area3>", ...],
            "next_steps": ["<step1>", "<step2>", "<step3>", ...],
            "questions_to_ask": ["<question1>", "<question2>", "<question3>", ...]
        }
    }

    **CRITICAL REMINDERS:**
    - Return ONLY valid JSON with no additional text
    - All questions must be answerable by the candidate based on their stated skills and experience
    - Focus on the intersection of job requirements and candidate capabilities
    - Generate questions based FIRST on candidate profile and THEN ensure alignment with job requirements
    - Adapt your language and focus to match the domain of the job role
    """

    prompt = escape_prompt(original_prompt)

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt)
    )

    try:
        input_data = {"input_data": request.dict()}
        print(f"Input to chain.invoke: {json.dumps(input_data, indent=2)}")
        
        raw_output = chain.invoke(input_data)
        output_text = raw_output["text"] if isinstance(raw_output, dict) else raw_output
        
        
        output_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)
        
        print(f"Raw LLM output: {output_text}")
        
        response_data = json.loads(output_text)
        
        validated_response = AIQuestionResponse(**response_data)
        print(f"Successfully generated response with AI score: {validated_response.ai_score}")
        
        return validated_response
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Failed output text: {output_text}")
        raise ValueError(f"Failed to parse LLM output as JSON: {e}")
    except Exception as e:
        print(f"General Error: {str(e)}")
        raise ValueError(f"Failed to process LLM request: {e}")
