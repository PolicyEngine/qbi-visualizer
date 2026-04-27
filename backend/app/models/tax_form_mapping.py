"""Pydantic models for tax form to PolicyEngine mapping."""

from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field


class ImplementationStatus(str, Enum):
    """Implementation status of a form line/element."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class FormLineMapping(BaseModel):
    """Mapping of a single form line to PolicyEngine implementation."""
    line_number: str = Field(..., description="Form line number (e.g., '1', '2a', '16')")
    line_label: str = Field(..., description="Official IRS label for this line")
    description: str = Field(..., description="What this line calculates or captures")
    status: ImplementationStatus
    pe_variable: Optional[str] = Field(None, description="PolicyEngine variable name if implemented")
    pe_formula: Optional[str] = Field(None, description="How PE calculates this")
    gap_description: Optional[str] = Field(None, description="What's missing if not complete")
    form_instructions: Optional[str] = Field(None, description="Key instruction from IRS")


class FormScheduleMapping(BaseModel):
    """Mapping of a form schedule (like Schedule A, B, C, D)."""
    schedule_id: str
    schedule_name: str
    description: str
    who_must_file: str
    status: ImplementationStatus
    status_notes: str
    lines: List[FormLineMapping] = Field(default_factory=list)
    key_requirements: List[str] = Field(default_factory=list)


class TaxFormMapping(BaseModel):
    """Complete mapping of a tax form to PolicyEngine."""
    form_number: str = Field(..., description="IRS form number (e.g., '8995')")
    form_title: str
    tax_year: int
    description: str
    who_can_use: str
    threshold_single: float
    threshold_joint: float
    irs_url: str
    instructions_url: str

    # Summary stats
    total_lines: int
    complete_lines: int
    partial_lines: int
    missing_lines: int

    # The actual mappings
    lines: List[FormLineMapping] = Field(default_factory=list)
    schedules: List[FormScheduleMapping] = Field(default_factory=list)


class FormSummary(BaseModel):
    """Summary statistics for form coverage."""
    total_elements: int
    complete: int
    partial: int
    missing: int
    implementation_pct: float


class FormMappingResponse(BaseModel):
    """Response containing all form mappings."""
    forms: List[TaxFormMapping]
    summary: FormSummary
    critical_gaps: List[Dict[str, str]]
    working_correctly: List[Dict[str, str]]
