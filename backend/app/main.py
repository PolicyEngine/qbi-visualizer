"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import law_structure, tax_form_mapping, calculator

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": settings.API_TITLE,
        "version": settings.API_VERSION,
        "github_repo": settings.GITHUB_REPO,
        "github_branch": settings.GITHUB_BRANCH,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "repos_dir": str(settings.REPOS_DIR),
        "cache_dir": str(settings.CACHE_DIR),
    }


# Include routers
app.include_router(law_structure.router, prefix="/api/law", tags=["law-structure"])
app.include_router(tax_form_mapping.router, tags=["tax-forms"])
app.include_router(calculator.router, prefix="/api/qbi", tags=["calculator"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
