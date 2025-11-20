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
    You are a professional job tag generator expert specializing in creating precise, role-specific tags for job postings.

    You are given the basic job information:

    Title: {title}
    Experience Range: {experienceRange}
    Job Description: {job_description}
    Key Responsibilities: {key_responsibility}
    Technical Skills: {technical_skill}
    Soft Skills: {soft_skill}
    Education: {education}
    Nice to Have: {nice_to_have}

    ### Tag Generation Rules:

    **Read and analyze all job information carefully** — understand the role, domain, and requirements before generating tags.

    **Generate tags in these categories:**

    1. **Primary Role / Job Title Tags (MOST IMPORTANT):**
       - Extract the core job role from the title and responsibilities
       - Examples: "QA Engineer", "Senior QA Engineer", "Frontend Developer", "Full Stack Developer", "Backend Developer", "Data Analyst", "DevOps Engineer", "Cloud Engineer", "AI/ML Engineer"
       - If title is "Senior .NET Engineer" → include "Senior .NET Engineer", ".NET Developer", "Backend Developer"
       - If title is "QA Automation Engineer" → include "QA Engineer", "Automation Tester", "Quality Assurance"

    2. **Core Technical Skill Tags:**
       - List ALL technical skills mentioned
       - Include both specific technologies AND general categories
       - Examples: "Python", "Django", "React.js", "Selenium", "AWS", "Docker", "SQL", "REST API"
       - For testing roles: "Selenium", "Test Automation", "API Testing", "Performance Testing"
       - For dev roles: specific languages, frameworks, databases

    3. **Domain / Specialization Tags:**
       - Identify the domain from responsibilities and description
       - Examples: "Software Testing", "Web Development", "Cloud Computing", "Machine Learning", "Mobile Development"
       - For QA: "Quality Assurance", "Testing", "Test Automation"
       - For Dev: "Software Development", "Web Development", "Backend Development"

    4. **Experience Level Tags:**
       - Based on experienceRange
       - Examples: "Senior", "Mid-Level", "Junior", "Lead", "Principal"
       - Include numeric format: "5+ Years", "3-5 Years", "8+ Years"

    5. **Methodology / Process Tags (if mentioned):**
       - Examples: "Agile", "Scrum", "CI/CD", "DevOps", "TDD", "BDD"

    **Inference Guidelines:**
    - Selenium + JIRA + Test Cases → "QA Engineer", "Automation Tester", "Software Testing"
    - React + JavaScript + HTML/CSS → "Frontend Developer", "Web Development"
    - Python + Django/Flask/FastAPI → "Backend Developer", "Python Developer"
    - AWS + Docker + Kubernetes → "DevOps Engineer", "Cloud Engineer"
    - .NET + C# + SQL Server → ".NET Developer", "Backend Developer"

    **CRITICAL RULES:**
    - Tags must be ROLE-SPECIFIC and DOMAIN-FOCUSED
    - Avoid generic tags like "Communication", "Teamwork" (these are soft skills, not tags)
    - Focus on technical skills and job role identity
    - Include both specific (e.g., "Selenium") and general (e.g., "Test Automation") tags
    - Ensure tags clearly identify the JOB DOMAIN (QA vs Dev vs Data vs DevOps)

    **Output Format:**
    Return only valid JSON in this exact format:
    {{
    "tags": ["tag1", "tag2", "tag3", ...]
    }}

    Generate 8-15 tags that accurately represent this job role and requirements.
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

