"""Tests that the PolicyEngine parameter helpers return live values."""

from app.services import pe_parameters as pe


def test_default_year_is_a_recent_year():
    assert 2024 <= pe.DEFAULT_YEAR <= 2030


def test_max_rate_is_twenty_percent():
    assert pe.qbi_max_rate() == 0.20


def test_reit_ptp_rate_matches_max_rate():
    assert pe.qbi_reit_ptp_rate() == pe.qbi_max_rate()


def test_w2_wages_rates():
    assert pe.qbi_w2_wages_rate() == 0.50
    assert pe.qbi_w2_wages_alt_rate() == 0.25
    assert pe.qbi_business_property_rate() == 0.025


def test_thresholds_in_expected_range():
    single = pe.qbi_threshold("SINGLE")
    joint = pe.qbi_threshold("JOINT")
    # Sanity bounds for inflation-adjusted thresholds since 2018.
    assert 150_000 < single < 250_000
    assert 300_000 < joint < 500_000
    # Joint is exactly 2× single per §199A(e)(2).
    assert joint == 2 * single


def test_phase_out_lengths_doubled_for_obbba():
    # Pre-OBBBA (TCJA): $50k single / $100k joint
    assert pe.qbi_phase_out_length("SINGLE", 2025) == 50_000
    assert pe.qbi_phase_out_length("JOINT", 2025) == 100_000
    # Post-OBBBA (2026+): expanded to $75k / $150k
    assert pe.qbi_phase_out_length("SINGLE", 2026) == 75_000
    assert pe.qbi_phase_out_length("JOINT", 2026) == 150_000


def test_minimum_floor_kicks_in_2026():
    assert pe.qbi_floor_in_effect(2025) is False
    assert pe.qbi_floor_in_effect(2026) is True


def test_floor_amount_is_400_at_qbi_threshold():
    # Below $1,000 QBI: no floor. At/above: $400.
    assert pe.qbi_floor_amount(0, 2026) == 0
    assert pe.qbi_floor_amount(999, 2026) == 0
    assert pe.qbi_floor_amount(1_000, 2026) == 400
    assert pe.qbi_floor_amount(1_000_000, 2026) == 400
