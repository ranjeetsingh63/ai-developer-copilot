import time
import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from .rate_limit import limiter
from .routers.repositories import router as repositories_router
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.projects import router as projects_router
from .logging_config import setup_logging

# Initialize structured logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Developer Copilot API",
    description="Backend API for the AI Developer Copilot",
    version="0.1.0"
)

app.state.limiter = limiter

STATUS_CODE_TO_ERROR_CODE = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "validation_error",
    status.HTTP_429_TOO_MANY_REQUESTS: "rate_limit_exceeded",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
}


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log successful requests and handled client errors (4xx)
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2)
            }
        )
        return response
    except Exception as e:
        # Catch and log any unhandled 500 errors with full tracebacks
        process_time = time.time() - start_time
        logger.exception(
            "Unhandled exception during request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "process_time_ms": round(process_time * 1000, 2)
            }
        )
        raise e


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code = STATUS_CODE_TO_ERROR_CODE.get(exc.status_code, "error")
    logger.warning(
        "HTTP Exception",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": exc.status_code,
            "error_code": code,
            "detail": exc.detail
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, str(exc.detail)),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(
        "Validation Error",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "errors": exc.errors()
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=error_body("validation_error", "Invalid request data"),
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(
        request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    logger.warning(
        "Rate Limit Exceeded",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": status.HTTP_429_TOO_MANY_REQUESTS
        }
    )
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=error_body("rate_limit_exceeded", "Too many requests. Please try again later."),
    )


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
app.include_router(repositories_router)


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