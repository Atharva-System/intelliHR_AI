import base64
import json
import mimetypes
import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from agents.resume_extractor import resume_info
import logging
import uuid
from pathlib import Path
from config.Settings import settings
from app.models.resume_analyze_model import BatchAnalyzeRequest, BatchAnalyzeResponse,AIQuestionRequest,AIQuestionResponse
from agents.resume_analyze import resume_score
from agents.ai_question_generate import generate_interview_questions

# Configure logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

class FilePayload(BaseModel):
    file_name: str
    file_data: str

    @validator('file_name')
    def validate_file_name(cls, v):
        if not v or not v.strip():
            raise ValueError('File name cannot be empty')
        # Sanitize file name
        return "".join(c for c in v if c.isalnum() or c in ('.', '_', '-'))

    @validator('file_data')
    def validate_file_data(cls, v):
        if not v or not v.strip():
            raise ValueError('File data cannot be empty')
        try:
            # Test if it's valid base64
            base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError('Invalid base64 file data')
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

# Configuration
SAVE_DIR = settings.save_directory
ALLOWED_MIME_TYPES = settings.allowed_mime_types
MAX_FILE_SIZE = settings.max_file_size

def setup_save_directory() -> None:
    """Create save directory if it doesn't exist."""
    try:
        SAVE_DIR.mkdir(exist_ok=True)
        logger.debug(f"Save directory ensured: {SAVE_DIR}")
    except Exception as e:
        logger.error(f"Failed to create save directory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to setup file storage")

def validate_file_type(file_name: str) -> bool:
    """
    Validate if file type is allowed.

    Args:
        file_name: Name of the file to validate

    Returns:
        bool: True if file type is allowed, False otherwise
    """
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type in ALLOWED_MIME_TYPES

def decode_and_validate_file(file_data: str, file_name: str) -> bytes:
    """
    Decode base64 file data and validate size.

    Args:
        file_data: Base64 encoded file data
        file_name: Name of the file for logging

    Returns:
        bytes: Decoded file bytes

    Raises:
        ValueError: If file is too large or invalid
    """
    try:
        file_bytes = base64.b64decode(file_data)

        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError(f"File {file_name} exceeds maximum size limit ({MAX_FILE_SIZE} bytes)")

        if len(file_bytes) == 0:
            raise ValueError(f"File {file_name} is empty")

        logger.debug(f"Successfully decoded file {file_name}, size: {len(file_bytes)} bytes")
        return file_bytes

    except base64.binascii.Error as e:
        logger.error(f"Base64 decode error for file {file_name}: {str(e)}")
        raise ValueError(f"Invalid base64 encoding for file {file_name}")

def save_file_temporarily(file_bytes: bytes, file_name: str, request_id: str) -> Path:
    """
    Save file temporarily for processing.

    Args:
        file_bytes: File content as bytes
        file_name: Original file name
        request_id: Unique request identifier

    Returns:
        Path: Path to saved file

    Raises:
        OSError: If file cannot be saved
    """
    try:
        # Create unique filename to avoid conflicts
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
    """
    Extract data from resume file.

    Args:
        file_path: Path to the resume file
        file_name: Original file name for logging

    Returns:
        Dict[str, Any]: Extracted resume data or error info
    """
    try:
        logger.info(f"Starting resume extraction for file: {file_name}")
        resume_data = resume_info(str(file_path))

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
    """
    Clean up temporary file.

    Args:
        file_path: Path to file to be cleaned up
        file_name: File name for logging
    """
    try:
        if file_path and file_path.exists():
            file_path.unlink()
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_name}: {str(e)}")

@router.post("/parse-cv", response_model=ResumeExtractionResponse)
def parse_resumes(payload: MultipleFiles):
    """
    Parse multiple resume files and extract information.

    Args:
        payload: MultipleFiles containing list of files to process

    Returns:
        ResumeExtractionResponse: Processing results and extracted data

    Raises:
        HTTPException: If setup fails or processing encounters critical errors
    """
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
                # Validate file type
                if not validate_file_type(file_name):
                    logger.warning(f"Invalid file type for {file_name}")
                    extracted_data.append({
                        "file_name": file_name,
                        "status": "error",
                        "error": "Invalid file type. Only PDF or DOC/DOCX files are allowed."
                    })
                    failed_extractions += 1
                    continue

                # Decode and validate file
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

                # Save file temporarily
                try:
                    temp_file_path = save_file_temporarily(file_bytes, file_name, request_id)
                except OSError as oe:
                    logger.error(f"File save failed for {file_name}: {str(oe)}")
                    extracted_data.append({
                        "file_name": file_name,
                        "status": "error",
                        "error": f"Failed to save file: {str(oe)}"
                    })
                    failed_extractions += 1
                    continue

                # Extract resume data
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
                # Always cleanup temporary file
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

@router.post("/ai/batch-analyze", response_model=BatchAnalyzeResponse)
def analyze_resumes(request: BatchAnalyzeRequest):
    try:
        response = resume_score(request)
        return response
    except Exception as e:
        logging.error(f"Error generating ai analyze: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate ai analyze")

@router.post("/generate-ai-question", response_model=AIQuestionResponse)
def ai_question_generator(request: AIQuestionRequest):
    try:
        return generate_interview_questions(request)
    except Exception as e:
        logging.error(f"Error generating ai job question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate ai job question")