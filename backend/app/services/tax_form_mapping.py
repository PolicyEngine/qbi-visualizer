"""Service for building tax form to PolicyEngine mappings."""

from typing import List, Dict
from app.models.tax_form_mapping import (
    ImplementationStatus,
    FormLineMapping,
    FormScheduleMapping,
    TaxFormMapping,
    FormMappingResponse,
    FormSummary,
)


def build_form_8995_mapping() -> TaxFormMapping:
    """Build the Form 8995 (Simplified) mapping."""

    lines = [
        FormLineMapping(
            line_number="1(a-e)",
            line_label="Trade, business, or aggregation name",
            description="Name and EIN of each qualified trade or business (up to 5)",
            status=ImplementationStatus.PARTIAL,
            pe_variable="qualified_business_income",
            pe_formula="Aggregated per person, not per business",
            gap_description="PE doesn't track individual businesses separately - all QBI is combined per person",
            form_instructions="Enter the name of each trade or business. If aggregating, enter 'Aggregation 1', etc."
        ),
        FormLineMapping(
            line_number="2",
            line_label="Total qualified business income or (loss)",
            description="Sum of QBI from all trades/businesses",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qualified_business_income",
            pe_formula="sum(income_source × would_be_qualified) - qbi_deductions",
            form_instructions="Combine the amounts from line 1, column (c)"
        ),
        FormLineMapping(
            line_number="3",
            line_label="Qualified business net (loss) carryforward from prior years",
            description="QBI losses carried forward from previous tax years",
            status=ImplementationStatus.MISSING,
            gap_description="PE uses max(0, QBI) which zeros out losses. No carryforward tracking exists.",
            form_instructions="Include the qualified portion of trade or business (loss) carryforward allowed in calculating taxable income"
        ),
        FormLineMapping(
            line_number="4",
            line_label="Total qualified business income",
            description="Line 2 + Line 3",
            status=ImplementationStatus.PARTIAL,
            pe_variable="qualified_business_income",
            pe_formula="max(0, gross_qbi - deductions)",
            gap_description="Missing carryforward component from Line 3",
            form_instructions="Add lines 2 and 3"
        ),
        FormLineMapping(
            line_number="5",
            line_label="Qualified business income component",
            description="20% of Line 4 (if positive)",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qbid_amount",
            pe_formula="0.20 × qualified_business_income",
            form_instructions="Multiply line 4 by 20% (0.20). If line 4 is less than zero, enter -0-"
        ),
        FormLineMapping(
            line_number="6",
            line_label="Qualified REIT dividends and publicly traded partnership (PTP) income or (loss)",
            description="REIT dividends and PTP ordinary income",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qualified_reit_and_ptp_income",
            pe_formula="qualified_reit_and_ptp_income (combined input variable)",
            form_instructions="Enter qualified REIT dividends and qualified PTP income or (loss)"
        ),
        FormLineMapping(
            line_number="7",
            line_label="Qualified REIT dividends and qualified PTP (loss) carryforward from prior years",
            description="PTP losses carried forward",
            status=ImplementationStatus.MISSING,
            gap_description="No PTP loss carryforward tracking",
            form_instructions="Include the qualified portion of PTP (loss) carryforward allowed in calculating taxable income"
        ),
        FormLineMapping(
            line_number="8",
            line_label="Total qualified REIT dividends and PTP income",
            description="Line 6 + Line 7",
            status=ImplementationStatus.PARTIAL,
            pe_variable="qualified_reit_and_ptp_income",
            pe_formula="Equals Line 6 only; Line 7 carryforward is not tracked",
            gap_description="REIT/PTP loss carryforward (Line 7) is not tracked in PolicyEngine",
            form_instructions="Add lines 6 and 7"
        ),
        FormLineMapping(
            line_number="9",
            line_label="REIT and PTP component",
            description="20% of Line 8 (if positive)",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qbid_amount (REIT/PTP component)",
            pe_formula="reit_ptp_rate × max(0, qualified_reit_and_ptp_income)",
            form_instructions="Multiply line 8 by 20% (0.20). If line 8 is less than zero, enter -0-"
        ),
        FormLineMapping(
            line_number="10",
            line_label="Qualified business income deduction before income limitation",
            description="Line 5 + Line 9",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qbid_amount (summed across persons)",
            pe_formula="non_sstb_component + sstb_component + reit_ptp_component",
            form_instructions="Add lines 5 and 9"
        ),
        FormLineMapping(
            line_number="11",
            line_label="Taxable income before qualified business income deduction",
            description="From Form 1040, calculated before QBID",
            status=ImplementationStatus.COMPLETE,
            pe_variable="taxable_income_less_qbid",
            pe_formula="Taxable income computed without QBID to avoid circular reference",
            form_instructions="See instructions for your return type"
        ),
        FormLineMapping(
            line_number="12",
            line_label="Net capital gain",
            description="Net capital gain plus qualified dividends",
            status=ImplementationStatus.COMPLETE,
            pe_variable="adjusted_net_capital_gain",
            pe_formula="long_term_capital_gains - short_term_capital_losses + qualified_dividends",
            form_instructions="Form 1040 line 3a plus net capital gain from Schedule D"
        ),
        FormLineMapping(
            line_number="13",
            line_label="Line 11 minus Line 12",
            description="Taxable income minus capital gains",
            status=ImplementationStatus.COMPLETE,
            pe_formula="taxable_income_less_qbid - adjusted_net_capital_gain",
            form_instructions="Subtract line 12 from line 11. If zero or less, enter -0-"
        ),
        FormLineMapping(
            line_number="14",
            line_label="Income limitation",
            description="20% of Line 13",
            status=ImplementationStatus.COMPLETE,
            pe_formula="0.20 × max(0, taxinc_less_qbid - netcg_qdiv)",
            form_instructions="Multiply line 13 by 20% (0.20)"
        ),
        FormLineMapping(
            line_number="15",
            line_label="Qualified business income deduction",
            description="Smaller of Line 10 or Line 14",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qualified_business_income_deduction",
            pe_formula="min(uncapped_qbid, taxinc_cap), then max with 2026+ minimum-deduction floor",
            form_instructions="Enter the smaller of line 10 or line 14"
        ),
        FormLineMapping(
            line_number="16",
            line_label="Total qualified business (loss) carryforward",
            description="QBI loss to carry to next year (if Line 4 negative)",
            status=ImplementationStatus.MISSING,
            gap_description="No loss carryforward tracking - losses are zeroed out",
            form_instructions="Combine lines 2 and 3. If the result is less than zero, enter it as a positive"
        ),
        FormLineMapping(
            line_number="17",
            line_label="Total qualified REIT dividends and PTP (loss) carryforward",
            description="PTP loss to carry to next year (if Line 8 negative)",
            status=ImplementationStatus.MISSING,
            gap_description="No PTP loss carryforward tracking",
            form_instructions="Combine lines 6 and 7. If the result is less than zero, enter it as a positive"
        ),
    ]

    complete = sum(1 for l in lines if l.status == ImplementationStatus.COMPLETE)
    partial = sum(1 for l in lines if l.status == ImplementationStatus.PARTIAL)
    missing = sum(1 for l in lines if l.status == ImplementationStatus.MISSING)

    return TaxFormMapping(
        form_number="8995",
        form_title="Qualified Business Income Deduction Simplified Computation",
        tax_year=2025,
        description="Use this form if your taxable income is at or below the threshold and you're not a patron of an agricultural cooperative.",
        who_can_use="Taxpayers with taxable income at or below $197,300 (single) or $394,600 (MFJ) who have QBI, qualified REIT dividends, or qualified PTP income",
        threshold_single=197300,
        threshold_joint=394600,
        irs_url="https://www.irs.gov/pub/irs-pdf/f8995.pdf",
        instructions_url="https://www.irs.gov/instructions/i8995",
        total_lines=len(lines),
        complete_lines=complete,
        partial_lines=partial,
        missing_lines=missing,
        lines=lines,
        schedules=[]
    )


