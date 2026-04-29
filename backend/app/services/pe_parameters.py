"""Live accessors for PolicyEngine-US QBI parameters.

All values are read from the installed policyengine_us package at the
requested year, so the law structure and form mappings stay in sync
with the canonical YAML rather than drifting against hardcoded copies.
"""

from policyengine_us.system import system

DEFAULT_YEAR = 2025


def pe_params(year: int = DEFAULT_YEAR):
    """Return the parameter tree for the start of the given calendar year."""
    return system.parameters(f"{year}-01-01")


def qbi_threshold(filing_status: str, year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.phase_out.start[filing_status])


def qbi_phase_out_length(filing_status: str, year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.phase_out.length[filing_status])


def qbi_max_rate(year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.max.rate)


def qbi_w2_wages_rate(year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.max.w2_wages.rate)


def qbi_w2_wages_alt_rate(year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.max.w2_wages.alt_rate)


def qbi_business_property_rate(year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.max.business_property.rate)


def qbi_reit_ptp_rate(year: int = DEFAULT_YEAR) -> float:
    return float(pe_params(year).gov.irs.deductions.qbi.max.reit_ptp_rate)


def qbi_floor_in_effect(year: int = DEFAULT_YEAR) -> bool:
    return bool(pe_params(year).gov.irs.deductions.qbi.deduction_floor.in_effect)


def qbi_floor_amount(qbi_value: float, year: int = DEFAULT_YEAR) -> float:
    """Look up the OBBBA minimum-deduction floor for the given QBI level."""
    return float(pe_params(year).gov.irs.deductions.qbi.deduction_floor.amount.calc(qbi_value))
