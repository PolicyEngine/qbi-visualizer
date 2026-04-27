"""API endpoints for tax form mapping."""

from fastapi import APIRouter
from app.models.tax_form_mapping import FormMappingResponse
from app.services.tax_form_mapping import build_form_mapping_response

router = APIRouter(prefix="/api/forms", tags=["Tax Form Mapping"])


@router.get("/mapping", response_model=FormMappingResponse)
async def get_form_mapping():
    """Get the complete Form 8995/8995-A to PolicyEngine mapping."""
    return build_form_mapping_response()
