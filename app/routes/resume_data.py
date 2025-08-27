import json
from fastapi import APIRouter, HTTPException
from agents.resume_extractor import resume_info
import logging

router = APIRouter()


@router.get("/get-data")
def resume_data():
    result = resume_info()  
    if isinstance(result, str):
        result = json.loads(result)
    return result