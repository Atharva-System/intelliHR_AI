from fastapi import APIRouter, HTTPException
from app.models.jd_model import JobRefineInput
from agents.jd_enhance import key_resp_chain, soft_chain, tech_chain, edu_chain, cert_chain, nice_chain
import logging

router = APIRouter()

@router.post("/refine-job-field")
def refine_job_field(job: JobRefineInput):
    logging.basicConfig(level=logging.DEBUG)
    job_dict = job.dict()
    context = {
        "title": job_dict.get("title"),
        "experienceRange": job_dict.get("experienceRange"),
        "department": job_dict.get("department"),
        "subDepartment": job_dict.get("subDepartment")
    }
    field_map = {
        "keyResponsibilities": (key_resp_chain, "keyResponsibilities"),
        "softSkills": (soft_chain, "softSkills"),
        "technicalSkills": (tech_chain, "technicalSkills"),
        "education": (edu_chain, "education"),
        "certifications": (cert_chain, "certifications"),
        "niceToHave": (nice_chain, "niceToHave")
    }
    for field, (chain, field_name) in field_map.items():
        if job_dict.get(field) is not None:
            payload = {**context, field_name: job_dict[field]}
            try:
                output = chain.invoke(payload)
                if isinstance(output, dict):
                    if "text" in output:
                        result = getattr(output["text"], field_name, [])
                    else:
                        result = output.get(field_name, [])
                else:
                    result = getattr(output, field_name, [])
                return {field_name: result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing {field_name}: {str(e)}")
    return {"error": "No valid field to refine found in input."}