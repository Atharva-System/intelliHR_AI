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
    max_output_tokens=10000
)

parser = PydanticOutputParser(pydantic_object=CandidateAllInOne)

prompt = PromptTemplate(
    input_variables=["text"],
    template = """
You are an expert data extractor. Extract candidate information from the given text and return it strictly in valid JSON matching the CandidateAllInOne schema.

Fields: full_name, email, phone, location, company, position, start_date, end_date, is_current, technologies, 
institution, degree, field_of_study, technical_skills, soft_skills, experience_level, primary_domain, 
key_strengths, career_progression_score, skill_diversity_score, good_point

Rules:
- Output must be valid JSON parsable by Pydantic.
- If a field is missing, return null.
- Dates as strings, lists as arrays, booleans as true/false.
- Do not add extra text, comments, or markdown—only JSON.
- Use double quotes for all JSON keys and string values.

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

def resume_info():
    pdf_path = "./app/services/sample.pdf"
    input_text = pdf_to_text(pdf_path)

    try:
        candidate = candidate_extraction_chain.run(text=input_text)
        result = candidate.json()
    except Exception:
        raw_output = llm(f"Extract JSON only from this text:\n{input_text}")
        result = json.loads(raw_output)
    print(result)  
    return result
