"""Pydantic models for law-structured QBID visualization."""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ImplementationStatus(str, Enum):
    """Implementation status of a legal provision."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class LegalReference(BaseModel):
    """Reference to legal code."""
    section: str = Field(..., description="Section number (e.g., '199A(a)')")
    title: str = Field(..., description="Section title")
    url: str = Field(..., description="URL to legal text")
    text: Optional[str] = Field(None, description="Relevant excerpt from law")


class InputVariable(BaseModel):
    """An input variable in the computation."""
    name: str
    label: str
    description: Optional[str] = None
    unit: Optional[str] = None
    default_value: Optional[float] = None
    current_value: Optional[float] = None
    github_url: Optional[str] = None


class Parameter(BaseModel):
    """A policy parameter used in computation."""
    name: str
    label: str
    value: Any
    unit: Optional[str] = None
    year: int = 2025
    filing_status: Optional[str] = None
    github_url: Optional[str] = None


class ComputationStep(BaseModel):
    """A single computation step within a section."""
    id: str
    description: str
    formula: Optional[str] = None
    formula_latex: Optional[str] = None
    inputs: List[str] = Field(default_factory=list)
    output: Optional[str] = None
    code_reference: Optional[str] = None
    github_url: Optional[str] = None


class DecisionPoint(BaseModel):
    """A decision/branching point in the computation."""
    id: str
    condition: str
    condition_formula: Optional[str] = None
    true_branch: str
    false_branch: str
    threshold_values: Optional[Dict[str, float]] = None


class LawSection(BaseModel):
    """A section of the law with its implementation."""
    id: str = Field(..., description="Unique identifier")
    section_number: str = Field(..., description="Legal section (e.g., '199A(a)')")
    title: str = Field(..., description="Section title")
    description: str = Field(..., description="Plain English description")

    # Legal reference
    legal_reference: LegalReference

    # Implementation status
    status: ImplementationStatus
    status_notes: Optional[str] = None

    # Computation details
    inputs: List[InputVariable] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    steps: List[ComputationStep] = Field(default_factory=list)
    decisions: List[DecisionPoint] = Field(default_factory=list)

    # Code mapping
    variables_used: List[str] = Field(default_factory=list)
    formula_source: Optional[str] = None
    github_url: Optional[str] = None

    # Flow
    next_sections: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)

    # Whether this is an adjacent/supporting section vs core 199A
    is_adjacent: bool = Field(default=False, description="True if this is an adjacent IRC section")
    parent_section: Optional[str] = Field(None, description="Which 199A section this supports")


class AdjacentSection(BaseModel):
    """An adjacent IRC section that supports or interacts with 199A."""
    id: str
    section_number: str
    title: str
    description: str
    relevance_to_qbid: str
    legal_reference: LegalReference
    status: ImplementationStatus
    status_notes: Optional[str] = None
    key_provisions: List[str] = Field(default_factory=list)
    variables_used: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    referenced_by: List[str] = Field(default_factory=list, description="Which 199A sections reference this")


class QBIDLawStructure(BaseModel):
    """Complete law-structured representation of QBID computation."""

    title: str = "26 U.S.C. § 199A - Qualified Business Income Deduction"
    effective_date: str = "2018-01-01"
    sunset_date: Optional[str] = "2025-12-31"  # TCJA sunset

    # Summary statistics
    total_sections: int
    implemented_sections: int
    partial_sections: int
    missing_sections: int

    # The main content
    sections: List[LawSection]

    # Adjacent IRC sections
    adjacent_sections: List[AdjacentSection] = Field(
        default_factory=list,
        description="Related IRC sections that interact with 199A"
    )

    # Overall flow order
    computation_order: List[str] = Field(
        default_factory=list,
        description="Ordered list of section IDs for computation flow"
    )

    # Metadata
    policyengine_commit: Optional[str] = None
    last_updated: Optional[str] = None


class CalculatorInput(BaseModel):
    """Input for the interactive calculator."""
    # Income sources
    self_employment_income: float = 0
    partnership_s_corp_income: float = 0
    rental_income: float = 0
    farm_income: float = 0

    # Qualification flags
    self_employment_qualified: bool = True
    partnership_qualified: bool = True
    rental_qualified: bool = True
    farm_qualified: bool = True

    # Business properties
    w2_wages: float = 0
    property_basis: float = 0
    is_sstb: bool = False

    # Deductions
    se_tax_deduction: float = 0
    health_insurance_deduction: float = 0
    pension_deduction: float = 0

    # Tax unit info
    filing_status: str = "SINGLE"
    taxable_income: float = 0
    capital_gains: float = 0

    # Investment income (not yet implemented in PE)
    reit_dividends: float = 0
    ptp_income: float = 0


class CalculatorStep(BaseModel):
    """A step in the calculator computation with values."""
    section_id: str
    section_title: str
    description: str
    inputs: Dict[str, float]
    computation: str
    result: float
    result_label: str
    notes: Optional[str] = None


class CalculatorResult(BaseModel):
    """Result from the interactive calculator."""
    inputs: CalculatorInput
    steps: List[CalculatorStep]
    final_deduction: float

    # Breakdown
    qbi_by_source: Dict[str, float]
    limitation_applied: bool
    limitation_type: Optional[str] = None
    sstb_reduction: float = 0
    taxable_income_cap_applied: bool = False

    # Warnings
    warnings: List[str] = Field(default_factory=list)
    missing_features_used: List[str] = Field(default_factory=list)
