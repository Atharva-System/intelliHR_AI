from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from agents.types import JobDescriptionTitleAISuggest
from app.models.jd_model import JobTitleAISuggestInput
from config.Settings import settings
from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)

def title_suggests(job:JobTitleAISuggestInput):
    job_title_prompt = PromptTemplate(
        input_variables=[
            "title",
            "experienceRange",
            "department",
            "subDepartment",
            "keyResponsibilities",
            "softSkills",
            "technicalSkills",
            "education",
            "certifications",
            "niceToHave",
        ],
        template="""
    You are an AI that suggests job titles based on the following job information:

    - Current Job Title: {title}
    - Experience Range: {experienceRange}
    - Department: {department}
    - Sub-Department: {subDepartment}
    - Key Responsibilities: {keyResponsibilities}
    - Soft Skills: {softSkills}
    - Technical Skills: {technicalSkills}
    - Education Requirements: {education}
    - Certifications: {certifications}
    - Nice to Have: {niceToHave}

    Return a JSON list of 5-10 suitable alternative job titles, in the following format:

    {{"title": ["title1", "title2", "title3", ...]}}
    """
    )

    parser = PydanticOutputParser(pydantic_object=JobDescriptionTitleAISuggest)


    llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

    chain = LLMChain(llm=llm,prompt=job_title_prompt,verbose=True,output_parser=parser)


    raw_output = chain.invoke({
        "title": job.title,
        "experienceRange": job.experienceRange,
        "department": job.department,
        "subDepartment": job.subDepartment or "",
        "keyResponsibilities": job.keyResponsibilities,
        "softSkills": job.softSkills,
        "technicalSkills": job.technicalSkills,
        "education": job.education,
        "certifications": job.certifications or [],
        "niceToHave": job.niceToHave or []
    })
    if isinstance(raw_output, dict) and "text" in raw_output:
        parsed = raw_output["text"]
    else:
        parsed = raw_output
    return parsed
