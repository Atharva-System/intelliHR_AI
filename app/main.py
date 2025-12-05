from fastapi import FastAPI, Request, HTTPException
from app.routes import feedback_operation, jd_operation, jd_refine, resume_data, chatbot
from fastapi.middleware.cors import CORSMiddleware
from config.logging import setup_logging
from config.Settings import settings
from starlette.middleware.base import BaseHTTPMiddleware

setup_logging()

app = FastAPI(
    title="talentpulse.AI",
    description="AI-powered Recruitment platform",
    version="1.0.0",
    debug=settings.debug_mode
)

# ALLOWED_IPS = ["127.0.0.1"]

# class IPFilterMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         client_ip = request.client.host
#         if client_ip not in ALLOWED_IPS:
#             raise HTTPException(status_code=403, detail=f"Access denied for {client_ip}")
#         return await call_next(request)

# app.add_middleware(IPFilterMiddleware)


api_v1 = "/api/v1"
app.include_router(jd_operation.router, prefix=api_v1, tags=["Job Descriptions"])
app.include_router(jd_refine.router, prefix=api_v1, tags=["Job Refinement"])
app.include_router(resume_data.router, prefix=api_v1, tags=["Resume Processing"])
app.include_router(feedback_operation.router, prefix=api_v1, tags=["Feedback Processing"])
app.include_router(chatbot.router, prefix=api_v1, tags=["Chatbot"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TalentPulse-AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,  
        port=settings.api_port,  
        reload=settings.debug_mode
    )
