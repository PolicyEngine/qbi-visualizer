"""API endpoints for the QBI calculator."""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.rate_limit import limiter
from app.services import pe_parameters as pe
from app.services.calculator import calculate, get_input_metadata, get_output_metadata

logger = logging.getLogger(__name__)

router = APIRouter()

FilingStatus = Literal[
    "SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"
]

# The 50 states plus DC — the codes policyengine-us accepts that this
# calculator supports (PE's StateCode enum also lists territories/military
# codes, but state tax logic there is not meaningful for this tool).
StateCode = Literal[
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA",
    "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY",
    "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
    "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

# Bounds for money inputs: generous but finite, so JSON like 1e999 (which
# parses to +inf) gets a clean 422 instead of flowing into the simulation.
Money = Annotated[float, Field(ge=-100_000_000, le=100_000_000)]


class CalculateRequest(BaseModel):
    """Request body for QBI calculation."""

    # 2018 = §199A effective date (TCJA).
    year: int = Field(pe.DEFAULT_YEAR, ge=2018, le=2035)
    filing_status: FilingStatus = "SINGLE"
    state_code: StateCode = "TX"
    # All other fields are passed through as variable values
    self_employment_income: Money = 0
    partnership_s_corp_income: Money = 0
    farm_operations_income: Money = 0
    farm_rent_income: Money = 0
    rental_income: Money = 0
    estate_income: Money = 0
    self_employment_income_would_be_qualified: bool = True
    partnership_s_corp_income_would_be_qualified: bool = True
    farm_operations_income_would_be_qualified: bool = True
    farm_rent_income_would_be_qualified: bool = True
    rental_income_would_be_qualified: bool = True
    estate_income_would_be_qualified: bool = True
    sstb_self_employment_income: Money = 0
    sstb_self_employment_income_would_be_qualified: bool = True
    business_is_sstb: bool = False
    w2_wages_from_qualified_business: Money = 0
    unadjusted_basis_qualified_property: Money = 0
    sstb_w2_wages_from_qualified_business: Money = 0
    sstb_unadjusted_basis_qualified_property: Money = 0
    qualified_reit_and_ptp_income: Money = 0
    employment_income: Money = 0
    long_term_capital_gains: Money = 0
    short_term_capital_gains: Money = 0
    qualified_dividend_income: Money = 0
    taxable_interest_income: Money = 0


class CalculateResponse(BaseModel):
    """Response body for QBI calculation.

    `outputs` values are always numbers; variables that failed to compute
    are omitted from `outputs` and reported in `errors` (variable name ->
    short error message), which is `{}` when nothing failed.
    """

    outputs: dict[str, float]
    errors: dict[str, str]
    parameters: dict[str, float]
    year: int
    filing_status: str


@router.get("/inputs")
async def list_inputs():
    """Return metadata about all available calculator inputs."""
    return {"inputs": get_input_metadata()}


@router.get("/outputs")
async def list_outputs():
    """Return metadata about all calculator outputs."""
    return {"outputs": get_output_metadata()}


@router.post("/calculate", response_model=CalculateResponse)
@limiter.limit("30/minute")
async def run_calculation(request: Request, payload: CalculateRequest):
    """Run a QBI calculation using PolicyEngine US."""
    try:
        return calculate(payload.model_dump())
    except HTTPException:
        raise
    except ValueError:
        # Input-shaped failure that slipped past Pydantic validation.
        logger.exception("Invalid calculation input: %s", payload.model_dump())
        raise HTTPException(status_code=422, detail="Invalid calculation input")
    except Exception:
        logger.exception("Calculation failed for input: %s", payload.model_dump())
        raise HTTPException(status_code=500, detail="Internal calculation error")
