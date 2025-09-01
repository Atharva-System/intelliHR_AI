import base64
import json
import mimetypes
import os
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.resume_extractor import resume_info
import logging
import uuid

id = uuid.uuid1()
router = APIRouter()


class FilePayload(BaseModel):
    file_name: str
    file_data: str  
class MultipleFiles(BaseModel):
    files: List[FilePayload]

SAVE_DIR = "downloaded_files"
os.makedirs(SAVE_DIR, exist_ok=True)



@router.post("/parse-cv")
def download_and_save(payload: MultipleFiles):
    saved_files = []
    extracted_data = []
    
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    for file in payload.files:
        try:
            
            mime_type, _ = mimetypes.guess_type(file.file_name)
            if mime_type not in ["application/pdf", 
                                 "application/msword", 
                                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                extracted_data.append({
                    "file_name": file.file_name,
                    "error": "Invalid file type. Only PDF or DOC/DOCX allowed."
                })
                continue
            
        
            file_bytes = base64.b64decode(file.file_data)
            save_path = os.path.join(SAVE_DIR, id.hex+file.file_name)
            with open(save_path, "wb") as f:
                f.write(file_bytes)
            saved_files.append(save_path)
            
        
            try:
                resume_data = resume_info(save_path)
                extracted_data.append({
                    "file_name": file.file_name,
                    "extracted_info": resume_data
                })
            except Exception as e:
                extracted_data.append({
                    "file_name": file.file_name,
                    "error": f"Failed to extract info: {str(e)}"
                })
                
        except Exception as e:
            extracted_data.append({
                "file_name": file.file_name,
                "error": f"Failed to process file: {str(e)}"
            })
        finally:
            if save_path and os.path.exists(save_path):
                os.remove(save_path)
            
    
    return {
        "status": "success",
        "saved_files": saved_files,
        "extracted_data": extracted_data
    }
    