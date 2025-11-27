import base64
import json
import mimetypes
import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from agents.ai_prompt_question import generate_prompt_based_questions
from agents.resume_extractor import resume_extract_info
import logging
import uuid
from pathlib import Path
from app.models.resume_analyze_model import AIPromptQuestionRequest, AIPromptQuestionResponse, AIQuestionRequest, AIQuestionResponse
from app.services.ai_match_score import calculate_weighted_coverage_score, check_domain_relevance, check_domain_relevance_strict
from config.Settings import settings
from app.models.batch_analyze_model import JobCandidateData, CandidateAnalysisResponse
from agents.resume_analyze import generate_batch_analysis
from agents.ai_question_generate import generate_interview_questions
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import numpy as np
logger = logging.getLogger(__name__)

router = APIRouter()

class FilePayload(BaseModel):
    file_name: str
    file_data: str

    @validator('file_name')
    def validate_file_name(cls, v):
        if not v or not v.strip():
            raise ValueError('File name cannot be empty')
        return "".join(c for c in v if c.isalnum() or c in ('.', '_', '-'))

    @validator('file_data')
    def validate_file_data(cls, v):
        if not v or not v.strip():
            raise ValueError('File data cannot be empty')
        try:
            # Remove data URI prefix if present
            file_data = v.split(",", 1)[-1] if v.startswith("data:") else v
            # Check for valid base64 characters
            import re
            if not re.match(r'^[A-Za-z0-9+/=]+$', file_data):
                raise ValueError('Invalid base64 characters')
            base64.b64decode(file_data, validate=True)
        except Exception as e:
            raise ValueError(f'Invalid base64 file data: {str(e)}')
        return v

class MultipleFiles(BaseModel):
    files: List[FilePayload]

    @validator('files')
    def validate_files_list(cls, v):
        if not v:
            raise ValueError('At least one file must be provided')
        if len(v) > settings.max_files_per_request:
            raise ValueError(f'Maximum {settings.max_files_per_request} files allowed per request')
        return v

class ResumeExtractionResponse(BaseModel):
    status: str
    processed_files: int
    successful_extractions: int
    failed_extractions: int
    extracted_data: List[Dict[str, Any]]

SAVE_DIR = settings.save_directory
ALLOWED_MIME_TYPES = settings.allowed_mime_types
MAX_FILE_SIZE = settings.max_file_size

def setup_save_directory() -> None:
    try:
        SAVE_DIR.mkdir(exist_ok=True)
        logger.debug(f"Save directory ensured: {SAVE_DIR}")
    except Exception as e:
        logger.error(f"Failed to create save directory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to setup file storage")

def validate_file_type(file_name: str) -> bool:
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type in ALLOWED_MIME_TYPES

def detect_file_type_from_bytes(file_bytes: bytes) -> str:
    if not file_bytes or len(file_bytes) < 8:
        return ""

    if file_bytes.startswith(b"%PDF-"):
        return "application/pdf"

    if file_bytes[:8] == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
        return "application/msword"

    if file_bytes[:2] == b"PK":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return ""

def ensure_filename_extension(file_name: str, detected_mime: str) -> str:
    base, ext = os.path.splitext(file_name)
    if ext:
        return file_name

    if detected_mime == "application/pdf":
        return f"{base}.pdf"
    if detected_mime == "application/msword":
        return f"{base}.doc"
    if detected_mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return f"{base}.docx"
    return file_name

def decode_and_validate_file(file_data: str, file_name: str) -> bytes:
    try:
        # Remove data URI prefix if present
        file_data = file_data.split(",", 1)[-1] if file_data.startswith("data:") else file_data
        # Check for valid base64 characters
        import re
        if not re.match(r'^[A-Za-z0-9+/=]+$', file_data):
            raise ValueError(f"File {file_name} contains invalid base64 characters")

        file_bytes = base64.b64decode(file_data, validate=True)

        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File {file_name} exceeds maximum size limit ({MAX_FILE_SIZE} bytes)")

        if len(file_bytes) == 0:
            raise ValueError(f"File {file_name} is empty")

        logger.debug(f"Successfully decoded file {file_name}, size: {len(file_bytes)} bytes")
        return file_bytes

    except base64.binascii.Error as e:
        logger.error(f"Base64 decode error for file {file_name}: {str(e)}")
        raise ValueError(f"Invalid base64 encoding for file {file_name}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error decoding file {file_name}: {str(e)}")
        raise ValueError(f"Failed to decode file {file_name}: {str(e)}")

