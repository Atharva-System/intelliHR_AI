from fastapi import FastAPI
from app.routes import jd_genrate


app = FastAPI(title="intelliHR-AI")

app.include_router(jd_genrate.router)
