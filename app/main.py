from fastapi import FastAPI
from app.routes import jd_operation


app = FastAPI(title="intelliHR-AI")

app.include_router(jd_operation.router)