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
