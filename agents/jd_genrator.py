from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from agents.types import JobDescriptionOutline
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
load_dotenv()

key = os.getenv("API_KEY")
model = os.getenv("MODEL")

def return_jd(title, experienceRange, department, subDepartment):
    template = """
    You are a professional HR and job description expert.

    You are given the basic job information:

    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

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

    output_parser = PydanticOutputParser(pydantic_object=JobDescriptionOutline)


    llm = GoogleGenerativeAI(model=model, google_api_key=key,temperature=0.2,max_output_tokens=10000)

    chain = LLMChain(llm=llm,prompt=prompt,verbose=True)
    raw_output = chain.invoke({
        "title": title,
        "experienceRange": experienceRange,
        "department": department,
        "subDepartment": subDepartment or ""
    })

    return output_parser.parse(raw_output["text"] if isinstance(raw_output, dict) and "text" in raw_output else raw_output)
