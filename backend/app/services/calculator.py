"""QBI calculator using PolicyEngine US."""

from policyengine_us import Simulation


# All person-level input variables relevant to QBI
QBI_INCOME_INPUTS = [
    {
        "name": "self_employment_income",
        "label": "Self-employment income",
        "group": "QBI Income Sources",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "partnership_s_corp_income",
        "label": "Partnership / S-corp income",
        "group": "QBI Income Sources",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "farm_operations_income",
        "label": "Farm operations income",
        "group": "QBI Income Sources",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "farm_rent_income",
        "label": "Farm rental income",
        "group": "QBI Income Sources",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "rental_income",
        "label": "Rental income",
        "group": "QBI Income Sources",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "estate_income",
        "label": "Estate / trust income",
        "group": "QBI Income Sources",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "self_employment_income_would_be_qualified",
        "label": "SE income is qualified",
        "group": "QBI Income Sources",
        "default": True,
        "type": "bool",
    },
    {
        "name": "partnership_s_corp_income_would_be_qualified",
        "label": "Partnership/S-corp income is qualified",
        "group": "QBI Income Sources",
        "default": True,
        "type": "bool",
    },
    {
        "name": "farm_operations_income_would_be_qualified",
        "label": "Farm operations income is qualified",
        "group": "QBI Income Sources",
        "default": True,
        "type": "bool",
    },
    {
        "name": "farm_rent_income_would_be_qualified",
        "label": "Farm rent income is qualified",
        "group": "QBI Income Sources",
        "default": True,
        "type": "bool",
    },
    {
        "name": "rental_income_would_be_qualified",
        "label": "Rental income is qualified",
        "group": "QBI Income Sources",
        "default": True,
        "type": "bool",
    },
    {
        "name": "estate_income_would_be_qualified",
        "label": "Estate income is qualified",
        "group": "QBI Income Sources",
        "default": True,
        "type": "bool",
    },
    {
        "name": "sstb_self_employment_income",
        "label": "SSTB self-employment income",
        "group": "SSTB Income",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "sstb_self_employment_income_would_be_qualified",
        "label": "SSTB SE income is qualified",
        "group": "SSTB Income",
        "default": True,
        "type": "bool",
    },
    {
        "name": "business_is_sstb",
        "label": "Business is SSTB (legacy flag)",
        "group": "SSTB Income",
        "default": False,
        "type": "bool",
    },
    {
        "name": "w2_wages_from_qualified_business",
        "label": "W-2 wages from qualified business",
        "group": "Wage & Property Limitation",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "unadjusted_basis_qualified_property",
        "label": "UBIA of qualified property",
        "group": "Wage & Property Limitation",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "sstb_w2_wages_from_qualified_business",
        "label": "SSTB allocable W-2 wages",
        "group": "Wage & Property Limitation",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "sstb_unadjusted_basis_qualified_property",
        "label": "SSTB allocable UBIA",
        "group": "Wage & Property Limitation",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "qualified_reit_and_ptp_income",
        "label": "Qualified REIT dividends & PTP income",
        "group": "REIT & PTP",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "employment_income",
        "label": "W-2 employment income",
        "group": "Other Income",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "long_term_capital_gains",
        "label": "Long-term capital gains",
        "group": "Other Income",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "short_term_capital_gains",
        "label": "Short-term capital gains",
        "group": "Other Income",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "qualified_dividend_income",
        "label": "Qualified dividend income",
        "group": "Other Income",
        "default": 0,
        "type": "currency",
    },
    {
        "name": "taxable_interest_income",
        "label": "Taxable interest income",
        "group": "Other Income",
        "default": 0,
        "type": "currency",
    },
]