def build_form_8995a_mapping() -> TaxFormMapping:
    """Build the Form 8995-A (Complex) mapping."""

    # Main form lines (Part I-IV)
    lines = [
        FormLineMapping(
            line_number="Part I",
            line_label="Trade or Business Information",
            description="Per-business QBI, W-2 wages, and UBIA tracking",
            status=ImplementationStatus.PARTIAL,
            pe_variable="qualified_business_income, w2_wages_from_qualified_business, unadjusted_basis_qualified_property",
            gap_description="PE aggregates per person, not per business. Cannot apply wage limits separately per business.",
            form_instructions="Complete a row for each trade or business"
        ),
        FormLineMapping(
            line_number="Part II",
            line_label="Determine Your Qualified Business Income Component",
            description="Calculate QBI component with W-2/UBIA limitations",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qbid_amount",
            pe_formula="Complex calculation with wage cap, alt cap, and phase-out",
            form_instructions="Follow Worksheet 12-A logic"
        ),
        FormLineMapping(
            line_number="Part III",
            line_label="Phased-In Reduction",
            description="Phase-in of W-2/UBIA limitations",
            status=ImplementationStatus.COMPLETE,
            pe_formula="reduction_rate = min(1, (taxinc - threshold) / phase_length)",
            form_instructions="Complete only if taxable income is within phase-in range"
        ),
        FormLineMapping(
            line_number="Part IV",
            line_label="Determine Your Qualified Business Income Deduction",
            description="Final QBID calculation combining QBI and REIT/PTP components",
            status=ImplementationStatus.COMPLETE,
            pe_variable="qualified_business_income_deduction",
            pe_formula="non_sstb + sstb + reit_ptp components, capped at 20% × (taxable income − net capital gain), with 2026+ minimum-deduction floor",
            form_instructions="Combine QBI component with REIT/PTP component, apply income limit"
        ),
    ]

    # Schedule A - SSTB
    schedule_a = FormScheduleMapping(
        schedule_id="A",
        schedule_name="Specified Service Trade or Business",
        description="Calculate SSTB phase-out for taxpayers in the phase-in range",
        who_must_file="Taxpayers with SSTB income and taxable income within phase-in range",
        status=ImplementationStatus.COMPLETE,
        status_notes="PE correctly implements SSTB phase-out via business_is_sstb boolean and applicable_rate calculation",
        lines=[
            FormLineMapping(
                line_number="A-1",
                line_label="SSTB identification",
                description="Is the business an SSTB?",
                status=ImplementationStatus.COMPLETE,
                pe_variable="business_is_sstb",
                form_instructions="Check if business performs services in specified fields"
            ),
            FormLineMapping(
                line_number="A-9",
                line_label="Applicable percentage",
                description="Phase-out percentage based on taxable income",
                status=ImplementationStatus.COMPLETE,
                pe_formula="applicable_rate = 1 - reduction_rate",
                form_instructions="Calculate phase-out percentage"
            ),
            FormLineMapping(
                line_number="A-11",
                line_label="SSTB QBI after phase-out",
                description="QBI × applicable percentage",
                status=ImplementationStatus.COMPLETE,
                pe_formula="qbi × sstb_multiplier where sstb_multiplier = applicable_rate for SSTBs",
                form_instructions="Multiply QBI by applicable percentage"
            ),
        ],
        key_requirements=[
            "Health, law, accounting, actuarial science",
            "Performing arts, consulting, athletics",
            "Financial services, brokerage",
            "Any business where principal asset is reputation/skill",
            "De minimis: <10% (≤$25M) or <5% (>$25M) from specified services"
        ]
    )

    # Schedule B - Aggregation
    schedule_b = FormScheduleMapping(
        schedule_id="B",
        schedule_name="Aggregation of Business Operations",
        description="Elect to aggregate multiple qualifying businesses",
        who_must_file="Taxpayers electing to aggregate businesses under Treas. Reg. § 1.199A-4",
        status=ImplementationStatus.MISSING,
        status_notes="PE does not support business aggregation election. Each business is treated independently.",
        lines=[
            FormLineMapping(
                line_number="B-1",
                line_label="Aggregation election",
                description="Elect to combine businesses for W-2 wage purposes",
                status=ImplementationStatus.MISSING,
                gap_description="Cannot aggregate businesses to share W-2 wage capacity",
                form_instructions="List all businesses being aggregated"
            ),
        ],
        key_requirements=[
            "50%+ ownership in each business",
            "Same tax year for all businesses",
            "No SSTB businesses in aggregation",
            "Meet 2+ of: similar services, shared facilities, operational coordination"
        ]
    )

    # Schedule C - Loss Netting
    schedule_c = FormScheduleMapping(
        schedule_id="C",
        schedule_name="Loss Netting and Carryforward",
        description="Net QBI losses across businesses and track carryforwards",
        who_must_file="Taxpayers with QBI losses in current or prior years",
        status=ImplementationStatus.MISSING,
        status_notes="PE uses max(0, QBI) which zeros out losses. No carryforward mechanism exists.",
        lines=[
            FormLineMapping(
                line_number="C-1",
                line_label="Current year QBI loss",
                description="Negative QBI from current year businesses",
                status=ImplementationStatus.MISSING,
                gap_description="Losses are zeroed, not tracked",
                form_instructions="Enter negative QBI amounts"
            ),
            FormLineMapping(
                line_number="C-2",
                line_label="Prior year loss carryforward",
                description="QBI losses from prior years",
                status=ImplementationStatus.MISSING,
                gap_description="No multi-year loss tracking",
                form_instructions="Enter carryforward from prior Form 8995-A"
            ),
            FormLineMapping(
                line_number="C-3",
                line_label="Loss allocation",
                description="Proportionally allocate losses across profitable businesses",
                status=ImplementationStatus.MISSING,
                gap_description="No loss allocation algorithm",
                form_instructions="Allocate losses proportionally"
            ),
        ],
        key_requirements=[
            "Losses offset positive QBI proportionally",
            "Excess losses carry forward indefinitely",
            "Suspended losses retain QBI character",
            "Pre-2018 losses are permanently non-QBI"
        ]
    )

    # Schedule D - Cooperatives
    schedule_d = FormScheduleMapping(
        schedule_id="D",
        schedule_name="Special Rules for Patrons of Agricultural or Horticultural Cooperatives",
        description="Calculate QBID for cooperative patrons under §199A(g)",
        who_must_file="Patrons who receive qualified payments from a specified cooperative",
        status=ImplementationStatus.MISSING,
        status_notes="§199A(g) cooperative provisions are not implemented in PolicyEngine",
        lines=[
            FormLineMapping(
                line_number="D-1",
                line_label="Qualified payments from cooperative",
                description="Patronage dividends qualifying for QBID",
                status=ImplementationStatus.MISSING,
                gap_description="No cooperative payment tracking",
                form_instructions="Enter qualified payments from Form 1099-PATR"
            ),
            FormLineMapping(
                line_number="D-2",
                line_label="Patron reduction",
                description="Lesser of 9% QBI or 50% W-2 wages",
                status=ImplementationStatus.MISSING,
                gap_description="Cooperative patron deduction not calculated",
                form_instructions="Calculate reduction for cooperative patron"
            ),
        ],
        key_requirements=[
            "Must receive qualified payments from specified cooperative",
            "Reduction = lesser of 9% of QBI or 50% of W-2 wages allocable",
            "Cooperative can pass through its QBID to patrons",
            "Reported on Form 1099-PATR"
        ]
    )

    all_lines = lines
    all_schedules = [schedule_a, schedule_b, schedule_c, schedule_d]

    # Count statuses
    complete = sum(1 for l in all_lines if l.status == ImplementationStatus.COMPLETE)
    partial = sum(1 for l in all_lines if l.status == ImplementationStatus.PARTIAL)
    missing = sum(1 for l in all_lines if l.status == ImplementationStatus.MISSING)

    for sched in all_schedules:
        complete += sum(1 for l in sched.lines if l.status == ImplementationStatus.COMPLETE)
        partial += sum(1 for l in sched.lines if l.status == ImplementationStatus.PARTIAL)
        missing += sum(1 for l in sched.lines if l.status == ImplementationStatus.MISSING)

    return TaxFormMapping(
        form_number="8995-A",
        form_title="Qualified Business Income Deduction",
        tax_year=2025,
        description="Use this form if your taxable income exceeds the threshold, you have SSTB income in the phase-in range, or you're a patron of an agricultural cooperative.",
        who_can_use="Taxpayers with taxable income above $197,300 (single) or $394,600 (MFJ), or with SSTB income in phase-in range, or cooperative patrons",
        threshold_single=197300,
        threshold_joint=394600,
        irs_url="https://www.irs.gov/pub/irs-pdf/f8995a.pdf",
        instructions_url="https://www.irs.gov/instructions/i8995a",
        total_lines=len(all_lines) + sum(len(s.lines) for s in all_schedules),
        complete_lines=complete,
        partial_lines=partial,
        missing_lines=missing,
        lines=all_lines,
        schedules=all_schedules
    )


