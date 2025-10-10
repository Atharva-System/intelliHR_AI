import re
from pydantic import BaseModel
from typing import List, Dict
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import json
from app.models.resume_analyze_model import AIQuestionRequest, AIQuestionResponse
from config.Settings import settings


def generate_interview_questions(request: AIQuestionRequest) -> AIQuestionResponse:
    llm = GoogleGenerativeAI(
        model=settings.model,
        google_api_key=settings.api_key,
        temperature=0.2,
        max_output_tokens=5000
    )

    prompt = """
    You are a professional technical interviewer.

    Based on the job requirements and the candidate's resume, generate a comprehensive analysis including an AI score, summary, and advice for the interview process.

    Instructions:
    1. Provide an **ai_score** (0-100) reflecting the candidate's overall technical fit for the role.
    2. Include a **summary** with:
       - **experience_match**:
           - `years_requirement_met` (boolean): Whether the candidate meets the required years of experience.
           - `experience_level_fit` (string): "under", "match", or "over" based on experience alignment.
       - **overall_match**: A brief description of the candidate's technical fit for the role.
       - **skill_match**:
           - `matched_skills`: List of skills the candidate possesses that match the job requirements.
           - `missing_skills`: List of required skills the candidate lacks.
           - `skill_gap_percentage`: Percentage of required skills the candidate lacks (0-100).
    3. Include **advice** with:
       - **interview_focus_areas**: List of 4-6 critical technical domains or topics to focus on during the interview.
       - **next_steps**: List of 2-4 recommended next steps for the hiring process.
       - **questions_to_ask**: Generate only **technical questions**, designed for a **30–45 minute interview**.
           - Include **10-15 questions**.
           - Questions should test depth of knowledge, problem-solving, and practical understanding.
           - Each question must be labeled as:
             - (Technical-<topic>-<level>), where level ∈ {{Basic, Intermediate, Advanced}}.
           - Questions should cover both **core** and **applied** aspects of the job skills.

    Format:
    Respond with a **JSON object** matching the following structure:
    {{
        "ai_score": int,
        "summary": {{
            "experience_match": {{
                "years_requirement_met": bool,
                "experience_level_fit": str
            }},
            "overall_match": str,
            "skill_match": {{
                "matched_skills": [str],
                "missing_skills": [str],
                "skill_gap_percentage": int
            }}
        }},
        "advice": {{
            "interview_focus_areas": [str],
            "next_steps": [str],
            "questions_to_ask": [str]
        }}
    }}

    Return a **JSON object only**, no markdown, no explanations, no triple backticks.

    Job Requirement and Resume Data:
    {{requirement_data}}
    """

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt)
    )

    try:
        input_data = {"requirement_data": request.dict()}
        print(f"Input to chain.invoke: {json.dumps(input_data, indent=2)}")
        
        raw_output = chain.invoke(input_data)
        output_text = raw_output["text"] if isinstance(raw_output, dict) else raw_output
        output_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)
        print(f"Raw LLM output: {output_text}")
        
        response_data = json.loads(output_text)
        return AIQuestionResponse(**response_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM output as JSON: {e}")
    except Exception as e:
        raise ValueError(f"Failed to process LLM request: {e}")
