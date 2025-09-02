import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from agents.types import CandidateAllInOne
from app.services.text_extract import pdf_to_text
from config.Settings import settings

key = settings.api_key
model = settings.model
llm = GoogleGenerativeAI(
    model=model,
    google_api_key=key,
    temperature=0.2,
    max_output_tokens=8000,

)

parser = PydanticOutputParser(pydantic_object=CandidateAllInOne)

prompt = PromptTemplate(
    input_variables=["text"],
    template = """
You are an expert information extractor. Extract candidate details from the given text and return a JSON object that strictly matches the CandidateAllInOne schema below.

### Extraction Rules:
1. For **all fields except `ai_analysis`**, extract only information explicitly present in the text.
2. Do not infer, assume, or generate missing data for non-AI-analysis fields.
3. If a value is not provided in the text (except AI analysis), set it to null.
4. Output must be strictly valid JSON (double quotes, arrays for lists, booleans lowercase).
5. Dates should follow the format "YYYY-MM" if mentioned.
6. Phone numbers should be digits only (no spaces, country codes, or special characters).
7. Skills must not include tool names unless explicitly listed.
8. Do not add extra text, explanations, or comments—return JSON only.

### AI Analysis Extraction:
- For `ai_analysis`, you may provide insights based on the candidate's text even if not explicitly stated.
- This section can include inferred experience level, primary domain, key strengths, career progression score, skill diversity score, and good_point if apparent.

### Schema:
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

### Input Text:
{text}

### Output:
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