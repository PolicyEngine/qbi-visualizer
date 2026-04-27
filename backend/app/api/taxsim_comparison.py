"""API endpoints for TAXSIM comparison."""

from fastapi import APIRouter

from app.models.taxsim_comparison import (
    ComparisonResult,
    CalculationComparisonInput,
    CalculationComparisonResult,
    TaxsimQBIImplementation,
    PolicyEngineQBIImplementation,
)
from app.services.taxsim_comparison import (
    build_comparison,
    compare_calculations,
    get_taxsim_qbi_code,
    get_policyengine_qbi_code,
    TAXSIM_QBI_VARIABLES,
)

router = APIRouter(prefix="/api/taxsim", tags=["taxsim"])


@router.get("/comparison", response_model=ComparisonResult)
async def get_full_comparison():
    """Get the complete comparison between TAXSIM and PolicyEngine QBI implementations."""
    return build_comparison()


@router.post("/calculate", response_model=CalculationComparisonResult)
async def run_comparison_calculation(inputs: CalculationComparisonInput):
    """Run both TAXSIM and PolicyEngine calculations and compare results."""
    return compare_calculations(inputs)


@router.get("/taxsim-implementation")
async def get_taxsim_implementation():
    """Get details of TAXSIM's QBI implementation."""
    return {
        "version": "TAXSIM 35",
        "source_file": "law87.for",
        "source_path": "/Users/pavelmakarchuk/taxsim/law87.for",
        "qbi_variables": [v.model_dump() for v in TAXSIM_QBI_VARIABLES],
        "code_blocks": [block.model_dump() for block in get_taxsim_qbi_code()],
    }


@router.get("/policyengine-implementation")
async def get_policyengine_implementation():
    """Get details of PolicyEngine's QBI implementation."""
    return {
        "version": "PolicyEngine US",
        "main_variable": "qualified_business_income_deduction",
        "code_blocks": [block.model_dump() for block in get_policyengine_qbi_code()],
    }


@router.get("/methodology-summary")
async def get_methodology_summary():
    """Get a summary of the key methodology differences."""
    return {
        "key_differences": [
            {
                "aspect": "W-2 Wage Limitation",
                "taxsim": "NOT applied to non-SSTB income",
                "policyengine": "Applied to all high-income taxpayers",
                "impact": "TAXSIM may give higher deductions for high-income taxpayers without W-2 wages",
                "severity": "significant"
            },
            {
                "aspect": "SSTB Phase-out Range",
                "taxsim": "Flat $50,000 for all filing statuses",
                "policyengine": "$50k single / $100k joint (per statute)",
                "impact": "Joint filers phase out twice as fast in TAXSIM",
                "severity": "minor"
            },
            {
                "aspect": "REIT/PTP Income",
                "taxsim": "Not implemented",
                "policyengine": "Not implemented",
                "impact": "Both miss 20% deduction on REIT dividends and PTP income",
                "severity": "significant"
            },
            {
                "aspect": "Loss Carryforward",
                "taxsim": "Not implemented",
                "policyengine": "Not implemented",
                "impact": "Both zero out negative QBI instead of carrying forward",
                "severity": "minor"
            },
            {
                "aspect": "Per-Business Tracking",
                "taxsim": "Aggregate calculation",
                "policyengine": "Per-person (not per-business)",
                "impact": "Neither tracks individual businesses for limitation purposes",
                "severity": "minor"
            },
        ],
        "overall_assessment": "PolicyEngine is more complete in implementing wage/property limitations. TAXSIM is simpler but may overstate deductions for high-income non-SSTB businesses. Both miss REIT/PTP component."
    }
