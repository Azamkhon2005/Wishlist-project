import time
from collections import defaultdict, deque
from http import HTTPStatus
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from . import models
from .api import users, wishes
from .database import engine

app = FastAPI(title="Wishlist API (Simple Auth)", version="0.1.0")


def problem(
    status: int,
    title: Optional[str] = None,
    detail: Optional[str] = None,
    type_: Optional[str] = None,
    extras: Optional[Dict[str, Any]] = None,
):
    cid = str(uuid4())
    if not title:
        try:
            title = HTTPStatus(status).phrase
        except Exception:
            title = "Error"
    if not type_:
        types = {
            401: "urn:problem:unauthorized",
            403: "urn:problem:forbidden",
            404: "urn:problem:not-found",
            422: "urn:problem:validation-error",
            429: "urn:problem:rate-limit",
        }
        type_ = types.get(status, "about:blank")
    payload = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail or "",
        "correlation_id": cid,
    }
    if extras:
        payload.update(extras)
    response = JSONResponse(payload, status_code=status)
    response.headers["X-Correlation-ID"] = cid
    return response


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return problem(status=exc.status, title="Application error", detail=exc.message)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return problem(status=exc.status_code, detail=detail)


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return problem(status=exc.status_code, detail=detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return problem(
        status=422,
        title="Validation error",
        detail="Request validation failed",
        type_="urn:problem:validation-error",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)


class RateLimitMiddleware(BaseHTTPMiddleware):
    storage: defaultdict = defaultdict(deque)

    def __init__(self, app):
        super().__init__(app)
        self.window = 60  # seconds
        self.limits = {
            "reg": 5,  # /api/users POST
            "auth": 100,  # endpoints with X-API-Key
        }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()
        fwd_for = request.headers.get("X-Forwarded-For")
        client_ip = (
            fwd_for.split(",")[0].strip()
            if fwd_for
            else (request.client.host if request.client else "unknown")
        ) or "unknown"
        api_key = request.headers.get("X-API-Key")

        now = time.time()

        if path == "/api/users/" and method == "POST":
            key = f"reg:{client_ip}"
            if not self._allow(key, now, self.limits["reg"]):
                return problem(
                    status=429,
                    title="Too Many Requests",
                    detail="Rate limit exceeded for registration",
                )

        if path.startswith("/api/") and not (
            path == "/api/users/" and method == "POST"
        ):
            if api_key:
                key = f"auth:{api_key}"
            else:
                key = f"auth-ip:{client_ip}"
            if not self._allow(key, now, self.limits["auth"]):
                return problem(
                    status=429,
                    title="Too Many Requests",
                    detail="Rate limit exceeded",
                )

        response = await call_next(request)
        return response

    def _allow(self, key: str, now: float, limit: int) -> bool:
        dq = self.storage[key]
        while dq and now - dq[0] >= self.window:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True


app.add_middleware(RateLimitMiddleware)

app.include_router(users.router, prefix="/api")
app.include_router(wishes.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Wishlist API! Visit /docs for documentation."}
