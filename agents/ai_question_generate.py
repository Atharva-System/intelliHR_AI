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


def generate_interview_questions(request: AIQuestionRequest) -> AIQuestionResponse:
    llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)
    prompt = """
    You are a professional technical interviewer.

    Based on the job requirements and the candidate's resume, generate a comprehensive analysis including an AI score, summary, and advice for the interview process.

    Important:
    - The technologies, domains, and interview questions **must strictly align** with the job role provided in the input.
    - Do **not** include unrelated technologies (e.g., Python, Data Science, Machine Learning) unless they appear in the job requirements.

    Instructions:
    1. Provide an **ai_score** (0-100) reflecting the candidate's overall technical fit for the role.
    2. Include a **summary** with:
    ...
    3. Include **advice** with:
    ...
    4. When generating **questions_to_ask**, ensure they are relevant to the **job technologies**:
    - Example: If the job mentions React, Node.js, and MongoDB, focus questions on those areas.
    - Do not include questions about other stacks (Python, ML, etc.).

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
