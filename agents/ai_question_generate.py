import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from app.models.resume_analyze_model import AIQuestionRequest,AIQuestionResponse
from config.Settings import settings
load_dotenv()

key = settings.api_key
model = settings.model

def generate_interview_questions(request: AIQuestionRequest) -> AIQuestionResponse:
    llm = GoogleGenerativeAI(
        model=model,
        google_api_key=key,
        temperature=0.2,
        max_output_tokens=5000
    )

    prompt = """
    You are a professional recruiter.

    Based on the job requirements and the candidate's resume, generate **100 to 200** relevant interview questions tailored to assess the candidate's fit for the role.

    Instructions:
    1. Start with **10 HR-related questions** that are strictly non-technical. 
    2. Then generate **90 to 190 technical questions** (basic → intermediate → advanced).
    3. Prefix:
       - (HR) for HR questions
       - (Technical-technology-basic) for basic
       - (Technical-technology-intermediate) for intermediate
       - (Technical-technology-advanced) for advanced

    Format:
    Respond with a **JSON list of strings only**, e.g.:
    [
      "(HR) What motivates you in your work?",
      "(Technical-SQL-basic) What is a primary key?"
    ]
    Return a **raw JSON array only**, no markdown, no explanations, no triple backticks.

    Job Requirement and Resume Data:
    {requirement_data}

    """

    chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt)
    )

   
    raw_output = chain.invoke({"requirement_data": request.dict()})

   
    output_text = raw_output["text"] if isinstance(raw_output, dict) else raw_output

    
    try:
        questions = json.loads(output_text)
    except Exception as e:
        raise ValueError(f"Failed to parse LLM output as JSON list:{e}")

   
    return AIQuestionResponse(questions=questions)