def build_form_mapping_response() -> FormMappingResponse:
    """Build the complete form mapping response."""

    form_8995 = build_form_8995_mapping()
    form_8995a = build_form_8995a_mapping()

    total_complete = form_8995.complete_lines + form_8995a.complete_lines
    total_partial = form_8995.partial_lines + form_8995a.partial_lines
    total_missing = form_8995.missing_lines + form_8995a.missing_lines

    critical_gaps = [
        {
            "id": "loss_carryforward",
            "title": "QBI Loss Carryforward Not Implemented",
            "form_lines": "Form 8995 Lines 3, 7, 16, 17; Form 8995-A Schedule C",
            "description": "PE uses max(0, QBI) which zeros out losses. Negative QBI should carry forward to reduce future years' deductions.",
            "impact": "Medium - affects taxpayers with business losses",
            "fix_complexity": "Medium - requires new state variables for multi-year tracking"
        },
        {
            "id": "per_business",
            "title": "Per-Business Tracking Missing",
            "form_lines": "Form 8995 Line 1; Form 8995-A Part I",
            "description": "PE aggregates all QBI per person. Cannot separately track W-2 wages and UBIA per business, which affects wage limitation calculations.",
            "impact": "Medium - affects taxpayers with multiple businesses",
            "fix_complexity": "High - architectural change to support multiple businesses"
        },
        {
            "id": "aggregation",
            "title": "Business Aggregation Election Missing",
            "form_lines": "Form 8995-A Schedule B",
            "description": "Taxpayers cannot elect to aggregate qualifying businesses to share W-2 wage capacity across businesses.",
            "impact": "Medium - affects taxpayers with multiple businesses",
            "fix_complexity": "High - requires new election and aggregation logic"
        },
        {
            "id": "cooperatives",
            "title": "Cooperative Patron Rules Missing",
            "form_lines": "Form 8995-A Schedule D",
            "description": "§199A(g) cooperative provisions are not implemented. Agricultural/horticultural cooperative patrons cannot claim their special deduction.",
            "impact": "Low - specialized use case for farmers",
            "fix_complexity": "Medium - requires new variables and Form 1099-PATR handling"
        },
    ]

    working_correctly = [
        {
            "id": "base_rate",
            "title": "20% Base Deduction Rate",
            "form_lines": "Form 8995 Lines 5, 9, 14",
            "description": "The 20% rate is correctly applied to QBI and the income limitation"
        },
        {
            "id": "wage_cap",
            "title": "W-2 Wage Limitation (50%)",
            "form_lines": "Form 8995-A Part II",
            "description": "The 50% of W-2 wages cap is correctly implemented"
        },
        {
            "id": "alt_cap",
            "title": "Alternative Cap (25% W-2 + 2.5% UBIA)",
            "form_lines": "Form 8995-A Part II",
            "description": "The alternative limitation using wages plus property basis is correct"
        },
        {
            "id": "sstb_phaseout",
            "title": "SSTB Phase-Out",
            "form_lines": "Form 8995-A Schedule A",
            "description": "SSTB income correctly phases out between threshold and threshold + range"
        },
        {
            "id": "income_cap",
            "title": "Taxable Income Cap",
            "form_lines": "Form 8995 Lines 11-15",
            "description": "QBID is correctly limited to 20% of (taxable income - capital gains)"
        },
        {
            "id": "capital_gains_exclusion",
            "title": "Capital Gains Exclusion",
            "form_lines": "Form 8995 Line 12",
            "description": "Net capital gains and qualified dividends are correctly excluded from the income cap"
        },
        {
            "id": "thresholds",
            "title": "Inflation-Adjusted Thresholds",
            "form_lines": "Instructions",
            "description": "Phase-out start thresholds (e.g., $197,300 single / $394,600 MFJ for 2025) are correctly parameterized and inflation-adjusted"
        },
        {
            "id": "reit_ptp",
            "title": "REIT/PTP Component",
            "form_lines": "Form 8995 Lines 6-9; Form 8995-A Part IV",
            "description": "20% of qualified_reit_and_ptp_income is added to the per-person QBID without wage or UBIA limits, matching §199A(b)(1)(B)"
        },
        {
            "id": "minimum_floor",
            "title": "Minimum Deduction Floor (2026+)",
            "form_lines": "§199A(i)",
            "description": "$400 minimum deduction for taxpayers with at least $1,000 of QBI, effective for tax years beginning after Dec 31, 2025 (added by the One Big Beautiful Bill Act)"
        },
        {
            "id": "phaseout_range",
            "title": "Phase-Out Range",
            "form_lines": "Instructions",
            "description": "Phase-out ranges are correctly parameterized: $50,000 single / $100,000 joint pre-2026, expanded to $75,000 / $150,000 starting 2026 under OBBBA"
        },
    ]

    return FormMappingResponse(
        forms=[form_8995, form_8995a],
        summary=FormSummary(
            total_elements=total_complete + total_partial + total_missing,
            complete=total_complete,
            partial=total_partial,
            missing=total_missing,
            implementation_pct=round(100 * (total_complete + 0.5 * total_partial) / (total_complete + total_partial + total_missing), 1)
        ),
        critical_gaps=critical_gaps,
        working_correctly=working_correctly
    )
