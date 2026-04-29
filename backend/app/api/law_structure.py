"""API endpoints for law-structured QBID visualization."""

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models.law_structure import QBIDLawStructure
from app.services.law_structure_builder import build_qbid_law_structure
from app.services.github_manager import GitHubManager

router = APIRouter()

github_manager = GitHubManager(
    base_path=settings.REPOS_DIR,
    repo_url=settings.GITHUB_REPO,
    branch=settings.GITHUB_BRANCH,
)


@router.get("/structure", response_model=QBIDLawStructure)
async def get_law_structure():
    """Return the complete law-structured representation of §199A QBID."""
    try:
        commit_info = github_manager.get_current_commit()
        return build_qbid_law_structure(
            variables={},
            parameters={},
            commit_sha=commit_info["sha"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
