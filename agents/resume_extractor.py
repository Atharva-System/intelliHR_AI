import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from agents.types import CandidateAllInOne
from app.services.text_extract import pdf_to_text
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("API_KEY")
model = os.getenv("MODEL")

llm = GoogleGenerativeAI(
    model=model,
    google_api_key=key,
    temperature=0.2,
    max_output_tokens=5000,
    
)

parser = PydanticOutputParser(pydantic_object=CandidateAllInOne)

prompt = PromptTemplate(
    input_variables=["text"],
    template = """
You are an expert data extractor. Extract candidate information from the given text and return it strictly in valid JSON matching the CandidateAllInOne schema. Adhere to the following anti-hallucination policy to ensure accuracy:

**Anti-Hallucination Policy**:
- Extract only information explicitly stated in the provided text.
- Do not infer, assume, or generate any information not directly present.
- If a field or value is not explicitly mentioned, set it to null.
- Do not embellish, summarize, or add details beyond the text.
- For the 'good_point' field in ai_analysis, include a value only if the text explicitly mentions impactful contributions or achievements; otherwise, set it to null.
- Ensure all output strictly matches the provided schema without deviations.



Schema (nested JSON):
{{
  "personal_info": {{
    "full_name": string | null,
    "email": string | null,
    "phone": string | null,
    "location": string | null
  }},
  "work_experience": [
    {{
      "company": string | null,
      "position": string | null,
      "start_date": string | null,
      "end_date": string | null,
      "is_current": boolean | null,
      "technologies": [string] | null
    }}
  ] | null,
  "education": [
    {{
      "institution": string | null,
      "degree": string | null,
      "field_of_study": string | null,
      "start_date": string | null,
      "end_date": string | null
    }}
  ] | null,
  "skills": {{
    "technical_skills": [string] | null,
    "soft_skills": [string] | null
  }} | null,
  "ai_analysis": {{
    "experience_level": string | null,
    "primary_domain": string | null,
    "key_strengths": [string] | null,
    "career_progression_score": int | null,
    "skill_diversity_score": int | null,
    "good_point": string | null
  }} | null
}}

Rules:
- Output must be valid JSON parsable by Pydantic.
- If a field is missing, return null.
- Dates as strings, lists as arrays, booleans as true/false.
- Do not add extra text, comments, or markdown—only JSON.
- Use double quotes for all JSON keys and string values.
- dont menshion tools name in skill
- identify if date menshion for education and work_experience and it look like year-month example 2021-06
- and phone number also in dose not menshion country code.
Text:
{text}

Return only the JSON object.
"""
)

candidate_extraction_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    output_parser=parser,
    verbose=True
)

def resume_info(pdf_path):
    input_text = pdf_to_text(pdf_path)
    try:
        candidate = candidate_extraction_chain.run(text=input_text)
        result = json.loads(candidate.json())  # Parse the JSON string into a dictionary
    except Exception:
        raw_output = llm(f"Extract JSON only from this text:\n{input_text}")
        try:
            result = json.loads(raw_output)  # Ensure this is a dictionary
        except json.JSONDecodeError as json_err:
            raise Exception(f"Failed to parse extracted JSON: {str(json_err)}")
    print(result)
    return result