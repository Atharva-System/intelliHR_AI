from fastapi import APIRouter, HTTPException
from agents.job_taging import return_jd
from agents.jd_genrator import return_jd as jd
from agents.jd_title_suggestion import title_suggests
from agents.types import JobDescriptionInput, JobTagsOutput
from app.models.jd_model import JobInput, JobTitleAISuggestInput, JobDescriptionResponse, TitleSuggestionResponse
import json
import logging
from app.models.resume_analyze_model import BatchAnalyzeRequest, BatchAnalyzeResponse

router = APIRouter()

@router.post("/generate-job-description", response_model=JobDescriptionResponse)
def generate_job_description(job: JobInput):
    try:
        response = jd(
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
    

@router.post("/generate-job-tags", response_model=JobTagsOutput)
def generate_job_tags(job: JobDescriptionInput):
    try:
        response = return_jd(
            title=job.title,
            experienceRange=job.experienceRange,
            job_description=job.job_description,
            key_responsibility=job.key_responsibility,
            technical_skill=job.technical_skill,
            soft_skill=job.soft_skill,
            education=job.education,
            nice_to_have=job.nice_to_have
        )
        return JobTagsOutput(tags=response.get("tags", []))
    except Exception as e:
        logging.error(f"Error generating job tags: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate job tags")
