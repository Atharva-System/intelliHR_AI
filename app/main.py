from fastapi import FastAPI
from app.routes import jd_operation,jd_refine,resume_data


app = FastAPI(title="intelliHR-AI")

app.include_router(jd_operation.router)
app.include_router(jd_refine.router)
app.include_router(resume_data.router)