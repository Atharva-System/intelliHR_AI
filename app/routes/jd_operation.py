from fastapi import APIRouter
from agents.jd_genrator import return_jd
from agents.jd_title_suggestion import title_suggesst
from app.models.jd_model import JobInput,JobTitleAISuggestInput
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

@router.post("/generate-AI-titleSuggestion")
def job_title_suggestion(job:JobTitleAISuggestInput):
    response = title_suggesst(job)
    return response