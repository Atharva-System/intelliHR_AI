import logging
from fastapi import APIRouter, HTTPException
from app.models.chatbot_model import CandidateMatchingRequest,ChatRequest,ChatResponse
from agents.ask_ai import ask_ai
import json, os

router = APIRouter()
FILE_PATH = "candidate_data.txt"

@router.post("/save-candidate-matching")
def save_candidate_matching(request: CandidateMatchingRequest):
    try:
        json_data = json.dumps(request.dict(), indent=4, default=str)
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            f.write(json_data)
        return {"message": "Candidate data saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        response = ask_ai(request.question)
        return ChatResponse(answer=response)

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")