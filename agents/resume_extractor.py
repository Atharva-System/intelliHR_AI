import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from agents.types import CandidateAllInOne
from app.services.text_extract import pdf_to_text
from config.Settings import settings
from datetime import datetime

today = datetime.today()

month = today.month
year = today.year

from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)
llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

parser = PydanticOutputParser(pydantic_object=CandidateAllInOne)

prompt = PromptTemplate(
    input_variables=["text","month","year"],
    template = """
You are an expert information extractor. Extract candidate details from the given text and return a JSON object that strictly matches the CandidateAllInOne schema below.

### Extraction Rules:
1. For **all fields except `ai_analysis` and `tags`**, extract only information explicitly present in the text.
2. Do not infer, assume, or generate missing data for non-AI-analysis fields.
3. If a value is not provided in the text (except AI analysis), set it to null.
4. Output must be strictly valid JSON (double quotes, arrays for lists, booleans lowercase).
5. Dates should follow the format "YYYY-MM" if mentioned.
6. Phone numbers should be digits only (no spaces, country codes, or special characters).
7. **All technologies mentioned anywhere in the text should be listed in `technical_skills`.** Do not include a `technologies` field under work experience.
8. Skills must not include tool names unless explicitly listed.
9. Do not add extra text, explanations, or comments—return JSON only.
10. for experience_year return float value have only value after dot (ex. 2.3,4.5)

### AI Analysis Extraction:
- For ai_analysis, calculate total work experience precisely:
  1. For each work_experience entry, determine duration:
     - If start_date and end_date are provided, compute months difference.
     - If end_date is missing:
       - If is_current=true → use current month {month} and year {year}.
       - Else → assume end_date is **the start_date of the next work_experience minus one month**.
     - If end_date is "Till date", "Present", or similar, use current month and year.
     - If only year is given, assume January as start month and December as end month.
  2. Sum all months across all work_experience entries.
  3. Convert total months to years as a float with **one decimal**:
     - total_years = total_months // 12 + (total_months % 12) / 12
     - Round **one decimal**, e.g., 14.3, 2.8
  4. Assign `experience_year` this float value.
- Determine experience_level based on total years (experience_year) using the same mapping as the system enum:
  - If 0 <= experience_year < 1 → "Entry_Level"
  - If 1 <= experience_year < 3 → "Junior_Level"
  - If 3 <= experience_year < 5 → "Mid_Level"
  - If 5 <= experience_year < 8 → "Mid_Senior_Level"
  - If 8 <= experience_year < 12 → "Senior"
  - If 12 <= experience_year < 15 → "Lead"
  - If experience_year >= 15 → "Principal/Director"
- Ensure the experience_year value is rounded to one decimal before comparison.
- Always select the correct level strictly based on these numeric thresholds (do not approximate or guess).
- Include primary_domain, key_strengths, career_progression_score (1–10), skill_diversity_score (1–10), and good_point if apparent.

### Tags (Smart Tag Generation Rules):

You are an expert career intelligence system responsible for generating highly accurate, descriptive, and meaningful tags for the candidate profile.
Follow these rules carefully
**Read and analyze the entire input text first** — understand the candidate’s role, domain, and experience before generating tags.
**Base all tags on facts in the text** — no hallucination.
**Include both explicit and inferred tags:**
  - If technologies clearly indicate a job type, infer the correct professional identity.
  - Combine skills logically to form meaningful roles.
**Tag Categories:**
  - **Primary Role / Identity Tags:**  
    Examples: “Frontend Developer”, “Full Stack Developer”, “Backend Developer”, “QA Engineer”, “Automation Tester”, “Data Analyst”, “AI/ML Engineer”, “Cloud Engineer”, “DevOps Engineer”.
  - **Experience & Level Tags:**  
    Examples: “Fresher”, “2+ Years Experience”, “Senior Engineer”, “8+ Years Experience”, “Mid-Level Professional”.
  - **Core Technical Skill Tags:**  
    Examples: “Python”, “Django”, “React.js”, “FastAPI”, “AWS”, “SQL”, “Selenium”, “Postman”, “TensorFlow”.
  - **Domain / Role Context Tags:**  
    Examples: “Software Testing”, “Web Development”, “Machine Learning”, “Cloud Computing”, “Project Management”.
  - **Leadership or Responsibility Tags (if applicable):**  
    Examples: “Team Lead”, “Project Manager”, “Scrum Master”, “Mentor”.
  - **Education Tags (1–2 only):**  
    Examples: “B.Tech Computer Science”, “MCA Graduate”, “B.Sc Information Technology”, “M.Tech AI”.
**Inference Guidelines:**
   - React + HTML + CSS → “Frontend Developer”
   - React + Django / Node.js / Python → “Full Stack Developer”
   - Python + Flask/FastAPI → “Backend Developer”
   - Selenium / JMeter / Postman → “QA Engineer”, “Automation Tester”
   - TensorFlow / NLP / LLM / Deep Learning → “AI/ML Engineer”
   - AWS / Docker / Jenkins / Kubernetes → “DevOps Engineer”, “Cloud Engineer”
   - Leadership keywords (lead, manage, mentor) → “Team Lead”, “Project Manager”
**Output Style:**
   - Return a JSON array of strings.
   - Include both short forms and full forms where relevant (e.g., “AI”, “Artificial Intelligence”).
   - Avoid duplicates or redundant phrasing.
   - Maximize tag diversity without reducing accuracy.
**Goal:**  
   Generate tags that provide a **concise, skill-based snapshot** of the candidate’s expertise, identity, and educational background.


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
      "is_current": boolean | null
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
    "experience_year": float | null
    "primary_domain": string | null,
    "key_strengths": [string] | null,
    "career_progression_score": int | null,
    "skill_diversity_score": int | null,
    "good_point": string | null
  }} | null,
  "tags": [string] | null
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

def resume_extract_info(pdf_path):
    input_text = pdf_to_text(pdf_path)
    try:
        candidate = candidate_extraction_chain.run(text=input_text,month=month,year=year)
        result = json.loads(candidate.json())  # Parse the JSON string into a dictionary
    except Exception:
        raw_output = llm(f"Extract JSON only from this text:\n{input_text}")
        try:
            result = json.loads(raw_output)  # Ensure this is a dictionary
        except json.JSONDecodeError as json_err:
            raise Exception(f"Failed to parse extracted JSON: {str(json_err)}")
    print(result)
    return result