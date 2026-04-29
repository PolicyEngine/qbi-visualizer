"""Service to build law-structured QBID representation."""

from typing import Dict, List, Optional
from app.models.law_structure import (
    QBIDLawStructure,
    LawSection,
    LegalReference,
    ImplementationStatus,
    InputVariable,
    Parameter,
    ComputationStep,
    AdjacentSection,
)
from app.services import pe_parameters as pe


GITHUB_BASE = "https://github.com/PolicyEngine/policyengine-us/blob/master"
CORNELL_BASE = "https://www.law.cornell.edu/uscode/text/26/199A"


def build_qbid_law_structure(
    variables: Dict,
    parameters: Dict,
    commit_sha: Optional[str] = None
) -> QBIDLawStructure:
    """Build the complete law-structured representation of QBID."""

    sections = [
        _build_section_a_allowance(variables, parameters),
        _build_section_b1_combined_qbi(variables, parameters),
        _build_section_b2_wage_limitation(variables, parameters),
        _build_section_b3_phaseout(variables, parameters),
        _build_section_c_qbi_definition(variables, parameters),
        _build_section_c2_loss_carryover(variables, parameters),
        _build_section_c3_exclusions(variables, parameters),
        _build_section_d_qualified_business(variables, parameters),
        _build_section_d2_sstb(variables, parameters),
        _build_section_e_thresholds(variables, parameters),
        _build_section_i_minimum_deduction(variables, parameters),
        _build_section_g_cooperatives(variables, parameters),
    ]

    # Count implementation status
    complete = sum(1 for s in sections if s.status == ImplementationStatus.COMPLETE)
    partial = sum(1 for s in sections if s.status == ImplementationStatus.PARTIAL)
    missing = sum(1 for s in sections if s.status == ImplementationStatus.MISSING)

    # Build adjacent sections
    adjacent_sections = _build_adjacent_sections()

    return QBIDLawStructure(
        total_sections=len(sections),
        implemented_sections=complete,
        partial_sections=partial,
        missing_sections=missing,
        sections=sections,
        adjacent_sections=adjacent_sections,
        policyengine_commit=commit_sha,
    )


def _build_section_a_allowance(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(a) - Allowance of deduction."""
    return LawSection(
        id="sec_a_allowance",
        section_number="199A(a)",
        title="Allowance of Deduction",
        description="The final deduction is the LESSER OF: (1) the combined QBI amount, or (2) 20% of taxable income exceeding net capital gains.",
        legal_reference=LegalReference(
            section="199A(a)",
            title="Allowance of deduction",
            url=f"{CORNELL_BASE}#a",
            text="In the case of a taxpayer other than a corporation, except as provided in subsection (i), there shall be allowed as a deduction for any taxable year an amount equal to the lesser of— (A) the combined qualified business income amount of the taxpayer, or (B) an amount equal to 20 percent of the excess (if any) of— (i) the taxable income of the taxpayer for the taxable year, over (ii) the net capital gain..."
        ),
        status=ImplementationStatus.COMPLETE,
        inputs=[
            InputVariable(
                name="combined_qbid",
                label="Combined QBI Amount",
                description="Sum of per-business QBID amounts",
                unit="USD"
            ),
            InputVariable(
                name="taxable_income_less_qbid",
                label="Taxable Income (before QBID)",
                unit="USD"
            ),
            InputVariable(
                name="adjusted_net_capital_gain",
                label="Net Capital Gains + Qualified Dividends",
                unit="USD"
            ),
        ],
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.max.rate",
                label="QBID Rate",
                value=pe.qbi_max_rate(),
                unit="rate"
            )
        ],
        steps=[
            ComputationStep(
                id="step_a1",
                description="Calculate taxable income cap (excluding capital gains)",
                formula="taxable_income_cap = 20% × MAX(0, taxable_income − net_capital_gain)",
                formula_latex=r"\text{Cap} = 0.20 \times \max(0, \text{Taxable Income} - \text{Net Capital Gain})",
                inputs=["taxable_income_less_qbid", "adjusted_net_capital_gain"],
                output="taxable_income_cap"
            ),
            ComputationStep(
                id="step_a2",
                description="Apply the taxable income cap (the §199A(i) floor for 2026+ is applied separately afterward)",
                formula="pre_floor_qbid = MIN(combined_qbid, taxable_income_cap)",
                formula_latex=r"\text{Pre-floor QBID} = \min(\text{Combined QBID}, \text{Cap})",
                inputs=["combined_qbid", "taxable_income_cap"],
                output="pre_floor_qbid"
            ),
        ],
        variables_used=["qualified_business_income_deduction", "taxable_income_less_qbid", "adjusted_net_capital_gain"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qualified_business_income_deduction.py",
    )


def _build_section_b1_combined_qbi(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(b)(1) - Combined QBI amount."""
    return LawSection(
        id="sec_b1_combined_qbi",
        section_number="199A(b)(1)",
        title="Combined Qualified Business Income Amount",
        description="Sum of: (A) 20% of QBI from each qualified trade/business (subject to limitations), PLUS (B) 20% of qualified REIT dividends and PTP income.",
        legal_reference=LegalReference(
            section="199A(b)(1)",
            title="Combined qualified business income amount",
            url=f"{CORNELL_BASE}#b_1",
            text="The term 'combined qualified business income amount' means... the sum of— (A) the deductible amount for each qualified trade or business... plus (B) 20 percent of the aggregate amount of the qualified REIT dividends and qualified publicly traded partnership income..."
        ),
        status=ImplementationStatus.COMPLETE,
        inputs=[
            InputVariable(
                name="qbid_amount",
                label="Per-Business QBID Amount",
                description="QBID for each qualified trade/business after limitations",
                unit="USD"
            ),
            InputVariable(
                name="qualified_reit_and_ptp_income",
                label="Qualified REIT Dividends and PTP Income",
                description="Combined qualified REIT dividends and qualified publicly traded partnership income",
                unit="USD"
            ),
        ],
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.max.reit_ptp_rate",
                label="REIT/PTP Deduction Rate",
                value=pe.qbi_reit_ptp_rate(),
                unit="rate"
            ),
        ],
        steps=[
            ComputationStep(
                id="step_b1_1",
                description="Sum QBID from all qualified trades/businesses",
                formula="sum_business_qbid = Σ(qbid_amount for each person)",
                inputs=["qbid_amount"],
                output="sum_business_qbid"
            ),
            ComputationStep(
                id="step_b1_2",
                description="Add 20% of REIT/PTP income",
                formula="reit_ptp_component = 20% × MAX(0, qualified_reit_and_ptp_income)",
                inputs=["qualified_reit_and_ptp_income"],
                output="reit_ptp_component"
            ),
            ComputationStep(
                id="step_b1_3",
                description="Calculate combined amount",
                formula="combined_qbid = sum_business_qbid + reit_ptp_component",
                inputs=["sum_business_qbid", "reit_ptp_component"],
                output="combined_qbid"
            ),
        ],
        variables_used=["qbid_amount", "qualified_reit_and_ptp_income", "qualified_business_income_deduction"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qualified_business_income_deduction.py",
    )