def save_file_temporarily(file_bytes: bytes, file_name: str, request_id: str) -> Path:
    try:
        unique_filename = f"{request_id}_{file_name}"
        save_path = SAVE_DIR / unique_filename

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        logger.debug(f"File saved temporarily: {save_path}")
        return save_path

    except OSError as e:
        logger.error(f"Failed to save file {file_name}: {str(e)}")
        raise OSError(f"Failed to save file {file_name}: {str(e)}")

def extract_resume_data(file_path: Path, file_name: str) -> Dict[str, Any]:
    try:
        logger.info(f"Starting resume extraction for file: {file_name}")
        resume_data = resume_extract_info(str(file_path))

        logger.info(f"Successfully extracted resume data from {file_name}")
        return {
            "file_name": file_name,
            "status": "success",
            "extracted_info": resume_data
        }

    except Exception as e:
        logger.error(f"Resume extraction failed for {file_name}: {str(e)}", exc_info=True)
        return {
            "file_name": file_name,
            "status": "error",
            "error": f"Failed to extract resume data: {str(e)}"
        }

def cleanup_file(file_path: Path, file_name: str) -> None:
    try:
        if file_path and file_path.exists():
            file_path.unlink()
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_name}: {str(e)}")

@router.post("/parse-cv", response_model=ResumeExtractionResponse)
def parse_resumes(payload: MultipleFiles):
    request_id = uuid.uuid4().hex
    logger.info(f"Starting resume parsing request {request_id} with {len(payload.files)} files")

    try:
        setup_save_directory()

        extracted_data = []
        successful_extractions = 0
        failed_extractions = 0

        for idx, file in enumerate(payload.files):
            file_name = file.file_name
            logger.info(f"Processing file {idx + 1}/{len(payload.files)}: {file_name}")

            temp_file_path = None

            try:
                try:
                    file_bytes = decode_and_validate_file(file.file_data, file_name)
                except ValueError as ve:
                    logger.warning(f"File validation failed for {file_name}: {str(ve)}")
                    extracted_data.append({
                        "file_name": file_name,
                        "status": "error",
                        "error": str(ve)
                    })
                    failed_extractions += 1
                    continue

                detected_mime = detect_file_type_from_bytes(file_bytes)
                effective_file_name = ensure_filename_extension(file_name, detected_mime)

                if detected_mime:
                    if detected_mime not in ALLOWED_MIME_TYPES:
                        logger.warning(f"Invalid file type for {file_name} (detected {detected_mime})")
                        extracted_data.append({
                            "file_name": file_name,
                            "status": "error",
                            "error": "Invalid file type. Only PDF or DOC/DOCX files are allowed."
                        })
                        failed_extractions += 1
                        continue
                else:
                    if not validate_file_type(effective_file_name):
                        logger.warning(f"Invalid file type for {file_name} (no magic match)")
                        extracted_data.append({
                            "file_name": file_name,
                            "status": "error",
                            "error": "Invalid file type. Only PDF or DOC/DOCX files are allowed."
                        })
                        failed_extractions += 1
                        continue

                try:
                    temp_file_path = save_file_temporarily(file_bytes, effective_file_name, request_id)
                except OSError as oe:
                    logger.error(f"File save failed for {file_name}: {str(oe)}")
                    extracted_data.append({
                        "file_name": file_name,
                        "status": "error",
                        "error": f"Failed to save file: {str(oe)}"
                    })
                    failed_extractions += 1
                    continue

                result = extract_resume_data(temp_file_path, file_name)
                extracted_data.append(result)

                if result.get("status") == "success":
                    successful_extractions += 1
                else:
                    failed_extractions += 1

            except Exception as e:
                logger.error(f"Unexpected error processing file {file_name}: {str(e)}", exc_info=True)
                extracted_data.append({
                    "file_name": file_name,
                    "status": "error",
                    "error": f"Unexpected processing error: {str(e)}"
                })
                failed_extractions += 1

            finally:
                if temp_file_path:
                    cleanup_file(temp_file_path, file_name)

        logger.info(f"Request {request_id} completed: {successful_extractions} successful, {failed_extractions} failed")

        return ResumeExtractionResponse(
            status="completed",
            processed_files=len(payload.files),
            successful_extractions=successful_extractions,
            failed_extractions=failed_extractions,
            extracted_data=extracted_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Critical error in parse_resumes for request {request_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/ai/batch-analyze-resumes", response_model=List[CandidateAnalysisResponse])
def batch_analyze_resumes_api(request: JobCandidateData):
    try:
        num_candidates = len(request.candidates) if request.candidates else 0
        num_jobs = len(request.jobs) if request.jobs else 0
        logger.info(f"Received batch analyze request with {num_candidates} candidates and {num_jobs} jobs")
        
        embeddings = FastEmbedEmbeddings()
        all_results = []

        MINIMUM_ELIGIBLE_SCORE = settings.minimum_eligible_score      
        
        for job in request.jobs or []:
            job_eligible_candidates = []
            
            for candidate in request.candidates or []:
        
                if not candidate.candidate_tag or len(candidate.candidate_tag) == 0:
                    logger.info(f"Job {job.job_id} - Candidate {candidate.candidateId}: "
                               f"No candidate tags, auto-include")
                    job_eligible_candidates.append(candidate)
                    continue
                    
                if not job.job_tag or len(job.job_tag) == 0:
                    logger.info(f"Job {job.job_id} - Candidate {candidate.candidateId}: "
                               f"No job tags, auto-include")
                    job_eligible_candidates.append(candidate)
                    continue
                
                try:
                    
                    relevance_score = check_domain_relevance_strict(
                        candidate.candidate_tag,
                        job.job_tag,
                        embeddings
                    )
                    
                    match_score = calculate_weighted_coverage_score(
                        candidate.candidate_tag,
                        job.job_tag,
                        embeddings
                    )
                    
                    if match_score >= MINIMUM_ELIGIBLE_SCORE:
                        job_eligible_candidates.append(candidate)
                        logger.info(f"Job {job.job_id} - Candidate {candidate.candidateId}: "
                                   f"Relevance {relevance_score:.1f}%, Score {match_score:.1f}% - ELIGIBLE")
                    else:
                        logger.info(f"Job {job.job_id} - Candidate {candidate.candidateId}: "
                                   f"Relevance {relevance_score:.1f}%, Score {match_score:.1f}% - REJECTED")
                        
                except Exception as e:
                    logger.warning(f"Error calculating match for job {job.job_id} "
                                  f"candidate {candidate.candidateId}: {str(e)}")
                    job_eligible_candidates.append(candidate)
            
            if job_eligible_candidates:
                logger.info(f"Job {job.job_id} has {len(job_eligible_candidates)} eligible candidates "
                           f"(filtered from {num_candidates} total)")
                
                job_specific_request = JobCandidateData(
                    jobs=[job],
                    candidates=job_eligible_candidates,
                    threshold=request.threshold,
                    cosine_score=MINIMUM_ELIGIBLE_SCORE
                )
                job_results = generate_batch_analysis(job_specific_request)
                all_results.extend(job_results)
            else:
                logger.warning(f"Job {job.job_id} has NO eligible candidates after filtering")
     
        serialized = [r.dict(exclude_none=True) for r in all_results]
        logger.info(f"Total analysis results: {len(serialized)}")
        return serialized
    
    except Exception as e:
        logger.error(f"Error generating batch AI analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate batch AI analysis")


@router.post("/generate-ai-question", response_model=AIQuestionResponse)
def ai_question_generator(request: AIQuestionRequest):
    try:
        return generate_interview_questions(request)
    except Exception as e:
        logger.error(f"Error generating AI job question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate AI job question")
    

@router.post("/generate-prompt-questions", response_model=AIPromptQuestionResponse)
def ai_prompt_question_generator(request: AIPromptQuestionRequest):
    try:
        if not request.prompt:
            raise Exception("Input array is empty")

        return generate_prompt_based_questions(request)

    except Exception as e:
        logger.error(f"Error generating prompt-based questions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"Error: {str(e)}"
        )