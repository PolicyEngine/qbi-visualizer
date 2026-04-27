"""Models for TAXSIM comparison functionality."""

from typing import Dict, List, Optional
from pydantic import BaseModel


class TaxsimInputVariable(BaseModel):
    """TAXSIM input variable definition."""
    number: int
    name: str
    description: str
    qbi_related: bool = False


class TaxsimCodeBlock(BaseModel):
    """A block of TAXSIM FORTRAN code."""
    file: str
    line_start: int
    line_end: int
    code: str
    description: str
    variables_used: List[str] = []


class PolicyEngineCodeBlock(BaseModel):
    """A block of PolicyEngine Python code."""
    file: str
    variable_name: str
    code: str
    description: str
    github_url: Optional[str] = None


class ComparisonItem(BaseModel):
    """A single comparison point between TAXSIM and PolicyEngine."""
    id: str
    law_section: str
    description: str
    taxsim_approach: str
    policyengine_approach: str
    taxsim_code: Optional[TaxsimCodeBlock] = None
    policyengine_code: Optional[PolicyEngineCodeBlock] = None
    difference: str
    severity: str  # "none", "minor", "significant", "critical"


class AdjacentSectionCoverage(BaseModel):
    """Coverage of an adjacent IRC section by each implementation."""
    section_id: str
    section_number: str
    title: str
    taxsim_status: str  # "complete", "partial", "missing", "not_applicable"
    taxsim_notes: str
    policyengine_status: str
    policyengine_notes: str
    impact_on_qbid: str  # How this affects QBID calculation


class TaxsimQBIImplementation(BaseModel):
    """Complete description of TAXSIM's QBI implementation."""
    version: str
    source_file: str
    qbi_variables: List[TaxsimInputVariable]
    code_blocks: List[TaxsimCodeBlock]
    key_features: List[str]
    limitations: List[str]


class PolicyEngineQBIImplementation(BaseModel):
    """Complete description of PolicyEngine's QBI implementation."""
    version: str
    main_variable: str
    dependent_variables: List[str]
    code_blocks: List[PolicyEngineCodeBlock]
    key_features: List[str]
    limitations: List[str]


class ComparisonResult(BaseModel):
    """Full comparison result between TAXSIM and PolicyEngine."""
    taxsim: TaxsimQBIImplementation
    policyengine: PolicyEngineQBIImplementation
    comparisons: List[ComparisonItem]
    adjacent_section_coverage: List[AdjacentSectionCoverage]
    summary: Dict[str, int]  # counts by severity
    methodology_differences: List[str]


class CalculationComparisonInput(BaseModel):
    """Input for running both calculators and comparing results."""
    # Income
    self_employment_income: float = 0
    partnership_s_corp_income: float = 0  # Maps to TAXSIM scorp (data 224)
    sstb_income: float = 0  # Maps to TAXSIM pprofinc/sprofinc (data 212, 215)
    rental_income: float = 0  # Maps to TAXSIM otherprop (data 213)

    # Filing info
    filing_status: str = "SINGLE"  # SINGLE, JOINT, etc.
    taxable_income: float = 0

    # For wage limitation
    w2_wages: float = 0
    property_basis: float = 0

    # Other
    capital_gains: float = 0
    year: int = 2023


class CalculationComparisonResult(BaseModel):
    """Result of running both calculators."""
    policyengine_result: float
    taxsim_result: float
    difference: float
    difference_pct: Optional[float]
    policyengine_steps: List[Dict]
    taxsim_steps: List[Dict]
    notes: List[str]
