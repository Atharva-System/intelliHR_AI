from fastapi import APIRouter, HTTPException
from agents.jd_genrator import return_jd
from agents.jd_title_suggestion import title_suggests
from app.models.jd_model import JobInput, JobTitleAISuggestInput, JobDescriptionResponse, TitleSuggestionResponse
import json
import logging

router = APIRouter()

@router.post("/generate-job-description", response_model=JobDescriptionResponse)
def generate_job_description(job: JobInput):
    try:
        response = return_jd(
            title=job.title,
            experienceRange=job.experienceRange,
            department=job.department,
            subDepartment=job.subDepartment or ""
        )
        return response
    except Exception as e:
        logging.error(f"Error generating job description: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate job description")

@router.post("/generate-AI-titleSuggestion", response_model=TitleSuggestionResponse)
def job_title_suggestion(job: JobTitleAISuggestInput):
    try:
        response = title_suggests(job)
        return response
    except Exception as e:
        logging.error(f"Error generating title suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate title suggestions")