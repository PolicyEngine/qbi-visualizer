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
    DecisionPoint,
    CalculatorInput,
    CalculatorResult,
    CalculatorStep,
    AdjacentSection,
)


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
        computation_order=[
            "sec_c_qbi_definition",
            "sec_c2_loss_carryover",
            "sec_b2_wage_limitation",
            "sec_b3_phaseout",
            "sec_d2_sstb",
            "sec_b1_combined_qbi",
            "sec_a_allowance",
            "sec_i_minimum",
        ],
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
            text="In the case of a taxpayer other than a corporation, there shall be allowed as a deduction... an amount equal to the lesser of— (A) the combined qualified business income amount, or (B) an amount equal to 20 percent of the excess (if any) of— (i) the taxable income of the taxpayer for the taxable year, over (ii) the net capital gain..."
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
                value=0.20,
                unit="rate"
            )
        ],
        steps=[
            ComputationStep(
                id="step_a1",
                description="Calculate taxable income cap",
                formula="taxable_income_cap = 20% × (taxable_income - capital_gains)",
                formula_latex=r"\text{Cap} = 0.20 \times (\text{Taxable Income} - \text{Net Capital Gains})",
                inputs=["taxable_income_less_qbid", "adjusted_net_capital_gain"],
                output="taxable_income_cap"
            ),
            ComputationStep(
                id="step_a2",
                description="Apply the taxable income cap",
                formula="final_qbid = MIN(combined_qbid, taxable_income_cap)",
                formula_latex=r"\text{QBID} = \min(\text{Combined QBID}, \text{Cap})",
                inputs=["combined_qbid", "taxable_income_cap"],
                output="qualified_business_income_deduction"
            ),
        ],
        variables_used=["qualified_business_income_deduction", "taxable_income_less_qbid", "adjusted_net_capital_gain"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qualified_business_income_deduction.py",
        next_sections=[],
        depends_on=["sec_b1_combined_qbi"],
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
        status=ImplementationStatus.PARTIAL,
        status_notes="REIT dividends and PTP income component (B) is NOT implemented",
        inputs=[
            InputVariable(
                name="qbid_amount",
                label="Per-Business QBID Amount",
                description="QBID for each qualified trade/business after limitations",
                unit="USD"
            ),
            InputVariable(
                name="reit_dividends",
                label="Qualified REIT Dividends",
                description="NOT IMPLEMENTED",
                unit="USD"
            ),
            InputVariable(
                name="ptp_income",
                label="Qualified PTP Income",
                description="NOT IMPLEMENTED",
                unit="USD"
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
                description="Add 20% of REIT/PTP income (NOT IMPLEMENTED)",
                formula="reit_ptp_component = 20% × (reit_dividends + ptp_income)",
                inputs=["reit_dividends", "ptp_income"],
                output="reit_ptp_component",
                code_reference="⚠️ This step is missing from PolicyEngine"
            ),
            ComputationStep(
                id="step_b1_3",
                description="Calculate combined amount",
                formula="combined_qbid = sum_business_qbid + reit_ptp_component",
                inputs=["sum_business_qbid", "reit_ptp_component"],
                output="combined_qbid"
            ),
        ],
        variables_used=["qbid_amount", "qualified_business_income_deduction"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qualified_business_income_deduction.py",
        next_sections=["sec_a_allowance"],
        depends_on=["sec_b2_wage_limitation", "sec_b3_phaseout", "sec_d2_sstb"],
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
                value=0.50,
                unit="rate"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.max.w2_wages.alt_rate",
                label="W-2 Wage Rate (alternative)",
                value=0.25,
                unit="rate"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.max.business_property.rate",
                label="Property Basis Rate",
                value=0.025,
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
        decisions=[
            DecisionPoint(
                id="dec_b2_apply",
                condition="Is taxable income above the threshold?",
                condition_formula="taxable_income > threshold",
                true_branch="Apply wage/property limitation",
                false_branch="No limitation - use full 20% × QBI",
                threshold_values={"SINGLE": 197300, "JOINT": 394600}
            )
        ],
        variables_used=["qbid_amount", "w2_wages_from_qualified_business", "unadjusted_basis_qualified_property"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qbid_amount.py",
        next_sections=["sec_b1_combined_qbi"],
        depends_on=["sec_c_qbi_definition", "sec_e_thresholds"],
    )


def _build_section_b3_phaseout(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(b)(3) - Phase-in of limitation."""
    return LawSection(
        id="sec_b3_phaseout",
        section_number="199A(b)(3)",
        title="Phase-In of Wage/Property Limitation",
        description="The W-2 wage limitation phases in over $50,000 ($100,000 for joint filers) above the threshold. Below threshold: no limitation. In phase-in range: partial limitation. Above phase-in: full limitation.",
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
                label="Phase-out Start (Single)",
                value=197300,
                unit="USD",
                year=2025,
                filing_status="SINGLE"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label="Phase-out Start (Joint)",
                value=394600,
                unit="USD",
                year=2025,
                filing_status="JOINT"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.length",
                label="Phase-out Range (Single)",
                value=50000,
                unit="USD",
                filing_status="SINGLE"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.length",
                label="Phase-out Range (Joint)",
                value=100000,
                unit="USD",
                filing_status="JOINT"
            ),
        ],
        steps=[
            ComputationStep(
                id="step_b3_1",
                description="Calculate reduction rate based on income in phase-out range",
                formula="reduction_rate = MIN(1, (taxable_income - threshold) / phase_out_length)",
                formula_latex=r"\text{Reduction Rate} = \min\left(1, \frac{\text{Income} - \text{Threshold}}{\text{Phase-out Length}}\right)",
                inputs=["taxable_income_less_qbid", "threshold", "phase_out_length"],
                output="reduction_rate"
            ),
            ComputationStep(
                id="step_b3_2",
                description="Calculate reduction amount",
                formula="reduction = reduction_rate × MAX(0, 20% × QBI - wage_cap)",
                inputs=["reduction_rate", "qbid_max", "full_cap"],
                output="reduction"
            ),
            ComputationStep(
                id="step_b3_3",
                description="Apply reduction to get phased QBID",
                formula="phased_qbid = 20% × QBI - reduction",
                inputs=["qbid_max", "reduction"],
                output="phased_qbid"
            ),
        ],
        decisions=[
            DecisionPoint(
                id="dec_b3_range",
                condition="Where is income relative to threshold?",
                condition_formula="taxable_income vs threshold",
                true_branch="Below threshold: No limitation",
                false_branch="In range: Partial | Above: Full limitation",
                threshold_values={"SINGLE": 197300, "JOINT": 394600}
            )
        ],
        variables_used=["qbid_amount", "taxable_income_less_qbid", "filing_status"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qbid_amount.py",
        next_sections=["sec_b1_combined_qbi"],
        depends_on=["sec_b2_wage_limitation", "sec_e_thresholds"],
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
        next_sections=["sec_b2_wage_limitation"],
        depends_on=[],
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
        next_sections=["sec_b2_wage_limitation"],
        depends_on=["sec_c_qbi_definition"],
    )


def _build_section_c3_exclusions(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(c)(3)(B) - Items not included in QBI."""
    return LawSection(
        id="sec_c3_exclusions",
        section_number="199A(c)(3)(B)",
        title="Items Excluded from QBI",
        description="Certain items are explicitly excluded from QBI: capital gains/losses, dividends, interest (unless business-allocable), reasonable compensation, and guaranteed payments.",
        legal_reference=LegalReference(
            section="199A(c)(3)(B)",
            title="Items not included",
            url=f"{CORNELL_BASE}#c_3_B",
            text="The following items shall not be taken into account as a qualified item of income, gain, deduction, or loss: (i) short-term or long-term capital gain or loss, (ii) dividend income, (iii) interest income, (iv) foreign currency gains or losses... (vi) any item of deduction or loss properly allocable to such amounts, (vii) reasonable compensation paid for services rendered, (viii) guaranteed payments for services..."
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
        next_sections=["sec_c_qbi_definition"],
        depends_on=[],
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
        next_sections=["sec_c_qbi_definition"],
        depends_on=[],
    )


def _build_section_d2_sstb(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(d)(2) - Specified service trade or business."""
    return LawSection(
        id="sec_d2_sstb",
        section_number="199A(d)(2)",
        title="Specified Service Trade or Business (SSTB)",
        description="SSTBs include health, law, accounting, actuarial science, performing arts, consulting, athletics, financial services, brokerage, and any business where principal asset is reputation/skill. SSTBs get NO deduction above the phase-out range, but are eligible below threshold.",
        legal_reference=LegalReference(
            section="199A(d)(2)",
            title="Specified service trade or business",
            url=f"{CORNELL_BASE}#d_2",
            text="The term 'specified service trade or business' means any trade or business... which involves the performance of services in the fields of health, law, accounting, actuarial science, performing arts, consulting, athletics, financial services, brokerage services..."
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
        decisions=[
            DecisionPoint(
                id="dec_d2_sstb",
                condition="Is this a Specified Service Trade or Business?",
                condition_formula="business_is_sstb == True",
                true_branch="Apply SSTB phase-out (0% above threshold + range)",
                false_branch="No SSTB reduction"
            )
        ],
        variables_used=["business_is_sstb", "qbid_amount"],
        github_url=f"{GITHUB_BASE}/policyengine_us/variables/household/income/person/self_employment/business_is_sstb.py",
        next_sections=["sec_b1_combined_qbi"],
        depends_on=["sec_b3_phaseout"],
    )


def _build_section_e_thresholds(variables: Dict, parameters: Dict) -> LawSection:
    """§199A(e) - Threshold amounts."""
    return LawSection(
        id="sec_e_thresholds",
        section_number="199A(e)",
        title="Threshold Amounts",
        description="The threshold amount is $157,500 ($315,000 for joint filers), adjusted annually for inflation. These thresholds determine when wage/property limitations and SSTB exclusions begin to apply.",
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
                label="2025 Threshold (Single/HoH)",
                value=197300,
                unit="USD",
                year=2025,
                filing_status="SINGLE"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label="2025 Threshold (Joint)",
                value=394600,
                unit="USD",
                year=2025,
                filing_status="JOINT"
            ),
            Parameter(
                name="gov.irs.deductions.qbi.phase_out.start",
                label="2025 Threshold (MFS)",
                value=197300,
                unit="USD",
                year=2025,
                filing_status="SEPARATE"
            ),
        ],
        variables_used=["filing_status", "taxable_income_less_qbid"],
        github_url=f"{GITHUB_BASE}/policyengine_us/parameters/gov/irs/deductions/qbi/phase_out/start.yaml",
        next_sections=["sec_b2_wage_limitation", "sec_b3_phaseout"],
        depends_on=[],
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
            text="In the case of an applicable taxpayer... the deduction shall be not less than $400... An applicable taxpayer is one with qualified business income of $1,000 or more."
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
                description="Check if QBI meets minimum threshold",
                formula="if qualified_business_income >= 1000",
                inputs=["qualified_business_income"],
                output="eligible_for_floor"
            ),
            ComputationStep(
                id="step_i2",
                description="Apply floor if eligible",
                formula="final_qbid = MAX(calculated_qbid, 400)",
                inputs=["calculated_qbid", "floor_amount"],
                output="final_qbid"
            ),
        ],
        variables_used=["qualified_business_income_deduction"],
        github_url=f"{GITHUB_BASE}/policyengine_us/parameters/gov/irs/deductions/qbi/deduction_floor/",
        next_sections=[],
        depends_on=["sec_a_allowance"],
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
            text="In the case of any taxable year of a specified agricultural or horticultural cooperative... there shall be allowed as a deduction an amount equal to 9 percent of the lesser of— (A) the qualified production activities income of the cooperative for the taxable year..."
        ),
        status=ImplementationStatus.MISSING,
        status_notes="Cooperative provisions are NOT implemented in PolicyEngine",
        variables_used=[],
        next_sections=[],
        depends_on=[],
    )


def calculate_qbid(inputs: CalculatorInput) -> CalculatorResult:
    """Run an interactive QBID calculation with step-by-step results."""

    steps = []
    warnings = []
    missing_features = []

    # Step 1: Calculate gross QBI
    gross_qbi = 0
    qbi_by_source = {}

    if inputs.self_employment_qualified:
        gross_qbi += inputs.self_employment_income
        qbi_by_source["self_employment"] = inputs.self_employment_income
    if inputs.partnership_qualified:
        gross_qbi += inputs.partnership_s_corp_income
        qbi_by_source["partnership_s_corp"] = inputs.partnership_s_corp_income
    if inputs.rental_qualified:
        gross_qbi += inputs.rental_income
        qbi_by_source["rental"] = inputs.rental_income
    if inputs.farm_qualified:
        gross_qbi += inputs.farm_income
        qbi_by_source["farm"] = inputs.farm_income

    steps.append(CalculatorStep(
        section_id="sec_c_qbi_definition",
        section_title="§199A(c) - QBI Definition",
        description="Sum qualified income sources",
        inputs=qbi_by_source,
        computation=f"Gross QBI = {' + '.join(f'${v:,.0f}' for v in qbi_by_source.values())}",
        result=gross_qbi,
        result_label="Gross QBI"
    ))

    # Step 2: Subtract QBI deductions
    qbi_deductions = inputs.se_tax_deduction + inputs.health_insurance_deduction + inputs.pension_deduction
    net_qbi = max(0, gross_qbi - qbi_deductions)

    steps.append(CalculatorStep(
        section_id="sec_c_qbi_definition",
        section_title="§199A(c) - QBI Deductions",
        description="Subtract allocable deductions",
        inputs={
            "se_tax_deduction": inputs.se_tax_deduction,
            "health_insurance": inputs.health_insurance_deduction,
            "pension": inputs.pension_deduction
        },
        computation=f"Net QBI = ${gross_qbi:,.0f} - ${qbi_deductions:,.0f}",
        result=net_qbi,
        result_label="Net QBI"
    ))

    # Step 3: Calculate base QBID (20%)
    qbid_max = 0.20 * net_qbi

    steps.append(CalculatorStep(
        section_id="sec_b1_combined_qbi",
        section_title="§199A(b)(1) - Base Deduction",
        description="Calculate 20% of QBI",
        inputs={"net_qbi": net_qbi},
        computation=f"Base QBID = 20% × ${net_qbi:,.0f}",
        result=qbid_max,
        result_label="Base QBID"
    ))

    # Step 4: Determine threshold
    thresholds = {
        "SINGLE": 197300,
        "JOINT": 394600,
        "SEPARATE": 197300,
        "HEAD_OF_HOUSEHOLD": 197300,
        "SURVIVING_SPOUSE": 394600,
    }
    phase_out_lengths = {
        "SINGLE": 50000,
        "JOINT": 100000,
        "SEPARATE": 50000,
        "HEAD_OF_HOUSEHOLD": 50000,
        "SURVIVING_SPOUSE": 100000,
    }

    threshold = thresholds.get(inputs.filing_status, 197300)
    phase_out_length = phase_out_lengths.get(inputs.filing_status, 50000)

    # Step 5: Calculate wage/property caps
    wage_cap = 0.50 * inputs.w2_wages
    alt_cap = 0.25 * inputs.w2_wages + 0.025 * inputs.property_basis
    full_cap = max(wage_cap, alt_cap)

    limitation_applied = False
    limitation_type = None

    steps.append(CalculatorStep(
        section_id="sec_b2_wage_limitation",
        section_title="§199A(b)(2) - Wage/Property Cap",
        description="Calculate limitation caps",
        inputs={
            "w2_wages": inputs.w2_wages,
            "property_basis": inputs.property_basis
        },
        computation=f"Wage Cap = 50% × ${inputs.w2_wages:,.0f} = ${wage_cap:,.0f}\nAlt Cap = 25% × ${inputs.w2_wages:,.0f} + 2.5% × ${inputs.property_basis:,.0f} = ${alt_cap:,.0f}",
        result=full_cap,
        result_label="Applicable Cap",
        notes=f"Using {'wage-only' if wage_cap >= alt_cap else 'wage+property'} cap"
    ))

    # Step 6: Apply phase-out
    taxable_income = inputs.taxable_income
    reduction_rate = min(1, max(0, taxable_income - threshold) / phase_out_length)
    applicable_rate = 1 - reduction_rate

    if taxable_income <= threshold:
        phase_status = "Below threshold - no limitation"
        phased_qbid = qbid_max
    elif taxable_income >= threshold + phase_out_length:
        phase_status = "Above phase-out - full limitation applies"
        phased_qbid = min(qbid_max, full_cap)
        limitation_applied = True
        limitation_type = "full"
    else:
        phase_status = f"In phase-out range ({reduction_rate*100:.1f}% limited)"
        reduction = reduction_rate * max(0, qbid_max - full_cap)
        phased_qbid = qbid_max - reduction
        limitation_applied = True
        limitation_type = "partial"

    steps.append(CalculatorStep(
        section_id="sec_b3_phaseout",
        section_title="§199A(b)(3) - Phase-Out",
        description="Apply income-based phase-out",
        inputs={
            "taxable_income": taxable_income,
            "threshold": threshold,
            "phase_out_length": phase_out_length
        },
        computation=f"Reduction rate = ({taxable_income:,.0f} - {threshold:,.0f}) / {phase_out_length:,.0f} = {reduction_rate:.2%}",
        result=phased_qbid,
        result_label="Phased QBID",
        notes=phase_status
    ))

    # Step 7: Apply SSTB reduction
    sstb_reduction = 0
    if inputs.is_sstb:
        if taxable_income > threshold + phase_out_length:
            # Above phase-out: SSTB gets nothing
            sstb_reduction = phased_qbid
            phased_qbid = 0
            sstb_note = "SSTB above phase-out range - no deduction allowed"
        elif taxable_income > threshold:
            # In phase-out: SSTB proportionally reduced
            sstb_reduction = phased_qbid * reduction_rate
            phased_qbid = phased_qbid * applicable_rate
            sstb_note = f"SSTB reduced by {reduction_rate:.1%}"
        else:
            sstb_note = "SSTB below threshold - full deduction allowed"

        steps.append(CalculatorStep(
            section_id="sec_d2_sstb",
            section_title="§199A(d)(2) - SSTB Reduction",
            description="Apply SSTB phase-out",
            inputs={"is_sstb": inputs.is_sstb, "applicable_rate": applicable_rate},
            computation=f"SSTB Multiplier = {applicable_rate:.2%}",
            result=phased_qbid,
            result_label="After SSTB",
            notes=sstb_note
        ))

    # Step 8: Add REIT/PTP (not implemented - warn user)
    if inputs.reit_dividends > 0 or inputs.ptp_income > 0:
        reit_ptp_component = 0.20 * (inputs.reit_dividends + inputs.ptp_income)
        missing_features.append("REIT dividends and PTP income")
        warnings.append(f"REIT/PTP income (${inputs.reit_dividends + inputs.ptp_income:,.0f}) would add ${reit_ptp_component:,.0f} to QBID but is NOT implemented in PolicyEngine")

    # Step 9: Apply taxable income cap
    taxable_income_cap = 0.20 * max(0, taxable_income - inputs.capital_gains)
    taxable_income_cap_applied = phased_qbid > taxable_income_cap
    final_qbid = min(phased_qbid, taxable_income_cap)

    steps.append(CalculatorStep(
        section_id="sec_a_allowance",
        section_title="§199A(a) - Final Cap",
        description="Apply taxable income limitation",
        inputs={
            "taxable_income": taxable_income,
            "capital_gains": inputs.capital_gains
        },
        computation=f"Cap = 20% × (${taxable_income:,.0f} - ${inputs.capital_gains:,.0f}) = ${taxable_income_cap:,.0f}",
        result=final_qbid,
        result_label="Final QBID",
        notes="Taxable income cap applied" if taxable_income_cap_applied else "Taxable income cap not binding"
    ))

    return CalculatorResult(
        inputs=inputs,
        steps=steps,
        final_deduction=final_qbid,
        qbi_by_source=qbi_by_source,
        limitation_applied=limitation_applied,
        limitation_type=limitation_type,
        sstb_reduction=sstb_reduction,
        taxable_income_cap_applied=taxable_income_cap_applied,
        warnings=warnings,
        missing_features_used=missing_features,
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
            relevance_to_qbid="§199A(d)(2) incorporates this definition to identify SSTBs whose owners cannot claim QBID above the income threshold.",
            legal_reference=LegalReference(
                section="1202(e)(3)(A)",
                title="Qualified small business stock - Excluded businesses",
                url="https://www.law.cornell.edu/uscode/text/26/1202#e_3_A",
                text="The term 'qualified trade or business' shall not include any trade or business involving the performance of services in the fields of health, law, engineering, architecture, accounting, actuarial science, performing arts, consulting, athletics, financial services, brokerage services..."
            ),
            status=ImplementationStatus.COMPLETE,
            status_notes="PolicyEngine fully implements SSTB handling via business_is_sstb boolean. The phase-out calculation correctly applies the SSTB reduction factor (1-reduction_rate) to zero out SSTB income above threshold.",
            key_provisions=[
                "Health services",
                "Law",
                "Accounting",
                "Actuarial science",
                "Performing arts",
                "Consulting",
                "Athletics",
                "Financial services",
                "Brokerage services",
                "Any business where principal asset is reputation/skill of employees"
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
            status=ImplementationStatus.PARTIAL,
            status_notes="PolicyEngine has 'qualified_reit_and_ptp_income' variable BUT it is NOT connected to the QBID calculation. The documentation misleadingly says 'Part of QBID calculation' but the variable is unused. REIT dividends should get a separate 20% deduction added to the final QBID.",
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
            status=ImplementationStatus.PARTIAL,
            status_notes="PolicyEngine has 'qualified_reit_and_ptp_income' variable (combines both) BUT it is NOT used in QBID calculation. Should be added to final deduction as: QBID = Combined QBI Component + 20% × REIT/PTP Income.",
            key_provisions=[
                "PTP = partnership traded on established securities market",
                "Qualified PTP income = ordinary income from PTP (not SSTB)",
                "20% deduction without W-2 wage limitation",
                "20% deduction without property basis limitation",
                "PTP losses reduce PTP income component (not QBI from other businesses)",
                "Reported on Schedule K-1"
            ],
            variables_used=[],
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
            section_number="§707(a)(c)",
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
            relevance_to_qbid="§199A(b)(4) references these rules for determining W-2 wages across related entities. Taxpayers may also elect to aggregate businesses under §199A(b)(5).",
            legal_reference=LegalReference(
                section="52",
                title="Controlled groups",
                url="https://www.law.cornell.edu/uscode/text/26/52",
                text="For purposes of this subpart, all employees of all corporations which are members of the same controlled group of corporations shall be treated as employed by a single employer."
            ),
            status=ImplementationStatus.MISSING,
            status_notes="Aggregation election under §199A(b)(5) is NOT implemented. Each business is treated independently. Users cannot elect to combine multiple qualifying businesses to share W-2 wages.",
            key_provisions=[
                "Controlled groups share wage limitation calculations",
                "Taxpayers may ELECT to aggregate qualifying businesses",
                "Aggregated businesses share one set of thresholds",
                "Can benefit taxpayers with multiple businesses (some with high wages, some without)",
                "Election is irrevocable without IRS consent"
            ],
            variables_used=[],
            referenced_by=["199A(b)(4)", "199A(b)(5)"]
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
                "Base year for QBID thresholds is 2017",
                "Rounded to nearest $50 for phase-out start",
                "Thresholds updated annually",
                "2024 thresholds: $191,950 single / $383,900 joint"
            ],
            variables_used=[],
            referenced_by=["199A(e)(2)(B)"]
        ),

        # Section 199A(c)(2) - Loss Carryforward (internal but critical)
        AdjacentSection(
            id="sec_199A_c2",
            section_number="§199A(c)(2)",
            title="QBI Loss Carryforward Rules",
            description="Provides that negative QBI (losses) carry forward to reduce future QBI amounts.",
            relevance_to_qbid="This is a core §199A provision. If QBI is negative, the loss offsets future QBI dollar-for-dollar before the 20% deduction is calculated.",
            legal_reference=LegalReference(
                section="199A(c)(2)",
                title="Carryover of loss",
                url="https://www.law.cornell.edu/uscode/text/26/199A#c_2",
                text="If the net amount of qualified business income from all qualified trades or businesses during any taxable year is less than zero, such amount shall be treated as a loss... carried forward to the next taxable year."
            ),
            status=ImplementationStatus.MISSING,
            status_notes="PolicyEngine uses max(0, QBI) and does NOT carry forward negative QBI to future years.",
            key_provisions=[
                "Negative QBI creates a QBI loss carryforward",
                "Loss reduces QBI in subsequent years",
                "Tracked separately from NOL carryforwards",
                "Reduces QBI before 20% calculation",
                "No limitation on carryforward period"
            ],
            variables_used=["qualified_business_income"],
            github_url=f"{GITHUB_BASE}/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction/qualified_business_income.py",
            referenced_by=["199A(c)(2)"]
        ),
    ]
