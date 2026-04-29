"""API endpoints for law-structured QBID visualization."""

from fastapi import APIRouter, HTTPException

from app.models.law_structure import QBIDLawStructure
from app.services.law_structure_builder import build_qbid_law_structure

router = APIRouter()


@router.get("/structure", response_model=QBIDLawStructure)
async def get_law_structure():
    """Return the complete law-structured representation of §199A QBID."""
    try:
        return build_qbid_law_structure(variables={}, parameters={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
