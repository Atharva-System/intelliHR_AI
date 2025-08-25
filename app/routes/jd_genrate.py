from fastapi import APIRouter
from agents.jd_genrator import return_jd
from agents.types import JobInput
import json

router = APIRouter()

@router.post("/generate-job-description")
def generate_job_description(job: JobInput):

    response = return_jd(
        title=job.title,
        experienceRange=job.experienceRange,
        department=job.department,
        subDepartment=job.subDepartment or ""
    )

    # response is already a dict, so return directly
    return response