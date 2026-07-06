"""Main FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.rate_limit import limiter
from app.api import law_structure, tax_form_mapping, calculator

# Ensure log records (including error tracebacks) have a handler even when
# not running under uvicorn's logging config (e.g. on Modal).
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

# In-app rate limiting (keyed by client IP) — works locally and on Modal.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware. No credentials: nothing uses cookies or auth headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "app": settings.API_TITLE,
        "version": settings.API_VERSION,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Include routers
app.include_router(law_structure.router, prefix="/api/law", tags=["law-structure"])
app.include_router(tax_form_mapping.router, tags=["tax-forms"])
app.include_router(calculator.router, prefix="/api/qbi", tags=["calculator"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
