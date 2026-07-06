"""API endpoints for law-structured QBID visualization."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.law_structure import QBIDLawStructure
from app.services.law_structure_builder import build_qbid_law_structure

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/structure", response_model=QBIDLawStructure)
async def get_law_structure():
    """Return the complete law-structured representation of §199A QBID."""
    try:
        return build_qbid_law_structure()
    except Exception:
        logger.exception("Failed to build QBID law structure")
        raise HTTPException(status_code=500, detail="Internal server error")
