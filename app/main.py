from fastapi import FastAPI
from app.routes import feedback_operation, jd_operation, jd_refine, resume_data
from fastapi.middleware.cors import CORSMiddleware
from config.logging import setup_logging
from config.Settings import settings

setup_logging()

app = FastAPI(
    title="intelliHR-AI",
    description="AI-powered HR platform",
    version="1.0.0",
    debug=settings.debug_mode
)

# API versioning
api_v1 = "/api/v1"
app.include_router(jd_operation.router, prefix=api_v1, tags=["Job Descriptions"])
app.include_router(jd_refine.router, prefix=api_v1, tags=["Job Refinement"])
app.include_router(resume_data.router, prefix=api_v1, tags=["Resume Processing"])
app.include_router(feedback_operation.router, prefix=api_v1, tags=["Feedback Processing"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "intelliHR-AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug_mode
    )