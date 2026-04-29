"""API endpoints for the QBI calculator."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import pe_parameters as pe
from app.services.calculator import calculate, get_input_metadata, get_output_metadata

router = APIRouter()


class CalculateRequest(BaseModel):
    """Request body for QBI calculation."""

    year: int = pe.DEFAULT_YEAR
    filing_status: str = "SINGLE"
    state_code: str = "TX"
    # All other fields are passed through as variable values
    self_employment_income: float = 0
    partnership_s_corp_income: float = 0
    farm_operations_income: float = 0
    farm_rent_income: float = 0
    rental_income: float = 0
    estate_income: float = 0
    self_employment_income_would_be_qualified: bool = True
    partnership_s_corp_income_would_be_qualified: bool = True
    farm_operations_income_would_be_qualified: bool = True
    farm_rent_income_would_be_qualified: bool = True
    rental_income_would_be_qualified: bool = True
    estate_income_would_be_qualified: bool = True
    sstb_self_employment_income: float = 0
    sstb_self_employment_income_would_be_qualified: bool = True
    business_is_sstb: bool = False
    w2_wages_from_qualified_business: float = 0
    unadjusted_basis_qualified_property: float = 0
    sstb_w2_wages_from_qualified_business: float = 0
    sstb_unadjusted_basis_qualified_property: float = 0
    qualified_reit_and_ptp_income: float = 0
    employment_income: float = 0
    long_term_capital_gains: float = 0
    short_term_capital_gains: float = 0
    qualified_dividend_income: float = 0
    taxable_interest_income: float = 0


@router.get("/inputs")
async def list_inputs():
    """Return metadata about all available calculator inputs."""
    return {"inputs": get_input_metadata()}


@router.get("/outputs")
async def list_outputs():
    """Return metadata about all calculator outputs."""
    return {"outputs": get_output_metadata()}


@router.post("/calculate")
async def run_calculation(request: CalculateRequest):
    """Run a QBI calculation using PolicyEngine US."""
    try:
        inputs = request.model_dump()
        result = calculate(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
