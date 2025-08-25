from fastapi import APIRouter
from agents.jd_genrator import return_jd
from agents.jd_title_sujjestion import title_sujjest
from app.models.jd_model import JobInput,JobTitleAISujjestInput
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
    return response

@router.post("/generate-AI-titleSujjestion")
def job_title_sujjestion(job:JobTitleAISujjestInput):
    response = title_sujjest(job)
    return response