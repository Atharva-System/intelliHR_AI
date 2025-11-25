from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from agents.types import JobDescriptionTitleAISuggest
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from agents.types import Enhancecertifications, Enhanceeducation, EnhancekeyResponsibilities, EnhanceniceToHave, EnhancesoftSkills, EnhancetechnicalSkills
from config.Settings import settings

load_dotenv()
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

# Key Responsibilities Chain
key_resp_parser = PydanticOutputParser(pydantic_object=EnhancekeyResponsibilities)
key_resp_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment", "keyResponsibilities"],
    template="""
    You are an expert HR assistant AI. Refine and enhance the list of key responsibilities for the following role to make them clear, professional, and aligned with industry standards. Ensure the responsibilities are tailored to the specified experience range, avoiding repetition of the input and adding value where possible (e.g., specificity, actionable language, or additional relevant duties).
    If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

    Input Key Responsibilities:
    {keyResponsibilities}

    {format_instructions}
    """,
    partial_variables={"format_instructions": key_resp_parser.get_format_instructions()},
)
key_resp_chain = LLMChain(llm=llm, prompt=key_resp_prompt, output_parser=key_resp_parser)

# Soft Skills Chain
soft_parser = PydanticOutputParser(pydantic_object=EnhancesoftSkills)
soft_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment", "softSkills"],
    template="""
    You are an expert HR AI. Enhance the list of soft skills for the specified role by:
    - Rephrasing each skill to be professional, impactful, and tailored to the role’s context, department, and experience level.
    - Expanding the list with additional relevant soft skills that align with the department and sub-department, avoiding generic additions.
    - Do NOT repeat the input verbatim; always improve or add value.
    - If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

    Input Soft Skills:
    {softSkills}

    {format_instructions}
    """,
    partial_variables={"format_instructions": soft_parser.get_format_instructions()},
)
soft_chain = LLMChain(llm=llm, prompt=soft_prompt, output_parser=soft_parser)

# Technical Skills Chain
tech_parser = PydanticOutputParser(pydantic_object=EnhancetechnicalSkills)
tech_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment", "technicalSkills"],
    template="""
    You are a technical recruiter AI. Refine and enhance the technical skills section for the following role by:
    - Rephrasing each skill to be precise, professional, and aligned with industry standards.
    - Adding relevant technical skills that complement the role, department, and experience level, if applicable.
    - Ensuring skills reflect the specific needs of the department and sub-department, avoiding generic or redundant entries.
    - Do NOT repeat the input verbatim; always improve or add value.
    - If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

    Input Technical Skills:
    {technicalSkills}

    {format_instructions}
    """,
    partial_variables={"format_instructions": tech_parser.get_format_instructions()},
)
tech_chain = LLMChain(llm=llm, prompt=tech_prompt, output_parser=tech_parser)

# Education Chain
edu_parser = PydanticOutputParser(pydantic_object=Enhanceeducation)
edu_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment", "education"],
    template="""
    You are an AI HR content enhancer. Refine and format the education requirements for the following role by:
    - Clarifying degree types, fields of study, or alternative qualifications (e.g., equivalent experience) to align with the role, department, and experience level.
    - Ensuring requirements are professional, specific, and relevant to the department and sub-department.
    - Avoiding overly generic or restrictive requirements unless specified in the input.
    - If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

    Input Education:
    {education}

    {format_instructions}
    """,
    partial_variables={"format_instructions": edu_parser.get_format_instructions()},
)
edu_chain = LLMChain(llm=llm, prompt=edu_prompt, output_parser=edu_parser)

# Certifications Chain
cert_parser = PydanticOutputParser(pydantic_object=Enhancecertifications)
cert_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment", "certifications"],
    template="""
    You are an AI assistant for job description writing. Refine and enhance the certifications for the following role by:
    - Rephrasing certifications to be clear, professional, and relevant to the role, department, and experience level.
    - Adding relevant certifications that align with the department and sub-department, if applicable, ensuring they are current and industry-recognized.
    - Avoiding repetition of the input and ensuring certifications reflect the role’s requirements.
    - If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

    Input Certifications:
    {certifications}

    {format_instructions}
    """,
    partial_variables={"format_instructions": cert_parser.get_format_instructions()},
)
cert_chain = LLMChain(llm=llm, prompt=cert_prompt, output_parser=cert_parser)

# Nice-to-Have Skills Chain
nice_parser = PydanticOutputParser(pydantic_object=EnhanceniceToHave)
nice_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment", "niceToHave"],
    template="""
    You are an AI that improves job description content. Refine and enhance the list of 'Nice-to-Have' skills for the following role by:
    - Rephrasing skills to be clear, professional, and aligned with the role, department, and experience level.
    - Adding relevant nice-to-have skills that complement the role and department, ensuring they are desirable but not essential and distinct from required skills.
    - Avoiding repetition of the input or overlap with required technical or soft skills.
    - If title ,experincerange,department,subdepartment as not valid so return response in all field empty.
    Title: {title}
    Experience Range: {experienceRange}
    Department: {department}
    Sub-Department: {subDepartment}

    Input Nice-to-Have Skills:
    {niceToHave}

    {format_instructions}
    """,
    partial_variables={"format_instructions": nice_parser.get_format_instructions()},
)
nice_chain = LLMChain(llm=llm, prompt=nice_prompt, output_parser=nice_parser)