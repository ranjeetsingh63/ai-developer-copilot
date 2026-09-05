from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .rate_limit import limiter
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.projects import router as projects_router


app = FastAPI(
    title="AI Developer Copilot API",
    description="Backend API for the AI Developer Copilot",
    version="0.1.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(projects_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "AI Developer Copilot API is running"
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy"
    }