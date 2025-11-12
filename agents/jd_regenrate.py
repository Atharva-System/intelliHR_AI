from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
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



key_resp_parser = PydanticOutputParser(pydantic_object=EnhancekeyResponsibilities)
key_resp_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment"],
    template="""
You are an expert HR assistant AI. Completely regenerate a new, comprehensive list of key responsibilities for the following role. Ignore any previous or input responsibilities. Base your output only on the context below and ensure the responsibilities are clear, professional, actionable, and tailored to the experience range, department, and sub-department.

Output format: A list of 3-7 main responsibilities as strings.

Title: {title}
Experience Range: {experienceRange}
Department: {department}
Sub-Department: {subDepartment}
If title ,experincerange,department,subdepartment,format_instructions as not valid so return response in all field empty.
{format_instructions}
""",
    partial_variables={"format_instructions": key_resp_parser.get_format_instructions()},
)
key_resp_chain_re = LLMChain(llm=llm, prompt=key_resp_prompt, output_parser=key_resp_parser)



soft_parser = PydanticOutputParser(pydantic_object=EnhancesoftSkills)
soft_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment"],
    template="""
You are an expert HR AI. Generate a new, complete list of soft skills for the specified role. Ignore any previous or input soft skills. Base your output only on the context below and ensure the skills are professional, impactful, and tailored to the role’s context, department, and experience level.

Output format: A list of 3-7 relevant soft skills as strings.

Title: {title}
Experience Range: {experienceRange}
Department: {department}
Sub-Department: {subDepartment}
If title ,experincerange,department,subdepartment,format_instructions as not valid so return response in all field empty.
{format_instructions}
""",
    partial_variables={"format_instructions": soft_parser.get_format_instructions()},
)
soft_chain_re = LLMChain(llm=llm, prompt=soft_prompt, output_parser=soft_parser)



tech_parser = PydanticOutputParser(pydantic_object=EnhancetechnicalSkills)
tech_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment"],
    template="""
You are a technical recruiter AI. Generate a new, complete list of technical skills for the following role. Ignore any previous or input technical skills. Base your output only on the context below and ensure the skills are precise, professional, and aligned with industry standards and the needs of the department and sub-department.

Output format: A list of 3-7 relevant technical skills as strings.

Title: {title}
Experience Range: {experienceRange}
Department: {department}
Sub-Department: {subDepartment}
If title ,experincerange,department,subdepartment,format_instructions as not valid so return response in all field empty.
{format_instructions}
""",
    partial_variables={"format_instructions": tech_parser.get_format_instructions()},
)
tech_chain_re = LLMChain(llm=llm, prompt=tech_prompt, output_parser=tech_parser)



edu_parser = PydanticOutputParser(pydantic_object=Enhanceeducation)
edu_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment"],
    template="""
You are an AI HR content enhancer. Generate a new, complete set of education requirements for the following role. Ignore any previous or input education. Base your output only on the context below and ensure requirements are professional, specific, and relevant to the department and sub-department.

Output format: A list of relevant degrees or qualifications as strings (3-7 recommended).

Title: {title}
Experience Range: {experienceRange}
Department: {department}
Sub-Department: {subDepartment}
If title ,experincerange,department,subdepartment,format_instructions as not valid so return response in all field empty.
{format_instructions}
""",
    partial_variables={"format_instructions": edu_parser.get_format_instructions()},
)
edu_chain_re = LLMChain(llm=llm, prompt=edu_prompt, output_parser=edu_parser)



cert_parser = PydanticOutputParser(pydantic_object=Enhancecertifications)
cert_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment"],
    template="""
You are an AI assistant for job description writing. Generate a new, complete list of certifications for the following role. Ignore any previous or input certifications. Base your output only on the context below and ensure certifications are clear, professional, relevant, and industry-recognized.

Output format: A list of relevant certifications as strings (optional, 3-7 recommended).

Title: {title}
Experience Range: {experienceRange}
Department: {department}
Sub-Department: {subDepartment}
If title ,experincerange,department,subdepartment,format_instructions as not valid so return response in all field empty.
{format_instructions}
""",
    partial_variables={"format_instructions": cert_parser.get_format_instructions()},
)
cert_chain_re = LLMChain(llm=llm, prompt=cert_prompt, output_parser=cert_parser)



nice_parser = PydanticOutputParser(pydantic_object=EnhanceniceToHave)
nice_prompt = PromptTemplate(
    input_variables=["title", "experienceRange", "department", "subDepartment"],
    template="""
You are an AI that generates job description content. Create a new, complete list of 'Nice-to-Have' skills for the following role. Ignore any previous or input nice-to-have skills. Base your output only on the context below and ensure skills are clear, professional, and desirable but not essential.

Output format: A list of relevant nice-to-have skills as strings (optional, 3-7 recommended).

Title: {title}
Experience Range: {experienceRange}
Department: {department}
Sub-Department: {subDepartment}
If title ,experincerange,department,subdepartment,format_instructions as not valid so return response in all field empty.
{format_instructions}
""",
    partial_variables={"format_instructions": nice_parser.get_format_instructions()},
)
nice_chain_re = LLMChain(llm=llm, prompt=nice_prompt, output_parser=nice_parser)