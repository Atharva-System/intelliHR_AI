import json
from fastapi import APIRouter, HTTPException
from app.models.jd_model import JobRefineInput
from agents.jd_regenrate import key_resp_chain_re, soft_chain_re, tech_chain_re, edu_chain_re, cert_chain_re, nice_chain_re
from agents.jd_enhance import nice_chain,cert_chain,edu_chain,tech_chain,soft_chain,key_resp_chain
import logging
from typing import Dict, Any

# Configure logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

def process_field_output(output: Any, field_name: str) -> list:
    """
    Process the output from chain invocation and extract the field data.

    Args:
        output: The output from chain invocation
        field_name: The name of the field being processed

    Returns:
        list: The processed field data

    Raises:
        ValueError: If output format is invalid
    """
    try:
        if isinstance(output, dict):
            if "text" in output:
                result = getattr(output["text"], field_name, [])
            else:
                result = output.get(field_name, [])
        else:
            result = getattr(output, field_name, [])

        # Ensure result is a list
        if not isinstance(result, list):
            logger.warning(f"Field {field_name} result is not a list, converting: {type(result)}")
            result = [result] if result else []

        return result
    except Exception as e:
        logger.error(f"Error processing output for field {field_name}: {str(e)}")
        raise ValueError(f"Invalid output format for field {field_name}")

def prepare_context(job_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare context dictionary from job input.

    Args:
        job_dict: Dictionary containing job data

    Returns:
        Dict[str, Any]: Context dictionary for chain invocation
    """
    return {
        "title": job_dict.get("title", ""),
        "experienceRange": job_dict.get("experienceRange", ""),
        "department": job_dict.get("department", ""),
        "subDepartment": job_dict.get("subDepartment", "")
    }

@router.post("/regenerate-job-field")
def regenerate_job_field(job: JobRefineInput):
    """
    Regenerate specific job description fields based on input.

    Args:
        job: JobRefineInput containing job details and fields to regenerate

    Returns:
        dict: Regenerated field data

    Raises:
        HTTPException: If processing fails or no valid field found
    """
    logger.info(f"Starting job field regeneration for job: {job.title}")

    try:
        job_dict = job.dict()
        context = prepare_context(job_dict)

        logger.debug(f"Context prepared: {context}")

        field_map = {
            "keyResponsibilities": (key_resp_chain_re, "keyResponsibilities"),
            "softSkills": (soft_chain_re, "softSkills"),
            "technicalSkills": (tech_chain_re, "technicalSkills"),
            "education": (edu_chain_re, "education"),
            "certifications": (cert_chain_re, "certifications"),
            "niceToHave": (nice_chain_re, "niceToHave")
        }

        for field, (chain, field_name) in field_map.items():
            if job_dict.get(field) is not None:
                logger.info(f"Processing field: {field_name}")
                payload = {**context, field_name: job_dict[field]}

                try:
                    logger.debug(f"Invoking chain for {field_name} with payload: {payload}")
                    output = chain.invoke(payload)
                    result = process_field_output(output, field_name)

                    logger.info(f"Successfully regenerated {field_name} with {len(result)} items")
                    return {field_name: result}

                except ValueError as ve:
                    logger.error(f"Value error processing {field_name}: {str(ve)}")
                    raise HTTPException(status_code=422, detail=f"Invalid data format for {field_name}: {str(ve)}")

                except Exception as e:
                    logger.error(f"Unexpected error processing {field_name}: {str(e)}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Error processing {field_name}: {str(e)}")

        logger.warning("No valid field to regenerate found in input")
        raise HTTPException(status_code=400, detail="No valid field to regenerate found in input")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in regenerate_job_field: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/enhance-job-field")
def enhance_job_field(job: JobRefineInput):
    """
    Enhance specific job description fields based on input.

    Args:
        job: JobRefineInput containing job details and fields to enhance

    Returns:
        dict: Enhanced field data

    Raises:
        HTTPException: If processing fails or no valid field found
    """
    logger.info(f"Starting job field enhancement for job: {job.title}")

    try:
        job_dict = job.dict()
        context = prepare_context(job_dict)

        logger.debug(f"Context prepared: {context}")

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
                logger.info(f"Processing field: {field_name}")
                payload = {**context, field_name: job_dict[field]}

                try:
                    logger.debug(f"Invoking chain for {field_name} with payload: {payload}")
                    output = chain.invoke(payload)
                    result = process_field_output(output, field_name)

                    logger.info(f"Successfully enhanced {field_name} with {len(result)} items")
                    return {field_name: result}

                except ValueError as ve:
                    logger.error(f"Value error processing {field_name}: {str(ve)}")
                    raise HTTPException(status_code=422, detail=f"Invalid data format for {field_name}: {str(ve)}")

                except Exception as e:
                    logger.error(f"Unexpected error processing {field_name}: {str(e)}", exc_info=True)
                    raise HTTPException(status_code=500, detail=f"Error processing {field_name}: {str(e)}")

        logger.warning("No valid field to enhance found in input")
        raise HTTPException(status_code=400, detail="No valid field to enhance found in input")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in enhance_job_field: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