# Output variables to compute
QBI_OUTPUTS = [
    {
        "name": "qualified_business_income_deduction",
        "label": "Qualified Business Income Deduction",
        "entity": "tax_unit",
        "primary": True,
    },
    {
        "name": "qualified_business_income",
        "label": "Non-SSTB Qualified Business Income",
        "entity": "person",
    },
    {
        "name": "sstb_qualified_business_income",
        "label": "SSTB Qualified Business Income",
        "entity": "person",
    },
    {
        "name": "qbid_amount",
        "label": "Per-Person QBID Amount (before TI cap)",
        "entity": "person",
    },
    {
        "name": "taxable_income_less_qbid",
        "label": "Taxable Income (before QBID)",
        "entity": "tax_unit",
    },
    {
        "name": "adjusted_net_capital_gain",
        "label": "Adjusted Net Capital Gain",
        "entity": "tax_unit",
    },
    {
        "name": "self_employment_tax_ald_person",
        "label": "SE Tax Deduction (QBI reduction)",
        "entity": "person",
    },
    {
        "name": "self_employed_health_insurance_ald_person",
        "label": "SE Health Insurance Deduction (QBI reduction)",
        "entity": "person",
    },
    {
        "name": "self_employed_pension_contribution_ald_person",
        "label": "SE Pension Deduction (QBI reduction)",
        "entity": "person",
    },
    {
        "name": "adjusted_gross_income",
        "label": "Adjusted Gross Income",
        "entity": "tax_unit",
    },
    {
        "name": "taxable_income",
        "label": "Taxable Income (after QBID)",
        "entity": "tax_unit",
    },
    {
        "name": "income_tax_before_credits",
        "label": "Income Tax Before Credits",
        "entity": "tax_unit",
    },
]


def get_input_metadata():
    """Return metadata about all QBI calculator inputs."""
    return QBI_INCOME_INPUTS


def get_output_metadata():
    """Return metadata about all QBI calculator outputs."""
    return QBI_OUTPUTS


def calculate(inputs: dict) -> dict:
    """
    Run a QBI calculation using PolicyEngine US.

    Args:
        inputs: Dictionary with keys matching variable names and values.
                Must include 'filing_status' and 'year'.

    Returns:
        Dictionary with input metadata, output values, and parameters.
    """
    year = str(inputs.get("year", 2024))
    filing_status = inputs.get("filing_status", "SINGLE")
    state_code = inputs.get("state_code", "TX")  # Default to no-income-tax state

    # Build person-level inputs
    person_vars = {"age": {year: 40}}
    for var_def in QBI_INCOME_INPUTS:
        var_name = var_def["name"]
        if var_name in inputs:
            val = inputs[var_name]
        else:
            val = var_def["default"]
        person_vars[var_name] = {year: val}

    # Build situation
    is_joint = filing_status in ("JOINT", "SURVIVING_SPOUSE")
    members = ["you", "spouse"] if is_joint else ["you"]

    situation = {
        "people": {
            "you": person_vars,
        },
        "tax_units": {
            "tax_unit": {
                "members": members,
            }
        },
        "families": {
            "family": {
                "members": members,
            }
        },
        "spm_units": {
            "spm_unit": {
                "members": members,
            }
        },
        "households": {
            "household": {
                "members": members,
                "state_code": {year: state_code},
            }
        },
        "marital_units": {},
    }

    # Add spouse if joint
    if is_joint:
        situation["people"]["spouse"] = {"age": {year: 40}}
        situation["marital_units"]["marital_unit"] = {
            "members": ["you", "spouse"],
        }
    else:
        situation["marital_units"]["marital_unit"] = {
            "members": ["you"],
        }

    sim = Simulation(situation=situation)

    # Compute all outputs
    results = {}
    for output_def in QBI_OUTPUTS:
        var_name = output_def["name"]
        try:
            value = sim.calculate(var_name, year)
            if output_def["entity"] == "tax_unit":
                results[var_name] = round(float(value[0]), 2)
            else:
                # Person-level: sum across all people (primarily just "you")
                results[var_name] = round(float(value[0]), 2)
        except Exception as e:
            results[var_name] = {"error": str(e)}

    # Get parameter values used
    params = sim.tax_benefit_system.parameters
    qbi_params = params.gov.irs.deductions.qbi
    period = f"{year}-01-01"

    try:
        param_values = {
            "max_rate": float(qbi_params.max.rate(period)),
            "w2_wages_rate": float(qbi_params.max.w2_wages.rate(period)),
            "w2_wages_alt_rate": float(qbi_params.max.w2_wages.alt_rate(period)),
            "business_property_rate": float(
                qbi_params.max.business_property.rate(period)
            ),
            "phase_out_start_single": float(
                qbi_params.phase_out.start.SINGLE(period)
            ),
            "phase_out_start_joint": float(
                qbi_params.phase_out.start.JOINT(period)
            ),
            "phase_out_length_single": float(
                qbi_params.phase_out.length.SINGLE(period)
            ),
            "phase_out_length_joint": float(
                qbi_params.phase_out.length.JOINT(period)
            ),
        }
    except Exception:
        param_values = {}

    return {
        "outputs": results,
        "parameters": param_values,
        "year": int(year),
        "filing_status": filing_status,
    }
