from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from agents.types import JobTagsOutput
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from config.Settings import settings

key = settings.api_key
model = settings.model

def return_jd(title, experienceRange, job_description, key_responsibility,
              technical_skill, soft_skill, education, nice_to_have):
    
    template = """
    You are a professional tag generator expert.

    You are given the basic job information:

    Title: {title}
    Experience Range: {experienceRange}
    Job Description: {job_description}
    Key Responsibilities: {key_responsibility}
    Technical Skills: {technical_skill}
    Soft Skills: {soft_skill}
    Education: {education}
    Nice to Have: {nice_to_have}

    Generate a list of relevant tags for this job.

    Return only valid JSON in this exact format:
    {{
    "tags": ["tag1", "tag2", "tag3"]
    }}
    """

    
    prompt = PromptTemplate(
        input_variables=["title", "experienceRange", "job_description",
                         "key_responsibility", "technical_skill",
                         "soft_skill", "education", "nice_to_have"],
        template=template
    )

    parser = PydanticOutputParser(pydantic_object=JobTagsOutput)

    llm = GoogleGenerativeAI(model=model, google_api_key=key, temperature=0.2, max_output_tokens=1000)

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

