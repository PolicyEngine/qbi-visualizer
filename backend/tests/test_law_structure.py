"""Tests that the law structure stays in sync with PolicyEngine code."""

import pytest

from app.models.law_structure import ImplementationStatus
from app.services import pe_parameters as pe
from app.services.law_structure_builder import build_qbid_law_structure


@pytest.fixture
def structure():
    return build_qbid_law_structure({}, {})


def test_no_tcja_sunset_after_obbba(structure):
    """OBBBA made §199A permanent — sunset must not be set."""
    assert structure.sunset_date is None


def test_main_section_count(structure):
    assert len(structure.sections) == 12


def test_status_counts_match_per_section_statuses(structure):
    by_status = {s.status: 0 for s in structure.sections}
    for s in structure.sections:
        by_status[s.status] = by_status.get(s.status, 0) + 1
    assert structure.implemented_sections == by_status.get(ImplementationStatus.COMPLETE, 0)
    assert structure.partial_sections == by_status.get(ImplementationStatus.PARTIAL, 0)
    assert structure.missing_sections == by_status.get(ImplementationStatus.MISSING, 0)


def test_section_ids_are_unique(structure):
    ids = [s.id for s in structure.sections]
    assert len(ids) == len(set(ids))


def test_adjacent_section_ids_are_unique(structure):
    ids = [a.id for a in structure.adjacent_sections]
    assert len(ids) == len(set(ids))


def test_no_duplication_between_main_and_adjacent(structure):
    """§199A subsections belong in main sections, not adjacent."""
    main_ids = {s.id for s in structure.sections}
    adjacent_ids = {a.id for a in structure.adjacent_sections}
    assert main_ids.isdisjoint(adjacent_ids)
    # Adjacent sections should not have section_numbers starting with "199A"
    for a in structure.adjacent_sections:
        assert not a.section_number.lstrip("§").startswith("199A"), (
            f"Adjacent section {a.id} ({a.section_number}) should be a main section"
        )


def test_reit_ptp_status_is_complete(structure):
    """qbid_amount.py adds 20% × qualified_reit_and_ptp_income to the QBID."""
    sec_b1 = next(s for s in structure.sections if s.id == "sec_b1_combined_qbi")
    assert sec_b1.status == ImplementationStatus.COMPLETE

    sec_857 = next(a for a in structure.adjacent_sections if a.id == "sec_857")
    sec_7704 = next(a for a in structure.adjacent_sections if a.id == "sec_7704")
    assert sec_857.status == ImplementationStatus.COMPLETE
    assert sec_7704.status == ImplementationStatus.COMPLETE


def test_loss_carryforward_still_missing(structure):
    """qualified_business_income.py still uses max_(0, ...)."""
    sec_c2 = next(s for s in structure.sections if s.id == "sec_c2_loss_carryover")
    assert sec_c2.status == ImplementationStatus.MISSING


def test_aggregation_cites_treas_reg_not_b5(structure):
    """§199A(b)(5) is 'Acquisitions/dispositions', not the aggregation election."""
    sec_52 = next(a for a in structure.adjacent_sections if a.id == "sec_52")
    assert "Treas. Reg." in sec_52.status_notes
    assert "199A(b)(5)" not in sec_52.status_notes


def test_threshold_parameters_use_live_values(structure):
    """The §199A(e) threshold card must show PE's live YAML values."""
    sec_e = next(s for s in structure.sections if s.id == "sec_e_thresholds")
    single_param = next(p for p in sec_e.parameters if "Single" in p.label)
    joint_param = next(p for p in sec_e.parameters if "Joint" in p.label)
    assert single_param.value == pe.qbi_threshold("SINGLE")
    assert joint_param.value == pe.qbi_threshold("JOINT")


def test_status_notes_dont_falsely_claim_not_implemented(structure):
    """Catch the common drift: a feature gets implemented but the note isn't updated."""
    for s in structure.sections:
        if s.status == ImplementationStatus.COMPLETE and s.status_notes:
            assert "NOT implemented" not in s.status_notes
            assert "is unused" not in s.status_notes
    for a in structure.adjacent_sections:
        if a.status == ImplementationStatus.COMPLETE and a.status_notes:
            assert "NOT implemented" not in a.status_notes
            assert "NOT connected" not in a.status_notes
            assert "is unused" not in a.status_notes
