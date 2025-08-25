from fastapi import FastAPI
from app.routes import hello


app = FastAPI(title="intelliHR-AI")

app.include_router(hello.router)
