from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routes.users import router as users_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Developer Copilot API",
    description="Backend API for the AI Developer Copilot",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "AI Developer Copilot API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }