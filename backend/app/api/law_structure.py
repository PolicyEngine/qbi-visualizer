"""API endpoints for law-structured QBID visualization."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.config import settings
from app.models.law_structure import (
    QBIDLawStructure,
    CalculatorInput,
    CalculatorResult,
)
from app.services.law_structure_builder import (
    build_qbid_law_structure,
    calculate_qbid,
)
from app.services.github_manager import GitHubManager

router = APIRouter()

# Initialize services
github_manager = GitHubManager(
    base_path=settings.REPOS_DIR,
    repo_url=settings.GITHUB_REPO,
    branch=settings.GITHUB_BRANCH,
)


@router.get("/structure", response_model=QBIDLawStructure)
async def get_law_structure():
    """
    Get the complete law-structured representation of §199A QBID.

    Returns sections mapped to legal code with implementation status,
    computation steps, and code references.
    """
    try:
        # Get commit info for reference
        commit_info = github_manager.get_current_commit()

        # Build the law structure (currently uses hardcoded knowledge)
        # In the future, this could dynamically extract from PolicyEngine
        structure = build_qbid_law_structure(
            variables={},  # TODO: Pass extracted variables
            parameters={},  # TODO: Pass extracted parameters
            commit_sha=commit_info["sha"],
        )

        return structure

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate", response_model=CalculatorResult)
async def calculate(inputs: CalculatorInput):
    """
    Run an interactive QBID calculation with step-by-step breakdown.

    Accepts income sources, business properties, and tax situation,
    returns detailed computation showing how each §199A section applies.
    """
    try:
        result = calculate_qbid(inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sections/{section_id}")
async def get_section(section_id: str):
    """
    Get detailed information about a specific section of §199A.

    Args:
        section_id: Section identifier (e.g., "sec_a_allowance")
    """
    try:
        structure = build_qbid_law_structure({}, {})

        for section in structure.sections:
            if section.id == section_id:
                return section

        raise HTTPException(
            status_code=404,
            detail=f"Section '{section_id}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_implementation_summary():
    """
    Get a summary of implementation status across all §199A sections.
    """
    try:
        structure = build_qbid_law_structure({}, {})

        sections_summary = []
        for section in structure.sections:
            sections_summary.append({
                "id": section.id,
                "section_number": section.section_number,
                "title": section.title,
                "status": section.status.value,
                "status_notes": section.status_notes,
                "legal_url": section.legal_reference.url,
            })

        return {
            "total_sections": structure.total_sections,
            "implemented": structure.implemented_sections,
            "partial": structure.partial_sections,
            "missing": structure.missing_sections,
            "implementation_percentage": round(
                (structure.implemented_sections + 0.5 * structure.partial_sections)
                / structure.total_sections * 100,
                1
            ),
            "sections": sections_summary,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
