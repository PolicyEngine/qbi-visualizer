"""End-to-end tests against the FastAPI app via TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_root_endpoint():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_law_structure_endpoint():
    r = client.get("/api/law/structure")
    assert r.status_code == 200
    body = r.json()
    assert body["sunset_date"] is None
    assert body["total_sections"] == 12
    assert len(body["adjacent_sections"]) >= 13


def test_law_structure_b1_is_complete():
    r = client.get("/api/law/structure")
    body = r.json()
    sec_b1 = next(s for s in body["sections"] if s["id"] == "sec_b1_combined_qbi")
    assert sec_b1["status"] == "complete"


def test_forms_mapping_endpoint():
    r = client.get("/api/forms/mapping")
    assert r.status_code == 200
    body = r.json()
    assert [f["form_number"] for f in body["forms"]] == ["8995", "8995-A"]
    gap_ids = [g["id"] for g in body["critical_gaps"]]
    assert "reit_ptp" not in gap_ids


def test_qbi_inputs_endpoint():
    r = client.get("/api/qbi/inputs")
    assert r.status_code == 200
    body = r.json()
    assert "inputs" in body
    assert len(body["inputs"]) > 0


def test_qbi_outputs_endpoint():
    r = client.get("/api/qbi/outputs")
    assert r.status_code == 200
    body = r.json()
    assert "outputs" in body
    assert len(body["outputs"]) > 0


def test_qbi_calculate_zero_income():
    r = client.post(
        "/api/qbi/calculate",
        json={"filing_status": "SINGLE", "year": 2025},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["outputs"]["qualified_business_income_deduction"] == 0


def test_qbi_calculate_with_qbi_below_threshold():
    """Single filer with $50k SE income — well below threshold, full 20% deduction."""
    r = client.post(
        "/api/qbi/calculate",
        json={
            "filing_status": "SINGLE",
            "year": 2025,
            "self_employment_income": 50_000,
        },
    )
    assert r.status_code == 200
    body = r.json()
    qbid = body["outputs"]["qualified_business_income_deduction"]
    # QBID should be roughly 20% of QBI after SE deductions; positive.
    assert qbid > 0
    assert qbid < 50_000 * 0.20  # Not full 20% — SE tax deduction reduces QBI first


def test_qbi_calculate_returns_parameters():
    """Calculate response should include the parameter snapshot used."""
    r = client.post(
        "/api/qbi/calculate",
        json={"filing_status": "SINGLE", "year": 2025},
    )
    body = r.json()
    assert "parameters" in body
    assert body["parameters"]["max_rate"] == 0.20


def _calc(**kwargs):
    """POST /calculate with defaults and return the parsed 200 body."""
    r = client.post("/api/qbi/calculate", json={"year": 2025, **kwargs})
    assert r.status_code == 200, r.text
    return r.json()


# $250k QBI sits between the 2025 SINGLE ($197,300) and JOINT ($394,600)
# phase-out thresholds, so filing status visibly changes the result.
PHASE_OUT_STRADDLING_INCOME = 250_000

QBID = "qualified_business_income_deduction"


@pytest.mark.parametrize(
    "filing_status",
    ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"],
)
def test_qbi_calculate_simulation_applies_requested_filing_status(filing_status):
    """The response echoes the *simulation's* filing_status output — it must
    match the request for every supported status (regression for the bug
    where HOH/SEPARATE computed as SINGLE and SURVIVING_SPOUSE as JOINT)."""
    body = _calc(filing_status=filing_status, self_employment_income=50_000)
    assert body["filing_status"] == filing_status
    assert body["errors"] == {}
    assert body["outputs"][QBID] > 0


def test_qbi_calculate_phase_out_params_differ_single_vs_joint():
    single = _calc(filing_status="SINGLE")["parameters"]
    joint = _calc(filing_status="JOINT")["parameters"]
    assert single["phase_out_start"] == single["phase_out_start_single"]
    assert joint["phase_out_start"] == joint["phase_out_start_joint"]
    assert joint["phase_out_start"] > single["phase_out_start"]
    assert joint["phase_out_length"] > single["phase_out_length"]


def test_qbi_calculate_filing_status_changes_phase_out_outcome():
    """Same income straddling the SINGLE threshold: JOINT and SURVIVING_SPOUSE
    (no living spouse, joint-level thresholds) get the full deduction, SINGLE
    gets a phased-out one."""
    single = _calc(
        filing_status="SINGLE",
        self_employment_income=PHASE_OUT_STRADDLING_INCOME,
    )
    joint = _calc(
        filing_status="JOINT",
        self_employment_income=PHASE_OUT_STRADDLING_INCOME,
    )
    surviving = _calc(
        filing_status="SURVIVING_SPOUSE",
        self_employment_income=PHASE_OUT_STRADDLING_INCOME,
    )
    # Surviving spouse files alone but uses joint thresholds — with a
    # no-income spouse, the joint result matches exactly.
    assert surviving["outputs"][QBID] == joint["outputs"][QBID]
    assert surviving["outputs"][QBID] > single["outputs"][QBID]
    assert surviving["parameters"]["phase_out_start"] == (
        joint["parameters"]["phase_out_start_joint"]
    )


def test_qbi_calculate_negative_income_loss():
    """A business loss yields zero QBID (no negative deduction)."""
    body = _calc(filing_status="SINGLE", self_employment_income=-50_000)
    assert body["errors"] == {}
    assert body["outputs"][QBID] == 0
    assert body["outputs"]["adjusted_gross_income"] < 0


def test_qbi_calculate_above_threshold_wage_limitation():
    """Above the fully-phased-in threshold, the W-2 wage limitation binds:
    zero wages/UBIA means zero QBID; sufficient wages restore it."""
    no_wages = _calc(filing_status="SINGLE", self_employment_income=500_000)
    assert no_wages["outputs"][QBID] == 0
    with_wages = _calc(
        filing_status="SINGLE",
        self_employment_income=500_000,
        w2_wages_from_qualified_business=200_000,
    )
    assert with_wages["outputs"][QBID] > 0


@pytest.mark.parametrize(
    "bad_field",
    [
        {"filing_status": "MARRIED"},
        {"filing_status": "single"},
        {"state_code": "ZZ"},
        {"year": 2017},
        {"year": 2050},
        {"self_employment_income": 1e12},
        {"employment_income": -1e12},
    ],
)
def test_qbi_calculate_invalid_input_returns_422(bad_field):
    r = client.post("/api/qbi/calculate", json={"year": 2025, **bad_field})
    assert r.status_code == 422
