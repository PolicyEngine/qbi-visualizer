"""Pydantic models for law-structured QBID visualization."""

from typing import List, Optional, Any
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


class Parameter(BaseModel):
    """A policy parameter used in computation."""
    name: str
    label: str
    value: Any
    unit: Optional[str] = None
    year: int = 2025
    filing_status: Optional[str] = None


class ComputationStep(BaseModel):
    """A single computation step within a section."""
    id: str
    description: str
    formula: Optional[str] = None
    formula_latex: Optional[str] = None
    inputs: List[str] = Field(default_factory=list)
    output: Optional[str] = None
    code_reference: Optional[str] = None


class LawSection(BaseModel):
    """A section of the law with its implementation."""
    id: str
    section_number: str
    title: str
    description: str
    legal_reference: LegalReference
    status: ImplementationStatus
    status_notes: Optional[str] = None
    inputs: List[InputVariable] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    steps: List[ComputationStep] = Field(default_factory=list)
    variables_used: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None


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
    referenced_by: List[str] = Field(default_factory=list)


class QBIDLawStructure(BaseModel):
    """Complete law-structured representation of QBID computation."""

    title: str = "26 U.S.C. § 199A - Qualified Business Income Deduction"
    effective_date: str = "2018-01-01"
    sunset_date: Optional[str] = None

    total_sections: int
    implemented_sections: int
    partial_sections: int
    missing_sections: int

    sections: List[LawSection]
    adjacent_sections: List[AdjacentSection] = Field(default_factory=list)
