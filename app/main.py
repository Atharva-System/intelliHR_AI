from fastapi import FastAPI
from app.routes import jd_operation,jd_refine


app = FastAPI(title="intelliHR-AI")

app.include_router(jd_operation.router)
app.include_router(jd_refine.router)