from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from agents.types import JobDescriptionOutline
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from config.Settings import settings
from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)

def return_jd(title, experienceRange, department, subDepartment):
    template = """
    You are a professional HR and job description expert.

    You are given the basic job information:

    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}
    If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Based on this, generate a complete job description in **JSON format** with the following fields:

    - keyResponsibilities: list of strings (3-7 main responsibilities)
    - softSkills: list of strings (3-7 relevant soft skills)
    - technicalSkills: list of strings (3-7 relevant technical skills)
    - education: list of strings (relevant degrees or qualifications)
    - certifications: list of strings (optional)
    - niceToHave: list of strings (optional)

    Return **only valid JSON**, do not include explanations.
    """

    prompt = PromptTemplate(
        input_variables=["title", "experienceRange", "department", "subDepartment"],
        template=template
    )

    parser = PydanticOutputParser(pydantic_object=JobDescriptionOutline)


    llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

    chain = LLMChain(llm=llm,prompt=prompt,verbose=True,output_parser=parser)
    raw_output = chain.invoke({
        "title": title,
        "experienceRange": experienceRange,
        "department": department,
        "subDepartment": subDepartment or ""
    })


    if isinstance(raw_output, dict) and "text" in raw_output:
        parsed = raw_output["text"]
    else:
        parsed = raw_output

    if isinstance(parsed, dict):
        job_fields = [
            "keyResponsibilities",
            "softSkills",
            "technicalSkills",
            "education",
            "certifications",
            "niceToHave"
        ]
        return {k: parsed.get(k) for k in job_fields}
    return parsed