def _build_section_b2_wage_limitation(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(b)(2) - W-2 wage limitation."""
    return LawSection(
        id="sec_b2_wage_limitation",
        section_number="199A(b)(2)",
        title="W-2 Wage and Property Limitation",
        description="For taxpayers above the income threshold, the deduction per business is LIMITED to the GREATER OF: (i) 50% of W-2 wages, OR (ii) 25% of W-2 wages + 2.5% of qualified property basis.",
        legal_reference=LegalReference(
            section="199A(b)(2)",
            title="Determination of deductible amount for each trade or business",
            url=f"{CORNELL_BASE}#b_2",
            text="The deductible amount for any taxable year shall be the lesser of— (A) 20 percent of the taxpayer's qualified business income... or (B) the greater of— (i) 50 percent of the W–2 wages... or (ii) the sum of 25 percent of the W–2 wages... plus 2.5 percent of the unadjusted basis immediately after acquisition of all qualified property."
        ),
        status=ImplementationStatus.COMPLETE,
        inputs=[
            InputVariable(
                name="w2_wages_from_qualified_business",
                label="W-2 Wages Paid",
                description="W-2 wages paid by the qualified business",
                unit="USD"
            ),
            InputVariable(
                name="unadjusted_basis_qualified_property",
                label="UBIA of Qualified Property",
                description="Unadjusted basis immediately after acquisition",
                unit="USD"
            ),
        ],
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.max.w2_wages.rate",
                label="W-2 Wage Rate (primary)",
                value=pe.qbi_w2_wages_rate(),
                unit="rate"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.max.w2_wages.alt_rate",
                label="W-2 Wage Rate (alternative)",
                value=pe.qbi_w2_wages_alt_rate(),
                unit="rate"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.max.business_property.rate",
                label="Property Basis Rate",
                value=pe.qbi_business_property_rate(),
                unit="rate"
            ),
        ],
        steps=[
            ComputationStep(
                id="step_b2_1",
                description="Calculate wage-only cap",
                formula="wage_cap = 50% × W2_wages",
                formula_latex=r"\text{Wage Cap} = 0.50 \times W_2",
                inputs=["w2_wages_from_qualified_business"],
                output="wage_cap"
            ),
            ComputationStep(
                id="step_b2_2",
                description="Calculate alternative (wage + property) cap",
                formula="alt_cap = 25% × W2_wages + 2.5% × property_basis",
                formula_latex=r"\text{Alt Cap} = 0.25 \times W_2 + 0.025 \times UBIA",
                inputs=["w2_wages_from_qualified_business", "unadjusted_basis_qualified_property"],
                output="alt_cap"
            ),
            ComputationStep(
                id="step_b2_3",
                description="Take the greater of the two caps",
                formula="full_cap = MAX(wage_cap, alt_cap)",
                formula_latex=r"\text{Cap} = \max(\text{Wage Cap}, \text{Alt Cap})",
                inputs=["wage_cap", "alt_cap"],
                output="full_cap"
            ),
        ],
        variables_used=["qbid_amount", "w2_wages_from_qualified_business", "unadjusted_basis_qualified_property"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qbid_amount.py",
    )


def _build_section_b3_phaseout(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(b)(3) - Phase-in of limitation."""
    return LawSection(
        id="sec_b3_phaseout",
        section_number="199A(b)(3)",
        title="Phase-In of Wage/Property Limitation",
        description=(
            "The W-2 wage limitation phases in above the threshold over a fixed range. "
            "Below threshold: no limitation. In phase-in range: partial limitation. "
            "Above phase-in: full limitation. "
            f"Range: ${int(pe.qbi_phase_out_length('SINGLE', 2025)):,} single / "
            f"${int(pe.qbi_phase_out_length('JOINT', 2025)):,} joint pre-2026; "
            f"expanded to ${int(pe.qbi_phase_out_length('SINGLE', 2026)):,} / "
            f"${int(pe.qbi_phase_out_length('JOINT', 2026)):,} starting 2026 under the One Big Beautiful Bill Act."
        ),
        legal_reference=LegalReference(
            section="199A(b)(3)",
            title="Modifications to limitation based on W-2 wages",
            url=f"{CORNELL_BASE}#b_3",
            text="In the case of any taxpayer whose taxable income for the taxable year exceeds the threshold amount... the deductible amount shall be reduced by the amount which bears the same ratio to the excess of [20% QBI over the wage cap] as such excess taxable income bears to $50,000 ($100,000 in the case of a joint return)."
        ),
        status=ImplementationStatus.COMPLETE,
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label=f"Phase-out Start (Single, {pe.DEFAULT_YEAR})",
                value=pe.qbi_threshold("SINGLE"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="SINGLE"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label=f"Phase-out Start (Joint, {pe.DEFAULT_YEAR})",
                value=pe.qbi_threshold("JOINT"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="JOINT"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.length",
                label=f"Phase-out Range (Single, {pe.DEFAULT_YEAR})",
                value=pe.qbi_phase_out_length("SINGLE"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="SINGLE"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.length",
                label=f"Phase-out Range (Joint, {pe.DEFAULT_YEAR})",
                value=pe.qbi_phase_out_length("JOINT"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="JOINT"
            ),
        ],
        steps=[
            ComputationStep(
                id="step_b3_1",
                description="Calculate reduction rate based on income in phase-out range (Worksheet 12-A line 24; Schedule A line 9)",
                formula="reduction_rate = MIN(1, MAX(0, taxable_income - threshold) / phase_out_length)",
                formula_latex=r"\text{Reduction Rate} = \min\left(1, \frac{\max(0, \text{Income} - \text{Threshold})}{\text{Phase-out Length}}\right)",
                inputs=["taxable_income_less_qbid", "threshold", "phase_out_length"],
                output="reduction_rate"
            ),
            ComputationStep(
                id="step_b3_2",
                description="Calculate reduction amount = reduction_rate × MAX(0, 20% × QBI − wage/UBIA cap)",
                formula="reduction = reduction_rate × MAX(0, qbid_max − full_cap)",
                inputs=["reduction_rate", "qbid_max", "full_cap"],
                output="reduction"
            ),
            ComputationStep(
                id="step_b3_3",
                description="Phased QBID is the larger of the capped amount or the reduced amount",
                formula="phased_qbid = MAX(MIN(qbid_max, full_cap), qbid_max − reduction)",
                inputs=["qbid_max", "full_cap", "reduction"],
                output="phased_qbid"
            ),
        ],
        variables_used=["qbid_amount", "taxable_income_less_qbid", "filing_status"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qbid_amount.py",
    )


def _build_section_c_qbi_definition(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(c) - Qualified business income definition."""
    return LawSection(
        id="sec_c_qbi_definition",
        section_number="199A(c)",
        title="Qualified Business Income Definition",
        description="QBI is the net amount of qualified items of income, gain, deduction, and loss from a qualified trade or business. It's reduced by deductible portions of SE tax, health insurance, and retirement contributions.",
        legal_reference=LegalReference(
            section="199A(c)",
            title="Qualified business income",
            url=f"{CORNELL_BASE}#c",
            text="The term 'qualified business income' means... the net amount of qualified items of income, gain, deduction, and loss with respect to any qualified trade or business of the taxpayer."
        ),
        status=ImplementationStatus.COMPLETE,
        inputs=[
            InputVariable(
                name="self_employment_income",
                label="Self-Employment Income",
                unit="USD"
            ),
            InputVariable(
                name="partnership_s_corp_income",
                label="Partnership/S-Corp Income",
                unit="USD"
            ),
            InputVariable(
                name="rental_income",
                label="Rental Income",
                unit="USD"
            ),
            InputVariable(
                name="farm_operations_income",
                label="Farm Operations Income",
                unit="USD"
            ),
            InputVariable(
                name="farm_rent_income",
                label="Farm Rent Income",
                unit="USD"
            ),
            InputVariable(
                name="estate_income",
                label="Estate/Trust Income",
                unit="USD"
            ),
        ],
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.income_definition",
                label="QBI Income Sources",
                value=["self_employment_income", "partnership_s_corp_income", "rental_income", "farm_operations_income", "farm_rent_income", "estate_income"],
                unit="list"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.deduction_definition",
                label="QBI Deductions",
                value=["self_employment_tax_ald_person", "self_employed_health_insurance_ald_person", "self_employed_pension_contribution_ald_person"],
                unit="list"
            ),
        ],
        steps=[
            ComputationStep(
                id="step_c1",
                description="Sum qualified income from each source (only if marked as qualified)",
                formula="gross_qbi = Σ(income × would_be_qualified)",
                inputs=["self_employment_income", "partnership_s_corp_income", "rental_income"],
                output="gross_qbi"
            ),
            ComputationStep(
                id="step_c2",
                description="Sum QBI-related deductions",
                formula="qbi_deductions = SE_tax_ded + health_ins_ded + pension_ded",
                inputs=["self_employment_tax_ald_person", "self_employed_health_insurance_ald_person", "self_employed_pension_contribution_ald_person"],
                output="qbi_deductions"
            ),
            ComputationStep(
                id="step_c3",
                description="Calculate net QBI",
                formula="qualified_business_income = MAX(0, gross_qbi - qbi_deductions)",
                inputs=["gross_qbi", "qbi_deductions"],
                output="qualified_business_income"
            ),
        ],
        variables_used=["qualified_business_income"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qualified_business_income.py",
    )


def _build_section_c2_loss_carryover(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(c)(2) - Loss carryforward."""
    return LawSection(
        id="sec_c2_loss_carryover",
        section_number="199A(c)(2)",
        title="QBI Loss Carryforward",
        description="If net QBI is negative in a year, the loss carries forward to reduce QBI in the next year. This prevents claiming deductions on income offset by prior losses.",
        legal_reference=LegalReference(
            section="199A(c)(2)",
            title="Carryover of losses",
            url=f"{CORNELL_BASE}#c_2",
            text="If the net amount of qualified income, gain, deduction, and loss with respect to qualified trades or businesses of the taxpayer for any taxable year is less than zero, such amount shall be treated as a loss from a qualified trade or business in the succeeding taxable year."
        ),
        status=ImplementationStatus.MISSING,
        status_notes="Loss carryforward is NOT implemented. Negative QBI is zeroed out instead of carried to next year.",
        steps=[
            ComputationStep(
                id="step_c2_1",
                description="Check if QBI is negative",
                formula="if net_qbi < 0: carry_to_next_year = net_qbi",
                code_reference="⚠️ NOT IMPLEMENTED - current code uses MAX(0, qbi)"
            ),
            ComputationStep(
                id="step_c2_2",
                description="Apply prior year losses",
                formula="adjusted_qbi = current_qbi + prior_year_qbi_loss",
                code_reference="⚠️ NOT IMPLEMENTED"
            ),
        ],
        variables_used=["qualified_business_income"],
    )


def _build_section_c3_exclusions(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(c)(3)(B) - Items not included in QBI."""
    return LawSection(
        id="sec_c3_exclusions",
        section_number="199A(c)(3)(B), (c)(4)",
        title="Items Excluded from QBI",
        description="Certain items are excluded from QBI. §199A(c)(3)(B) excludes investment-type income (capital gains/losses, dividends, interest, foreign currency gains/losses, certain commodities transactions, annuity income). §199A(c)(4) separately excludes reasonable compensation paid to the taxpayer and guaranteed payments to partners.",
        legal_reference=LegalReference(
            section="199A(c)(3)(B), (c)(4)",
            title="Items not included; reasonable compensation and guaranteed payments",
            url=f"{CORNELL_BASE}#c_3_B",
            text="(c)(3)(B): The following items shall not be taken into account as a qualified item of income, gain, deduction, or loss: (i) short- or long-term capital gain or loss, (ii) dividend income, (iii) interest income (other than properly allocable to a trade or business), (iv) foreign currency gains/losses, (v) certain net gains from notional principal contracts and commodities, (vi) annuity income (other than business-related), and (vii) any item of deduction or loss properly allocable to such amounts. (c)(4): Qualified business income shall not include— (A) reasonable compensation paid to the taxpayer by any qualified trade or business of the taxpayer for services rendered, (B) any guaranteed payment described in section 707(c) for services rendered, or (C) to the extent provided in regulations, any payment described in section 707(a) to a partner for services rendered."
        ),
        status=ImplementationStatus.PARTIAL,
        status_notes="The model assumes inputs are already properly adjusted. No explicit validation of exclusions.",
        steps=[
            ComputationStep(
                id="step_c3_1",
                description="Exclude capital gains/losses",
                code_reference="Implicit - separate capital gains variables"
            ),
            ComputationStep(
                id="step_c3_2",
                description="Exclude dividends",
                code_reference="Implicit - dividend income tracked separately"
            ),
            ComputationStep(
                id="step_c3_3",
                description="Exclude reasonable compensation",
                code_reference="⚠️ Relies on correct K-1 input classification"
            ),
        ],
        variables_used=[],
    )


def _build_section_d_qualified_business(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(d)(1) - Qualified trade or business."""
    return LawSection(
        id="sec_d_qualified_business",
        section_number="199A(d)(1)",
        title="Qualified Trade or Business Definition",
        description="A qualified trade or business is any section 162 trade or business EXCEPT: (A) specified service trades (SSTBs), and (B) performing services as an employee.",
        legal_reference=LegalReference(
            section="199A(d)(1)",
            title="Qualified trade or business",
            url=f"{CORNELL_BASE}#d_1",
            text="The term 'qualified trade or business' means any trade or business other than— (A) a specified service trade or business, or (B) the trade or business of performing services as an employee."
        ),
        status=ImplementationStatus.COMPLETE,
        status_notes="Implemented via boolean input flags for each income source",
        inputs=[
            InputVariable(
                name="self_employment_income_would_be_qualified",
                label="SE Income is Qualified",
                description="Whether self-employment income is from a qualified business"
            ),
            InputVariable(
                name="rental_income_would_be_qualified",
                label="Rental Income is Qualified",
                description="Whether rental activity qualifies as a trade/business"
            ),
        ],
        variables_used=["business_is_qualified"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/self_employment/business_is_qualified.py",
    )


def _build_section_d2_sstb(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(d)(2) - Specified service trade or business."""
    return LawSection(
        id="sec_d2_sstb",
        section_number="199A(d)(2), (d)(3)",
        title="Specified Service Trade or Business (SSTB)",
        description="SSTBs include health, law, accounting, actuarial science, performing arts, consulting, athletics, financial services, brokerage, and any business where principal asset is reputation/skill. Engineering and architecture, which are SSTBs under §1202(e)(3)(A), are explicitly carved out by §199A(d)(2)(A). Per §199A(d)(3), SSTBs phase out the deduction proportionally above the threshold and receive no deduction above threshold + phase-out range.",
        legal_reference=LegalReference(
            section="199A(d)(2), (d)(3)",
            title="Specified service trade or business; applicable percentage",
            url=f"{CORNELL_BASE}#d_2",
            text="The term 'specified service trade or business' means any trade or business— (A) which is described in section 1202(e)(3)(A) (applied without regard to the words 'engineering, architecture'), or (B) which involves the performance of services that consist of investing and investment management, trading, or dealing in securities... §199A(d)(3) provides that for taxpayers in the phase-in range, the SSTB deduction is reduced by an 'applicable percentage' equal to 1 minus the phase-in fraction; above the range, no SSTB deduction is allowed."
        ),
        status=ImplementationStatus.COMPLETE,
        inputs=[
            InputVariable(
                name="business_is_sstb",
                label="Is SSTB",
                description="Whether the business is a specified service trade or business"
            ),
        ],
        steps=[
            ComputationStep(
                id="step_d2_1",
                description="Calculate applicable percentage (phases out for SSTBs)",
                formula="applicable_rate = 1 - reduction_rate",
                inputs=["reduction_rate"],
                output="applicable_rate"
            ),
            ComputationStep(
                id="step_d2_2",
                description="Apply SSTB multiplier to QBI and caps",
                formula="sstb_multiplier = is_sstb ? applicable_rate : 1",
                inputs=["is_sstb", "applicable_rate"],
                output="sstb_multiplier"
            ),
            ComputationStep(
                id="step_d2_3",
                description="Adjust QBID max for SSTB",
                formula="adj_qbid_max = qbid_max × sstb_multiplier",
                inputs=["qbid_max", "sstb_multiplier"],
                output="adj_qbid_max"
            ),
        ],
        variables_used=["business_is_sstb", "qbid_amount"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/self_employment/business_is_sstb.py",
    )


def _build_section_e_thresholds(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(e) - Threshold amounts."""
    return LawSection(
        id="sec_e_thresholds",
        section_number="199A(e)",
        title="Threshold Amounts",
        description="The statutory base threshold is $157,500 (single) / $315,000 (joint), adjusted annually for inflation since 2018. Current values determine when the W-2 wage/UBIA limitation phases in and when the SSTB applicable percentage reduction applies.",
        legal_reference=LegalReference(
            section="199A(e)",
            title="Other definitions",
            url=f"{CORNELL_BASE}#e",
            text="The term 'threshold amount' means— (A) except as provided in subparagraph (B), $157,500 (200 percent of such amount in the case of a joint return)... adjusted for inflation after 2018."
        ),
        status=ImplementationStatus.COMPLETE,
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label=f"{pe.DEFAULT_YEAR} Threshold (Single/HoH)",
                value=pe.qbi_threshold("SINGLE"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="SINGLE"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label=f"{pe.DEFAULT_YEAR} Threshold (Joint)",
                value=pe.qbi_threshold("JOINT"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="JOINT"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label=f"{pe.DEFAULT_YEAR} Threshold (MFS)",
                value=pe.qbi_threshold("SEPARATE"),
                unit="USD",
                year=pe.DEFAULT_YEAR,
                filing_status="SEPARATE"
            ),
        ],
        variables_used=["filing_status", "taxable_income_less_qbid"],
        github_url=f"{GITHUB_BASE}/policyengine_us/parameters/gov/irs/deductions/qbi/phase_out/start.yaml",
    )


def _build_section_i_minimum_deduction(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(i) - Minimum deduction (new provision)."""
    return LawSection(
        id="sec_i_minimum",
        section_number="199A(i)",
        title="Minimum Deduction Floor",
        description="Starting in 2026, taxpayers with at least $1,000 of QBI receive a minimum deduction of $400, regardless of other limitations.",
        legal_reference=LegalReference(
            section="199A(i)",
            title="Minimum deduction",
            url=f"{CORNELL_BASE}#i",
            text="In the case of an applicable taxpayer for any taxable year, the deduction allowed under subsection (a) for the taxable year shall be equal to the greater of— (A) the amount otherwise determined under subsection (a), or (B) $400. An 'applicable taxpayer' is one with at least $1,000 of aggregate qualified business income from qualified trades or businesses in which the taxpayer materially participates."
        ),
        status=ImplementationStatus.COMPLETE,
        status_notes="Effective starting 2026 per One Big Beautiful Bill Act",
        parameters=[
            Parameter(
                name="gov.irs.deductions.qbi.deduction_floor.in_effect",
                label="Floor In Effect",
                value=True,
                year=2026
            ),
            Parameter(
                name="gov.irs.deductions.qbi.deduction_floor.amount",
                label="Minimum Deduction",
                value=400,
                unit="USD",
                year=2026
            ),
        ],
        steps=[
            ComputationStep(
                id="step_i1",
                description="Determine the floor amount based on aggregate QBI (per single_amount bracket)",
                formula="floor = 400 if (non_sstb_qbi + sstb_qbi) ≥ 1,000 else 0",
                inputs=["qualified_business_income", "sstb_qualified_business_income"],
                output="floor"
            ),
            ComputationStep(
                id="step_i2",
                description="Take the greater of the pre-floor QBID and the floor",
                formula="final_qbid = MAX(pre_floor_qbid, floor)",
                inputs=["pre_floor_qbid", "floor"],
                output="qualified_business_income_deduction"
            ),
        ],
        variables_used=["qualified_business_income_deduction"],
        github_url=f"{GITHUB_BASE}/policyengine_us/parameters/gov/irs/deductions/qbi/deduction_floor/",
    )


def _build_section_g_cooperatives(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(g) - Agricultural cooperatives."""
    return LawSection(
        id="sec_g_cooperatives",
        section_number="199A(g)",
        title="Agricultural/Horticultural Cooperatives",
        description="Qualified agricultural or horticultural cooperatives may claim a separate deduction equal to 9% of qualified production activities income.",
        legal_reference=LegalReference(
            section="199A(g)",
            title="Deduction for income attributable to domestic production activities of specified agricultural or horticultural cooperatives",
            url=f"{CORNELL_BASE}#g",
            text="In the case of a taxpayer which is a specified agricultural or horticultural cooperative, there shall be allowed as a deduction an amount equal to 9 percent of the lesser of— (A) the qualified production activities income of the taxpayer for the taxable year, or (B) the taxable income of the taxpayer for the taxable year (determined without regard to this section)..."
        ),
        status=ImplementationStatus.MISSING,
        status_notes="Cooperative provisions are NOT implemented in PolicyEngine",
        variables_used=[],
    )


def _build_adjacent_sections() -> List[AdjacentSection]:
    """Build the list of adjacent IRC sections that interact with §199A."""

    return [
        # Section 1202 - SSTB Definition
        AdjacentSection(
            id="sec_1202",
            section_number="§1202(e)(3)(A)",
            title="Specified Service Trade or Business Definition",
            description="Defines the categories of 'specified service trades or businesses' (SSTBs) that face deduction limitations under §199A.",
            relevance_to_qbid="§199A(d)(2) incorporates this definition to identify SSTBs whose owners cannot claim QBID above the income threshold. Note: engineering and architecture, which §1202(e)(3)(A) lists, are explicitly carved out of the §199A SSTB definition.",
            legal_reference=LegalReference(
                section="1202(e)(3)(A)",
                title="Qualified small business stock - Excluded businesses",
                url="https://www.law.cornell.edu/uscode/text/26/1202#e_3_A",
                text="The term 'qualified trade or business' shall not include any trade or business involving the performance of services in the fields of health, law, engineering, architecture, accounting, actuarial science, performing arts, consulting, athletics, financial services, brokerage services..."
            ),
            status=ImplementationStatus.COMPLETE,
            status_notes="PolicyEngine fully implements SSTB handling. The applicable-percentage phase-out (1 - reduction_rate) is applied to the SSTB-only QBI bucket, while non-SSTB QBI is computed in parallel without the phase-out.",
            key_provisions=[
                "§199A SSTB list (subset of §1202(e)(3)(A)):",
                "Health, law, accounting, actuarial science",
                "Performing arts, consulting, athletics",
                "Financial services, brokerage services",
                "Investing/investment management, trading, dealing in securities",
                "Any business where principal asset is reputation/skill of employees",
                "§199A excludes engineering and architecture (§199A(d)(2)(A))",
            ],
            variables_used=["business_is_sstb"],
            github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/self_employment/business_is_sstb.py",
            referenced_by=["199A(d)(2)"]
        ),

        # Section 469 - Passive Activity Rules
        AdjacentSection(
            id="sec_469",
            section_number="§469",
            title="Passive Activity Losses and Credits",
            description="Establishes rules for passive vs. active business participation. Rental activities are generally passive unless the taxpayer materially participates.",
            relevance_to_qbid="Determines whether rental income qualifies as QBI. Rental activities must rise to the level of a 'trade or business' (typically 250+ hours/year) to qualify.",
            legal_reference=LegalReference(
                section="469",
                title="Passive activity losses and credits limited",
                url="https://www.law.cornell.edu/uscode/text/26/469",
                text="The passive activity loss and the passive activity credit for any taxable year shall be disallowed... A passive activity is any activity which involves the conduct of any trade or business in which the taxpayer does not materially participate."
            ),
            status=ImplementationStatus.PARTIAL,
            status_notes="PolicyEngine provides rental_income_would_be_qualified flag for user to indicate qualification. Material participation tests and 250-hour safe harbor are NOT automatically calculated.",
            key_provisions=[
                "Material participation requires regular, continuous, and substantial involvement",
                "Seven tests for material participation (500+ hours, substantially all participation, etc.)",
                "Rental activities presumed passive with real estate professional exception",
                "Safe harbor: 250+ hours of rental services qualifies rental as trade/business for QBID",
                "$25,000 allowance for active participation in rental real estate"
            ],
            variables_used=["rental_income_would_be_qualified"],
            referenced_by=["199A(c)", "199A(d)(1)"]
        ),

        # Section 857 - REIT Dividends
        AdjacentSection(
            id="sec_857",
            section_number="§857(b)(3)",
            title="Real Estate Investment Trust (REIT) Taxation",
            description="Defines qualified REIT dividends, which receive a 20% QBID without the W-2 wage and property limitations.",
            relevance_to_qbid="§199A(b)(1)(B) provides that 20% of qualified REIT dividends is added to the combined QBI amount, without wage/property limitations.",
            legal_reference=LegalReference(
                section="857(b)(3)",
                title="REIT capital gain dividends",
                url="https://www.law.cornell.edu/uscode/text/26/857#b_3",
                text="For purposes of this title, a capital gain dividend is any dividend, or part thereof, which is designated by the real estate investment trust as a capital gain dividend..."
            ),
            status=ImplementationStatus.COMPLETE,
            status_notes="PolicyEngine implements REIT/PTP component in qbid_amount.py: 20% × qualified_reit_and_ptp_income is added to the per-person QBID without wage or UBIA limits. Loss carryforward (Form 8995 line 7) is not separately tracked.",
            key_provisions=[
                "Qualified REIT dividends = ordinary REIT dividends (not capital gain dividends)",
                "20% deduction applies without W-2 wage limitation",
                "20% deduction applies without property basis limitation",
                "Subject only to taxable income cap",
                "Reported on Form 1099-DIV Box 5"
            ],
            variables_used=["qualified_reit_and_ptp_income"],
            github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/dividends/qualified_reit_and_ptp_income.py",
            referenced_by=["199A(b)(1)(B)", "199A(e)(3)"]
        ),

        # Section 7704 - Publicly Traded Partnerships
        AdjacentSection(
            id="sec_7704",
            section_number="§7704",
            title="Publicly Traded Partnerships (PTPs)",
            description="Defines publicly traded partnerships. Qualified PTP income receives a 20% QBID similar to REIT dividends.",
            relevance_to_qbid="§199A(b)(1)(B) provides that 20% of qualified PTP income is added to combined QBI amount, without wage/property limitations.",
            legal_reference=LegalReference(
                section="7704",
                title="Certain publicly traded partnerships treated as corporations",
                url="https://www.law.cornell.edu/uscode/text/26/7704",
                text="A publicly traded partnership shall be treated as a corporation... interests in such partnership are traded on an established securities market, or are readily tradable on a secondary market."
            ),
            status=ImplementationStatus.COMPLETE,
            status_notes="PolicyEngine combines REIT and PTP income into a single variable (qualified_reit_and_ptp_income). qbid_amount.py applies the 20% rate (gov.irs.deductions.qbi.max.reit_ptp_rate) to this combined input and adds it to the final per-person QBID. Loss carryforward (Form 8995 line 7) is not separately tracked.",
            key_provisions=[
                "PTP = partnership traded on established securities market",
                "Qualified PTP income = ordinary income from PTP (not SSTB)",
                "20% deduction without W-2 wage limitation",
                "20% deduction without property basis limitation",
                "PTP losses reduce PTP income component (not QBI from other businesses)",
                "Reported on Schedule K-1"
            ],
            variables_used=["qualified_reit_and_ptp_income"],
            referenced_by=["199A(b)(1)(B)", "199A(e)(4)"]
        ),

        # Section 1(h) - Capital Gains
        AdjacentSection(
            id="sec_1_h",
            section_number="§1(h)",
            title="Net Capital Gain Definition",
            description="Defines 'net capital gain' used in the taxable income cap calculation for QBID.",
            relevance_to_qbid="§199A(a) limits QBID to 20% of taxable income MINUS net capital gain. This ensures QBID doesn't benefit already-preferentially-taxed income.",
            legal_reference=LegalReference(
                section="1(h)",
                title="Maximum capital gains rate",
                url="https://www.law.cornell.edu/uscode/text/26/1#h",
                text="Net capital gain means the excess of net long-term capital gain for the taxable year over the net short-term capital loss for such year."
            ),
            status=ImplementationStatus.COMPLETE,
            status_notes="Implemented via 'adjusted_net_capital_gain' variable.",
            key_provisions=[
                "Net capital gain = long-term gains minus short-term losses",
                "Includes qualified dividends for rate purposes",
                "Excluded from the taxable income base for QBID cap calculation"
            ],
            variables_used=["adjusted_net_capital_gain", "long_term_capital_gains", "short_term_capital_gains"],
            github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/adjusted_net_capital_gain.py",
            referenced_by=["199A(a)"]
        ),

        # Section 162 - Trade or Business
        AdjacentSection(
            id="sec_162",
            section_number="§162",
            title="Trade or Business Expenses",
            description="Defines what constitutes a 'trade or business' - the foundational requirement for QBI eligibility.",
            relevance_to_qbid="§199A(d)(1) requires income be from a 'section 162 trade or business' to qualify. Investment activities and hobbies do not qualify.",
            legal_reference=LegalReference(
                section="162",
                title="Trade or business expenses",
                url="https://www.law.cornell.edu/uscode/text/26/162",
                text="There shall be allowed as a deduction all the ordinary and necessary expenses paid or incurred during the taxable year in carrying on any trade or business..."
            ),
            status=ImplementationStatus.PARTIAL,
            status_notes="Implicit in income source categorization. No explicit validation that activity constitutes a trade or business.",
            key_provisions=[
                "Activity must be entered into for profit",
                "Activity must be regular and continuous",
                "Mere investment activities do not qualify",
                "Hobby activities do not qualify (see §183)",
                "Employee services are excluded from QBID (§199A(d)(1)(B))"
            ],
            variables_used=["self_employment_income", "business_is_qualified"],
            referenced_by=["199A(d)(1)"]
        ),

        # Section 707 - Partnership Payments
        AdjacentSection(
            id="sec_707",
            section_number="§707(c)",
            title="Partnership Transactions with Partners",
            description="Defines guaranteed payments and payments for services to partners, which are EXCLUDED from QBI.",
            relevance_to_qbid="§199A(c)(4) excludes reasonable compensation and guaranteed payments from QBI to prevent double-dipping.",
            legal_reference=LegalReference(
                section="707",
                title="Transactions between partner and partnership",
                url="https://www.law.cornell.edu/uscode/text/26/707",
                text="Guaranteed payments... to a partner for services or for the use of capital shall be considered as made to one who is not a member of the partnership..."
            ),
            status=ImplementationStatus.PARTIAL,
            status_notes="PolicyEngine relies on input data being properly classified. No explicit handling of guaranteed payments.",
            key_provisions=[
                "Guaranteed payments for services excluded from QBI",
                "Guaranteed payments for use of capital excluded from QBI",
                "Reasonable compensation to S-corp shareholders excluded",
                "Prevents claiming QBID on what is essentially wages"
            ],
            variables_used=["partnership_s_corp_income"],
            referenced_by=["199A(c)(4)"]
        ),

        # Section 167/168 - Depreciation (UBIA)
        AdjacentSection(
            id="sec_167_168",
            section_number="§167/168",
            title="Depreciation and UBIA",
            description="Defines depreciation methods and recovery periods used to calculate the unadjusted basis immediately after acquisition (UBIA) of qualified property.",
            relevance_to_qbid="§199A(b)(2)(B)(ii) allows an alternative wage limitation based on 25% of W-2 wages PLUS 2.5% of UBIA of qualified property.",
            legal_reference=LegalReference(
                section="167/168",
                title="Depreciation / ACRS",
                url="https://www.law.cornell.edu/uscode/text/26/168",
                text="Property is qualified property if... such property is tangible property subject to depreciation under section 167..."
            ),
            status=ImplementationStatus.PARTIAL,
            status_notes="Variable 'unadjusted_basis_qualified_property' exists but is USER INPUT ONLY - no formula. Does not automatically calculate UBIA from depreciation schedules or validate property is still within depreciable period.",
            key_provisions=[
                "UBIA = cost basis at time of acquisition (before depreciation)",
                "Qualified property must be depreciable tangible property",
                "Property must be used in the trade or business",
                "Property must be within its depreciable period",
                "Depreciable period ends on later of: 10 years or last day of full depreciation"
            ],
            variables_used=["unadjusted_basis_qualified_property"],
            github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/self_employment/unadjusted_basis_qualified_property.py",
            referenced_by=["199A(b)(2)(B)(ii)", "199A(b)(6)"]
        ),

        # Section 52 - Aggregation Rules
        AdjacentSection(
            id="sec_52",
            section_number="§52(a)(b)",
            title="Controlled Group Aggregation",
            description="Rules for aggregating commonly controlled businesses for purposes of wage limitations.",
            relevance_to_qbid="§199A(b)(4) references these rules for determining W-2 wages across related entities. Taxpayers may also elect to aggregate businesses under Treas. Reg. § 1.199A-4.",
            legal_reference=LegalReference(
                section="52",
                title="Controlled groups",
                url="https://www.law.cornell.edu/uscode/text/26/52",
                text="For purposes of this subpart, all employees of all corporations which are members of the same controlled group of corporations shall be treated as employed by a single employer."
            ),
            status=ImplementationStatus.MISSING,
            status_notes="The aggregation election (Treas. Reg. § 1.199A-4) is NOT implemented. Each business is treated independently. Users cannot elect to combine multiple qualifying businesses to share W-2 wages.",
            key_provisions=[
                "Controlled groups share wage limitation calculations",
                "Taxpayers may ELECT to aggregate qualifying businesses",
                "Aggregated businesses share one set of thresholds",
                "Can benefit taxpayers with multiple businesses (some with high wages, some without)",
                "Election is irrevocable without IRS consent"
            ],
            variables_used=[],
            referenced_by=["199A(b)(4)", "Treas. Reg. § 1.199A-4"]
        ),

        # Section 6051(a) - W-2 Wage Definition
        AdjacentSection(
            id="sec_6051",
            section_number="§6051(a)",
            title="W-2 Wage Reporting Requirements",
            description="Defines what constitutes W-2 wages for purposes of the wage limitation calculation.",
            relevance_to_qbid="§199A(b)(4)(A) references this section to define W-2 wages. Only wages properly reported on Form W-2 count toward the wage limitation.",
            legal_reference=LegalReference(
                section="6051(a)",
                title="Receipts for employees",
                url="https://www.law.cornell.edu/uscode/text/26/6051#a",
                text="Every person required to deduct and withhold from an employee... shall furnish to each such employee... a written statement showing... the total amount of wages as defined in section 3401(a)..."
            ),
            status=ImplementationStatus.PARTIAL,
            status_notes="Variable 'w2_wages_from_qualified_business' exists but is USER INPUT ONLY - no formula. Does not automatically derive from W-2 forms or validate proper reporting. The 50% wage cap and 25%+2.5% alternative cap ARE correctly implemented once the value is provided.",
            key_provisions=[
                "W-2 wages must be properly reported to count for limitation",
                "Includes wages, tips, and other compensation",
                "Must be reported by filing deadline (including extensions)",
                "Elective deferrals to retirement plans are included",
                "Deferred compensation generally excluded until includable in income"
            ],
            variables_used=["w2_wages_from_qualified_business"],
            github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/self_employment/w2_wages_from_qualified_business.py",
            referenced_by=["199A(b)(4)(A)"]
        ),

        # Section 1382/1385 - Cooperative Provisions
        AdjacentSection(
            id="sec_1382_1385",
            section_number="§1382/1385",
            title="Agricultural Cooperative Provisions",
            description="Special rules for patronage dividends and cooperative income that interact with the QBID deduction.",
            relevance_to_qbid="§199A(g) provides special rules for agricultural cooperatives. Patrons may receive Form 1099-PATR showing their share of the cooperative's QBID.",
            legal_reference=LegalReference(
                section="1382/1385",
                title="Cooperative patronage dividends",
                url="https://www.law.cornell.edu/uscode/text/26/1382",
                text="In determining the taxable income of a cooperative organization... there shall not be taken into account amounts paid during the payment period as patronage dividends..."
            ),
            status=ImplementationStatus.MISSING,
            status_notes="Cooperative provisions under §199A(g) are not implemented.",
            key_provisions=[
                "Patron's deduction based on QBI from cooperative",
                "Cooperative can pass through QBID to patrons",
                "Patron limited to 20% of qualified payments received",
                "Alternative: patron can take lesser of 9% of QBI or 50% of W-2 wages",
                "Form 1099-PATR reports cooperative distributions"
            ],
            variables_used=[],
            referenced_by=["199A(g)(1)(C)", "199A(g)(2)"]
        ),

        # Section 475 - Securities/Commodities Dealers
        AdjacentSection(
            id="sec_475",
            section_number="§475(c)(2), (e)(2)",
            title="Securities and Commodities Definitions",
            description="Defines securities and commodities for SSTB determination in financial services.",
            relevance_to_qbid="§199A(d)(2)(B) references these sections to clarify what constitutes 'financial services' and 'brokerage services' for SSTB classification.",
            legal_reference=LegalReference(
                section="475(c)(2)",
                title="Securities definition",
                url="https://www.law.cornell.edu/uscode/text/26/475#c_2",
                text="The term 'security' means any stock, partnership or beneficial ownership interest in partnership or trust, note, bond, debenture, debt instrument, or derivative..."
            ),
            status=ImplementationStatus.PARTIAL,
            status_notes="PolicyEngine uses boolean SSTB flag without detailed financial services classification.",
            key_provisions=[
                "Securities include stocks, bonds, notes, derivatives",
                "Commodities include physical commodities and commodity derivatives",
                "Trading in securities/commodities is an SSTB",
                "Dealers and traders in securities face SSTB treatment",
                "Exception for certain hedging transactions"
            ],
            variables_used=["business_is_sstb"],
            referenced_by=["199A(d)(2)(B)"]
        ),

        # Section 1(f)(3) - Inflation Adjustment
        AdjacentSection(
            id="sec_1_f",
            section_number="§1(f)(3)",
            title="Cost-of-Living Adjustment",
            description="Provides the methodology for inflation-adjusting the QBID threshold amounts.",
            relevance_to_qbid="§199A(e)(2)(B) requires threshold amounts to be adjusted for inflation using the methodology in §1(f)(3), with 2017 as the base year.",
            legal_reference=LegalReference(
                section="1(f)(3)",
                title="Cost-of-living adjustment",
                url="https://www.law.cornell.edu/uscode/text/26/1#f_3",
                text="The cost-of-living adjustment for any calendar year is the percentage by which the CPI for the preceding calendar year exceeds the CPI for the calendar year 2016..."
            ),
            status=ImplementationStatus.COMPLETE,
            status_notes="PolicyEngine parameters are inflation-adjusted with updated thresholds by year.",
            key_provisions=[
                "Uses Chained CPI-U for adjustments",
                "Base year for QBID thresholds is 2017 (per §199A(e)(2)(B))",
                "Rounded down to nearest $25 (or $25 for MFS)",
                "Thresholds updated annually via PolicyEngine YAML"
            ],
            variables_used=[],
            referenced_by=["199A(e)(2)(B)"]
        ),
    ]
