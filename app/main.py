from fastapi import FastAPI
from app.routes import jd_operation,jd_refine,resume_data
from fastapi import APIRouter, HTTPException, FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="intelliHR-AI")

app.include_router(jd_operation.router)
app.include_router(jd_refine.router)
app.include_router(resume_data.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"], 
)