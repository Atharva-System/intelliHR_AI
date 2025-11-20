from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from agents.types import JobTagsOutput
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from config.Settings import settings
from config.Settings import api_key, settings
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)

def return_jd(title, experienceRange, job_description, key_responsibility,
              technical_skill, soft_skill, education, nice_to_have):
    
    template = """
    You are a professional job role identifier expert.

    You are given the basic job information:

    Title: {title}
    Experience Range: {experienceRange}
    Job Description: {job_description}
    Key Responsibilities: {key_responsibility}
    Technical Skills: {technical_skill}
    Soft Skills: {soft_skill}
    Education: {education}
    Nice to Have: {nice_to_have}

    ### CRITICAL INSTRUCTION:
    Generate EXACTLY 3 tags that identify the JOB ROLE ONLY.

    **Tag Rules:**
    1. Focus ONLY on job role/position identity
    2. DO NOT include technical skills, tools, or technologies
    3. DO NOT include soft skills or methodologies
    4. Tags must clearly identify the PROFESSIONAL ROLE
    5. Analyze the title, responsibilities, and technical skills to infer the correct role
    6. Generate 3 variations of the same role (e.g., specific title, general role, alternative title)

    **Output Format:**
    Return EXACTLY 3 role-specific tags in valid JSON:
    {{
    "tags": ["Role Tag 1", "Role Tag 2", "Role Tag 3"]
    }}
    """

    
    prompt = PromptTemplate(
        input_variables=["title", "experienceRange", "job_description",
                         "key_responsibility", "technical_skill",
                         "soft_skill", "education", "nice_to_have"],
        template=template
    )

    parser = PydanticOutputParser(pydantic_object=JobTagsOutput)

    llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

    chain = LLMChain(llm=llm, prompt=prompt, verbose=True, output_parser=parser)

    raw_output = chain.invoke({
        "title": title,
        "experienceRange": experienceRange,
        "job_description": job_description,
        "key_responsibility": key_responsibility,
        "technical_skill": technical_skill,
        "soft_skill": soft_skill,
        "education": education,
        "nice_to_have": nice_to_have
    })

    if isinstance(raw_output, dict):
        if "tags" in raw_output:
            return raw_output
        elif "text" in raw_output and hasattr(raw_output["text"], "tags"):
            return {"tags": raw_output["text"].tags}
        elif "text" in raw_output and isinstance(raw_output["text"], dict) and "tags" in raw_output["text"]:
            return {"tags": raw_output["text"]["tags"]}
        else:
            raise ValueError(f"Unexpected dict structure: {raw_output.keys()}")
    elif hasattr(raw_output, "tags"):
        return {"tags": raw_output.tags}
    else:
        raise ValueError(f"Unexpected output format: {raw_output}")

