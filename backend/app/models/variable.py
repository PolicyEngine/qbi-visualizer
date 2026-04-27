"""Pydantic models for variables."""

from typing import List, Optional

from pydantic import BaseModel, Field


class VariableMetadata(BaseModel):
    """Metadata for a PolicyEngine variable."""

    name: str = Field(..., description="Variable name (snake_case)")
    class_name: str = Field(..., description="Class name (CamelCase)")
    label: Optional[str] = Field(None, description="Human-readable label")
    entity: Optional[str] = Field(None, description="Entity type (person, tax_unit, etc)")
    definition_period: Optional[str] = Field(None, description="Time period (YEAR, MONTH, etc)")
    value_type: Optional[str] = Field(None, description="Value type (float, int, bool, etc)")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    reference: List[str] = Field(default_factory=list, description="Legal/documentation references")
    documentation: Optional[str] = Field(None, description="Variable documentation")
    defined_for: Optional[str] = Field(None, description="Condition for variable definition")

    # File information
    file_path: str = Field(..., description="Path to source file")
    github_url: Optional[str] = Field(None, description="GitHub URL to source file")

    # Formula information
    has_formula: bool = Field(False, description="Whether variable has a formula")
    is_input: bool = Field(False, description="Whether variable is an input (no formula)")
    formula: Optional[str] = Field(None, description="Unparsed formula")
    formula_source: Optional[str] = Field(None, description="Source code of formula")
    formula_line_start: Optional[int] = Field(None, description="Formula start line")
    formula_line_end: Optional[int] = Field(None, description="Formula end line")
    formula_github_url: Optional[str] = Field(None, description="GitHub URL to formula")

    # Dependencies
    dependencies: List[str] = Field(default_factory=list, description="Variables this depends on")
    adds: List[str] = Field(default_factory=list, description="Variables combined with add()")
    parameters: List[str] = Field(default_factory=list, description="Parameter paths used")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "qualified_business_income",
                "class_name": "QualifiedBusinessIncome",
                "label": "Qualified business income",
                "entity": "person",
                "definition_period": "YEAR",
                "value_type": "float",
                "unit": "currency-USD",
                "has_formula": True,
                "is_input": False,
                "dependencies": ["self_employment_income", "partnership_s_corp_income"],
                "parameters": ["gov.irs.deductions.qbi.income_definition"],
            }
        }


class VariableList(BaseModel):
    """List of variables."""

    variables: List[VariableMetadata] = Field(..., description="List of variables")
    count: int = Field(..., description="Total count")
    commit_sha: Optional[str] = Field(None, description="Git commit SHA")
    commit_date: Optional[str] = Field(None, description="Git commit date")


class VariableGraphNode(BaseModel):
    """Node in the dependency graph."""

    id: str = Field(..., description="Variable name")
    label: str = Field(..., description="Display label")
    type: str = Field(..., description="Node type: input, intermediate, output")
    entity: Optional[str] = Field(None, description="Entity type")
    value: Optional[float] = Field(None, description="Calculated value (if applicable)")


class VariableGraphEdge(BaseModel):
    """Edge in the dependency graph."""

    source: str = Field(..., description="Source variable name")
    target: str = Field(..., description="Target variable name")
    type: str = Field("dependency", description="Edge type")


class VariableGraph(BaseModel):
    """Complete dependency graph."""

    nodes: List[VariableGraphNode] = Field(..., description="Graph nodes")
    edges: List[VariableGraphEdge] = Field(..., description="Graph edges")
    layers: Optional[dict] = Field(None, description="Layer assignments for visualization")
