"""Tests that the form mapping stays consistent with the law structure."""

import pytest

from app.models.tax_form_mapping import ImplementationStatus
from app.services import pe_parameters as pe
from app.services.tax_form_mapping import build_form_mapping_response


@pytest.fixture
def response():
    return build_form_mapping_response()


def test_two_forms(response):
    assert [f.form_number for f in response.forms] == ["8995", "8995-A"]


def test_tax_year_matches_default(response):
    for form in response.forms:
        assert form.tax_year == pe.DEFAULT_YEAR


def test_thresholds_match_pe(response):
    for form in response.forms:
        assert form.threshold_single == pe.qbi_threshold("SINGLE")
        assert form.threshold_joint == pe.qbi_threshold("JOINT")


def test_form_8995_has_17_lines(response):
    """The IRS Form 8995 has lines 1 through 17."""
    form_8995 = next(f for f in response.forms if f.form_number == "8995")
    assert len(form_8995.lines) == 17


def test_reit_ptp_lines_marked_complete(response):
    """Lines 6, 9, 10, 15 should be COMPLETE post-REIT/PTP wiring."""
    form_8995 = next(f for f in response.forms if f.form_number == "8995")
    for line_no in ("6", "9", "10", "15"):
        line = next(l for l in form_8995.lines if l.line_number == line_no)
        assert line.status == ImplementationStatus.COMPLETE, (
            f"Line {line_no} should be COMPLETE, got {line.status}"
        )


def test_form_8995a_part_iv_complete(response):
    form_8995a = next(f for f in response.forms if f.form_number == "8995-A")
    part_iv = next(l for l in form_8995a.lines if l.line_number == "Part IV")
    assert part_iv.status == ImplementationStatus.COMPLETE


def test_critical_gaps_does_not_contain_reit_ptp(response):
    """REIT/PTP is no longer a gap — it's wired up in qbid_amount.py."""
    gap_ids = [g["id"] for g in response.critical_gaps]
    assert "reit_ptp" not in gap_ids


def test_working_correctly_contains_reit_ptp(response):
    """REIT/PTP should be celebrated as working, not flagged as missing."""
    ids = [w["id"] for w in response.working_correctly]
    assert "reit_ptp" in ids


def test_implementation_pct_in_reasonable_range(response):
    """Sanity-bound the rolled-up implementation percentage."""
    assert 50.0 <= response.summary.implementation_pct <= 80.0


def test_summary_counts_match_form_lines(response):
    """The top-level summary should equal the sum of per-form line counts."""
    expected_complete = sum(f.complete_lines for f in response.forms)
    expected_partial = sum(f.partial_lines for f in response.forms)
    expected_missing = sum(f.missing_lines for f in response.forms)
    assert response.summary.complete == expected_complete
    assert response.summary.partial == expected_partial
    assert response.summary.missing == expected_missing
