"""Service for comparing TAXSIM and PolicyEngine QBI implementations."""

import os
import subprocess
import tempfile
from typing import Dict, List, Optional

from app.models.taxsim_comparison import (
    TaxsimInputVariable,
    TaxsimCodeBlock,
    PolicyEngineCodeBlock,
    ComparisonItem,
    AdjacentSectionCoverage,
    TaxsimQBIImplementation,
    PolicyEngineQBIImplementation,
    ComparisonResult,
    CalculationComparisonInput,
    CalculationComparisonResult,
)


# TAXSIM source path
TAXSIM_PATH = "/Users/pavelmakarchuk/taxsim"
TAXSIM_EXECUTABLE = "/Users/pavelmakarchuk/policyengine-taxsim/resources/taxsim35/taxsim35-osx.exe"

# TAXSIM QBI-related data variables (from documentation and code analysis)
TAXSIM_QBI_VARIABLES = [
    TaxsimInputVariable(
        number=211,
        name="pbusinc",
        description="Primary taxpayer's active QBI (non-SSTB) - subject to preferential rate without phaseout",
        qbi_related=True
    ),
    TaxsimInputVariable(
        number=212,
        name="pprofinc",
        description="Primary taxpayer's SSTB income - subject to claw-back phaseout",
        qbi_related=True
    ),
    TaxsimInputVariable(
        number=213,
        name="rentinc",
        description="Rental income eligible for QBI (from documentation context)",
        qbi_related=True
    ),
    TaxsimInputVariable(
        number=214,
        name="sbusinc",
        description="Secondary taxpayer's active QBI (non-SSTB)",
        qbi_related=True
    ),
    TaxsimInputVariable(
        number=215,
        name="sprofinc",
        description="Secondary taxpayer's SSTB income",
        qbi_related=True
    ),
    TaxsimInputVariable(
        number=224,
        name="scorp",
        description="S-Corp and other passive business income (non-SSTB, no SECA)",
        qbi_related=True
    ),
    TaxsimInputVariable(
        number=17,
        name="gssi",
        description="Gross Social Security (used in QBI calc context for pass-through)",
        qbi_related=False  # Not directly QBI but appears in formula
    ),
]


def get_taxsim_qbi_code() -> List[TaxsimCodeBlock]:
    """Extract QBI-related code blocks from TAXSIM source."""

    # Main QBI calculation from law87.for (lines 791-808)
    main_qbi_calc = """c 2018+ pass-through income qualifies for 20% deduction
c income after fica and phaseout for sstb + scorp only
      if(lawyr.ge.2018) then
        ptqbi  =max(0.d0,data(211))+max(0.d0,data(214))
     &  +max(0.d0,data(224))+max(0d0,data(17))
        ptsst  =max(0.d0,data(212))+max(0.d0,data(215))
        ptfica =sen
        ptinc  =data(213)+ptqbi+ptsst-ptfica
        ptstrt =phin(lawyr,max(1,int(data(7))))
        if(sepret.eq.2.and.lawyr.eq.2019) ptstrt=160725.d0
        ptexcs =max(0d0,taxinc-ptstrt)
        perc   =min(1.d0,max(0.d0,ptexcs/50000.d0))
        ptlim  =max(0.d0,.2d0*(taxinc-(capgn+data(12))))
        ptded  =.2d0*(ptsst*(1.d0-perc)+ptqbi+data(213)-.5*sen)
        ptded  =max(0.d0,min(ptded,ptlim))
        taxinc=taxinc-ptded
      endif"""

    # AMT QBI deduction from law87.for (lines 1137-1138)
    amt_qbi = """c QBI deduction starts in 2018
      if(lawyr.ge.2018) alminy=max(0.0d0,alminy-ptded)"""

    # QBI split for married taxpayers (lines 1425-1437)
    qbi_split = """c qbi for primary taxpayer and spouse separate
         qbit=data(211)+data(212)+data(214)+data(215)
         if(qbit.gt.0d0) then
             setaxh = setax*(data(211) + data(212))/qbit
             setaxw = setax*(data(214) + data(215))/qbit
             seleft = setax - setaxh - setaxw
             earnww = max(0.0d0,data(17)+data(21)-.5*seleft)
             earnh = max(0.0d0,data(85)+data(211)+data(212)-.5*setaxh)
     &+earnww/2
             earnw = max(0.0d0,data(86)+data(214)+data(215)-.5*setaxw)
     &+earnww/2
         endif"""

    return [
        TaxsimCodeBlock(
            file="law87.for",
            line_start=791,
            line_end=808,
            code=main_qbi_calc,
            description="Main QBI/QBID calculation - computes pass-through deduction for 2018+",
            variables_used=["data(211)", "data(212)", "data(213)", "data(214)", "data(215)", "data(224)", "data(17)", "taxinc", "capgn", "sen"]
        ),
        TaxsimCodeBlock(
            file="law87.for",
            line_start=1137,
            line_end=1138,
            code=amt_qbi,
            description="QBI deduction applied to Alternative Minimum Tax calculation",
            variables_used=["alminy", "ptded"]
        ),
        TaxsimCodeBlock(
            file="law87.for",
            line_start=1425,
            line_end=1437,
            code=qbi_split,
            description="Split QBI between primary and secondary taxpayers for married filing",
            variables_used=["data(211)", "data(212)", "data(214)", "data(215)", "setax", "earnh", "earnw"]
        ),
    ]


def get_policyengine_qbi_code() -> List[PolicyEngineCodeBlock]:
    """Get PolicyEngine QBI code blocks."""

    github_base = "https://github.com/PolicyEngine/policyengine-us/blob/master/policyengine_us/variables/gov/irs/income/taxable_income/deductions/qualified_business_income_deduction"

    # Main QBID calculation
    main_qbid = """class qualified_business_income_deduction(Variable):
    # The final deduction is the LESSER of:
    # (1) the combined QBI amount (sum of per-person QBID amounts)
    # (2) 20% of taxable income exceeding net capital gains

    def formula(tax_unit, period, parameters):
        combined_qbi = tax_unit.sum(
            tax_unit.members("qbid_amount", period)
        )
        taxable_income = tax_unit("taxable_income_less_qbid", period)
        capital_gains = tax_unit("adjusted_net_capital_gain", period)
        p = parameters(period).gov.irs.deductions.qbi

        # 20% of taxable income cap (excluding capital gains)
        cap = p.max.rate * max_(0, taxable_income - capital_gains)

        return min_(combined_qbi, cap)"""

    # QBI definition
    qbi_def = """class qualified_business_income(Variable):
    # QBI = Sum of qualified income sources minus allocable deductions

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.qbi

        # Sum income sources (only if marked as qualified)
        total_qbi = sum([
            person(source, period) * person(f"{source}_would_be_qualified", period)
            for source in p.income
        ])

        # Subtract allocable deductions
        deductions = sum([
            person(ded, period) for ded in p.deductions
        ])

        return max_(0, total_qbi - deductions)"""

    # QBID amount per person
    qbid_amount = """class qbid_amount(Variable):
    # Per-person QBID amount with wage/property limitations

    def formula(person, period, parameters):
        qbi = person("qualified_business_income", period)
        p = parameters(period).gov.irs.deductions.qbi

        # Base: 20% of QBI
        qbid_max = p.max.rate * qbi

        # Wage/property cap (for high income)
        w2_wages = person("w2_wages_from_qualified_business", period)
        property_basis = person("unadjusted_basis_qualified_property", period)

        wage_cap = p.max.w2_wages.rate * w2_wages
        alt_cap = p.max.w2_wages.alt_rate * w2_wages + \\
                  p.max.business_property.rate * property_basis
        full_cap = max_(wage_cap, alt_cap)

        # Apply phase-out based on taxable income
        taxable_income = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)
        threshold = p.phase_out.start[filing_status]
        phase_out_length = p.phase_out.length[filing_status]

        reduction_rate = min_(1, max_(0,
            (taxable_income - threshold) / phase_out_length
        ))

        # SSTB reduction
        is_sstb = person("business_is_sstb", period)
        applicable_rate = where(is_sstb, 1 - reduction_rate, 1)

        # Final calculation
        adj_qbid_max = qbid_max * applicable_rate
        adj_cap = full_cap * applicable_rate

        return where(
            taxable_income <= threshold,
            adj_qbid_max,  # No limitation
            max_(0, adj_qbid_max - reduction_rate * max_(0, adj_qbid_max - adj_cap))
        )"""

    return [
        PolicyEngineCodeBlock(
            file="qualified_business_income_deduction.py",
            variable_name="qualified_business_income_deduction",
            code=main_qbid,
            description="Main QBID calculation - applies taxable income cap",
            github_url=f"{github_base}/qualified_business_income_deduction.py"
        ),
        PolicyEngineCodeBlock(
            file="qualified_business_income.py",
            variable_name="qualified_business_income",
            code=qbi_def,
            description="QBI definition - sums qualified sources minus deductions",
            github_url=f"{github_base}/qualified_business_income.py"
        ),
        PolicyEngineCodeBlock(
            file="qbid_amount.py",
            variable_name="qbid_amount",
            code=qbid_amount,
            description="Per-person QBID with wage/property limitations and SSTB phase-out",
            github_url=f"{github_base}/qbid_amount.py"
        ),
    ]


def build_comparison() -> ComparisonResult:
    """Build a complete comparison of TAXSIM and PolicyEngine QBI implementations."""

    taxsim_impl = TaxsimQBIImplementation(
        version="TAXSIM 35",
        source_file="law87.for",
        qbi_variables=TAXSIM_QBI_VARIABLES,
        code_blocks=get_taxsim_qbi_code(),
        key_features=[
            "Handles 2018+ TCJA pass-through deduction",
            "Separates QBI (non-SSTB) from SSTB income",
            "SSTB income phases out with income above threshold",
            "Non-SSTB QBI gets full 20% deduction (no wage limitation)",
            "Applies taxable income cap (20% of TI minus capital gains)",
            "Splits QBI between spouses for joint returns",
            "Applies QBI deduction to both regular tax and AMT",
        ],
        limitations=[
            "No W-2 wage/property limitation for non-SSTB income",
            "Simplified SSTB phaseout (flat $50k range regardless of filing status)",
            "No per-business tracking",
            "No REIT/PTP income component (separate from pass-through)",
            "No loss carryforward provisions",
            "Phase-out threshold lookup uses phin() function - hardcoded by year",
        ]
    )

    policyengine_impl = PolicyEngineQBIImplementation(
        version="PolicyEngine US",
        main_variable="qualified_business_income_deduction",
        dependent_variables=[
            "qualified_business_income",
            "qbid_amount",
            "business_is_qualified",
            "business_is_sstb",
            "w2_wages_from_qualified_business",
            "unadjusted_basis_qualified_property",
        ],
        code_blocks=get_policyengine_qbi_code(),
        key_features=[
            "Full W-2 wage and property basis limitations",
            "Per-person QBID calculation with aggregation",
            "SSTB phase-out with filing-status-specific ranges",
            "Taxable income cap (20% of TI minus capital gains)",
            "Configurable via YAML parameters",
            "Supports reform modeling",
            "Multiple income source qualification flags",
        ],
        limitations=[
            "No REIT dividends / PTP income component",
            "No QBI loss carryforward",
            "No per-business tracking (aggregated per person)",
            "No cooperative provisions (Section 199A(g))",
        ]
    )

    comparisons = [
        ComparisonItem(
            id="base_rate",
            law_section="199A(b)(1)",
            description="Base deduction rate",
            taxsim_approach="20% rate applied to all eligible QBI",
            policyengine_approach="20% rate applied via parameter (gov.irs.deductions.qbi.max.rate)",
            difference="Equivalent - both use 20% rate",
            severity="none"
        ),
        ComparisonItem(
            id="wage_limitation",
            law_section="199A(b)(2)",
            description="W-2 wage and property limitation",
            taxsim_approach="NOT IMPLEMENTED - non-SSTB income (data 211, 214, 224) always gets full deduction regardless of wages paid",
            policyengine_approach="IMPLEMENTED - applies 50% W-2 wage cap or 25% W-2 + 2.5% property basis cap for high-income taxpayers",
            taxsim_code=TaxsimCodeBlock(
                file="law87.for",
                line_start=805,
                line_end=805,
                code="ptded  =.2d0*(ptsst*(1.d0-perc)+ptqbi+data(213)-.5*sen)",
                description="Notice ptqbi (non-SSTB) is multiplied by full 20% with no wage cap",
                variables_used=["ptqbi", "ptsst", "perc", "sen"]
            ),
            difference="TAXSIM does not apply wage/property limitations to non-SSTB income. This can result in significantly higher deductions for high-income taxpayers without W-2 wages.",
            severity="significant"
        ),
        ComparisonItem(
            id="sstb_phaseout",
            law_section="199A(d)(2)",
            description="SSTB income phase-out",
            taxsim_approach="Uses 'perc' variable: min(1, (taxinc-threshold)/50000) - applies same $50k range for all filing statuses",
            policyengine_approach="Filing-status-specific phase-out: $50k for single, $100k for joint",
            taxsim_code=TaxsimCodeBlock(
                file="law87.for",
                line_start=803,
                line_end=803,
                code="perc   =min(1.d0,max(0.d0,ptexcs/50000.d0))",
                description="Hardcoded $50,000 phase-out range",
                variables_used=["ptexcs"]
            ),
            difference="TAXSIM uses $50k phase-out for everyone; PolicyEngine correctly uses $100k for joint filers per statute",
            severity="minor"
        ),
        ComparisonItem(
            id="income_cap",
            law_section="199A(a)",
            description="Taxable income cap",
            taxsim_approach="ptlim = max(0, 0.2*(taxinc-(capgn+data(12)))) - caps at 20% of TI minus capital gains",
            policyengine_approach="Same formula: min(combined_qbi, 0.2*(taxable_income - capital_gains))",
            taxsim_code=TaxsimCodeBlock(
                file="law87.for",
                line_start=804,
                line_end=804,
                code="ptlim  =max(0.d0,.2d0*(taxinc-(capgn+data(12))))",
                description="Taxable income limitation",
                variables_used=["taxinc", "capgn", "data(12)"]
            ),
            difference="Equivalent implementation",
            severity="none"
        ),
        ComparisonItem(
            id="se_tax_deduction",
            law_section="199A(c)(1)",
            description="SE tax deduction from QBI",
            taxsim_approach="Subtracts 0.5*sen (half of SE tax) directly in QBID formula",
            policyengine_approach="QBI is reduced by self_employment_tax_ald_person before 20% calculation",
            taxsim_code=TaxsimCodeBlock(
                file="law87.for",
                line_start=805,
                line_end=805,
                code="ptded  =.2d0*(ptsst*(1.d0-perc)+ptqbi+data(213)-.5*sen)",
                description="Note: -.5*sen subtracts half of SE tax",
                variables_used=["sen"]
            ),
            difference="TAXSIM applies SE tax deduction at the QBID level; PolicyEngine applies it at the QBI level. Both reduce the final deduction equivalently.",
            severity="none"
        ),
        ComparisonItem(
            id="reit_ptp",
            law_section="199A(b)(1)(B)",
            description="REIT dividends and PTP income",
            taxsim_approach="NOT IMPLEMENTED as separate QBI component",
            policyengine_approach="NOT IMPLEMENTED",
            difference="Neither implementation includes the REIT/PTP 20% deduction component",
            severity="significant"
        ),
        ComparisonItem(
            id="loss_carryforward",
            law_section="199A(c)(2)",
            description="QBI loss carryforward",
            taxsim_approach="NOT IMPLEMENTED - negative QBI zeroed out",
            policyengine_approach="NOT IMPLEMENTED - uses max(0, qbi)",
            difference="Both ignore loss carryforward provisions",
            severity="minor"
        ),
        ComparisonItem(
            id="amt_treatment",
            law_section="199A",
            description="AMT treatment of QBID",
            taxsim_approach="QBID explicitly deducted from AMT income (alminy)",
            policyengine_approach="QBID reduces taxable income which affects AMT calculation",
            taxsim_code=TaxsimCodeBlock(
                file="law87.for",
                line_start=1138,
                line_end=1138,
                code="if(lawyr.ge.2018) alminy=max(0.0d0,alminy-ptded)",
                description="QBI deduction applied to AMT",
                variables_used=["alminy", "ptded"]
            ),
            difference="Both correctly allow QBID for AMT purposes",
            severity="none"
        ),
        ComparisonItem(
            id="spouse_split",
            law_section="199A",
            description="QBI allocation between spouses",
            taxsim_approach="Splits QBI proportionally based on each spouse's share of total QBI",
            policyengine_approach="Per-person QBID calculation based on each person's own QBI",
            taxsim_code=TaxsimCodeBlock(
                file="law87.for",
                line_start=1427,
                line_end=1430,
                code="""qbit=data(211)+data(212)+data(214)+data(215)
if(qbit.gt.0d0) then
    setaxh = setax*(data(211) + data(212))/qbit
    setaxw = setax*(data(214) + data(215))/qbit""",
                description="Proportional QBI split for SE tax allocation",
                variables_used=["data(211)", "data(212)", "data(214)", "data(215)", "setax"]
            ),
            difference="Different approaches but should yield same total QBID for joint returns",
            severity="none"
        ),
    ]

    # Build adjacent section coverage comparison
    adjacent_coverage = get_adjacent_section_coverage()

    return ComparisonResult(
        taxsim=taxsim_impl,
        policyengine=policyengine_impl,
        comparisons=comparisons,
        adjacent_section_coverage=adjacent_coverage,
        summary={
            "none": sum(1 for c in comparisons if c.severity == "none"),
            "minor": sum(1 for c in comparisons if c.severity == "minor"),
            "significant": sum(1 for c in comparisons if c.severity == "significant"),
            "critical": sum(1 for c in comparisons if c.severity == "critical"),
        },
        methodology_differences=[
            "TAXSIM separates SSTB from non-SSTB income explicitly; PolicyEngine uses a boolean flag per-income-source",
            "TAXSIM uses single formula for all income; PolicyEngine has modular per-person calculation",
            "TAXSIM hardcodes year-specific thresholds in phin() function; PolicyEngine uses YAML parameters",
            "TAXSIM's biggest gap: No W-2 wage/property limitation for non-SSTB income",
            "PolicyEngine is more configurable for reform modeling but both miss REIT/PTP component",
            "Neither implementation handles QBI loss carryforward per §199A(c)(2)",
            "Both implementations lack REIT dividend and PTP income components",
        ]
    )


def get_adjacent_section_coverage() -> List[AdjacentSectionCoverage]:
    """Build comparison of adjacent IRC section coverage between TAXSIM and PolicyEngine."""

    return [
        AdjacentSectionCoverage(
            section_id="sec_1202",
            section_number="§1202(e)(3)(A)",
            title="SSTB Definition",
            taxsim_status="partial",
            taxsim_notes="Has separate input variables for SSTB income (pprofinc, sprofinc) but no enumerated field validation",
            policyengine_status="complete",
            policyengine_notes="Fully implemented via business_is_sstb boolean. Phase-out calculation correctly applies SSTB reduction factor (1-reduction_rate) to fully exclude SSTB income above threshold.",
            impact_on_qbid="Determines whether income is subject to phase-out above threshold - SSTB income phases to $0 above threshold+range"
        ),
        AdjacentSectionCoverage(
            section_id="sec_469",
            section_number="§469",
            title="Passive Activity Losses",
            taxsim_status="partial",
            taxsim_notes="Basic passive income handling through rental income variable (data 213)",
            policyengine_status="partial",
            policyengine_notes="Provides rental_income_would_be_qualified flag for user input. Material participation tests and 250-hour safe harbor are NOT automatically calculated.",
            impact_on_qbid="Passive losses can reduce QBI; rental must meet 250-hour safe harbor to qualify as trade/business for QBID"
        ),
        AdjacentSectionCoverage(
            section_id="sec_857",
            section_number="§857(b)(3)",
            title="REIT Taxation",
            taxsim_status="missing",
            taxsim_notes="No REIT dividend input variable or calculation",
            policyengine_status="partial",
            policyengine_notes="Variable qualified_reit_and_ptp_income exists but is NOT connected to QBID. Documentation misleadingly says 'Part of QBID calculation' but it's unused. REIT dividends should get separate 20% deduction.",
            impact_on_qbid="REIT dividends qualify for separate 20% deduction per §199A(b)(1)(B) - NOT wage limited"
        ),
        AdjacentSectionCoverage(
            section_id="sec_7704",
            section_number="§7704",
            title="Publicly Traded Partnerships",
            taxsim_status="missing",
            taxsim_notes="No PTP income input or handling",
            policyengine_status="partial",
            policyengine_notes="Variable qualified_reit_and_ptp_income exists (combines both) but is NOT used in QBID calculation. Should be added to final deduction separately from QBI component.",
            impact_on_qbid="PTP income qualifies for separate 20% deduction without wage limitation per §199A(b)(1)(B)"
        ),
        AdjacentSectionCoverage(
            section_id="sec_1_h",
            section_number="§1(h)",
            title="Net Capital Gain Definition",
            taxsim_status="complete",
            taxsim_notes="Capital gains excluded from taxable income cap via (taxinc-(capgn+data(12)))",
            policyengine_status="complete",
            policyengine_notes="Uses adjusted_net_capital_gain in taxable income cap calculation",
            impact_on_qbid="QBID cannot exceed 20% of taxable income minus net capital gains"
        ),
        AdjacentSectionCoverage(
            section_id="sec_162",
            section_number="§162",
            title="Trade or Business Expenses",
            taxsim_status="partial",
            taxsim_notes="Basic business income/expense netting through input variables",
            policyengine_status="complete",
            policyengine_notes="Full ordinary and necessary business expense handling",
            impact_on_qbid="Determines what constitutes a qualified trade or business"
        ),
        AdjacentSectionCoverage(
            section_id="sec_707",
            section_number="§707(a)(c)",
            title="Partnership Transactions",
            taxsim_status="partial",
            taxsim_notes="S-corp/partnership income as lump sum (scorp variable)",
            policyengine_status="partial",
            policyengine_notes="Basic guaranteed payments handling; §707(c) payments excluded from QBI",
            impact_on_qbid="Guaranteed payments to partners are NOT qualified business income"
        ),
        AdjacentSectionCoverage(
            section_id="sec_167_168",
            section_number="§167/168",
            title="Depreciation and UBIA",
            taxsim_status="missing",
            taxsim_notes="No property basis input; wage/property limitation not implemented at all",
            policyengine_status="partial",
            policyengine_notes="Variable unadjusted_basis_qualified_property exists but is USER INPUT ONLY. Does not auto-calculate from depreciation schedules or validate property is within depreciable period. The 25%+2.5% formula IS correctly applied.",
            impact_on_qbid="UBIA is alternative to 50% wage cap: 25% W-2 + 2.5% property basis. Useful for capital-intensive businesses with few employees."
        ),
        AdjacentSectionCoverage(
            section_id="sec_52",
            section_number="§52(a)(b)",
            title="Controlled Group Aggregation",
            taxsim_status="missing",
            taxsim_notes="No controlled group or common ownership handling",
            policyengine_status="partial",
            policyengine_notes="Basic wage aggregation for commonly controlled entities",
            impact_on_qbid="Related businesses can aggregate W-2 wages for limitation calculation"
        ),
        AdjacentSectionCoverage(
            section_id="sec_6051",
            section_number="§6051(a)",
            title="W-2 Wage Reporting",
            taxsim_status="missing",
            taxsim_notes="No W-2 wage input for QBI limitation; wage cap not implemented",
            policyengine_status="partial",
            policyengine_notes="Variables w2_wages_from_qualified_business and unadjusted_basis_qualified_property exist but are USER INPUT ONLY - no automatic calculation from W-2 forms or depreciation schedules",
            impact_on_qbid="W-2 wages from qualified business limit QBID for high-income taxpayers via 50% cap or 25%+2.5% alternative"
        ),
        AdjacentSectionCoverage(
            section_id="sec_1382_1385",
            section_number="§1382/1385",
            title="Agricultural Cooperatives",
            taxsim_status="missing",
            taxsim_notes="No cooperative provisions",
            policyengine_status="missing",
            policyengine_notes="§199A(g) cooperative provisions not implemented",
            impact_on_qbid="Patrons of agricultural cooperatives get additional deduction"
        ),
        AdjacentSectionCoverage(
            section_id="sec_475",
            section_number="§475(c)(2), (e)(2)",
            title="Securities and Commodities",
            taxsim_status="missing",
            taxsim_notes="No specific securities/commodities dealer handling",
            policyengine_status="partial",
            policyengine_notes="SSTB includes brokerage but commodities dealer status not modeled",
            impact_on_qbid="Dealers in securities are SSTBs; commodities definitions affect qualification"
        ),
        AdjacentSectionCoverage(
            section_id="sec_1_f",
            section_number="§1(f)(3)",
            title="COLA Adjustment",
            taxsim_status="complete",
            taxsim_notes="Year-specific thresholds via phin() lookup function",
            policyengine_status="complete",
            policyengine_notes="Thresholds uprated via YAML parameters with CPI adjustments",
            impact_on_qbid="Phase-out thresholds ($182,100/$364,200 for 2023) adjusted annually"
        ),
        AdjacentSectionCoverage(
            section_id="sec_199A_c2",
            section_number="§199A(c)(2)",
            title="QBI Loss Carryforward",
            taxsim_status="missing",
            taxsim_notes="Negative QBI zeroed out with max(0, ...) - no carryforward",
            policyengine_status="missing",
            policyengine_notes="Uses max_(0, QBI) which zeroes out losses instead of carrying forward",
            impact_on_qbid="Losses should reduce QBI in subsequent years; both implementations ignore this"
        ),
    ]


def run_taxsim_calculation(inputs: CalculationComparisonInput) -> Dict:
    """Run TAXSIM calculation and return result."""

    # Map filing status
    mstat_map = {
        "SINGLE": 1,
        "JOINT": 2,
        "HEAD_OF_HOUSEHOLD": 1,  # TAXSIM determines HoH from dependents
        "SEPARATE": 6,
        "SURVIVING_SPOUSE": 2,
    }

    # Build TAXSIM input line (CSV format)
    # Format: taxsimid,year,state,mstat,page,sage,depx,...income vars...
    taxsim_input = {
        "taxsimid": 1,
        "year": inputs.year,
        "state": 0,  # Federal only
        "mstat": mstat_map.get(inputs.filing_status, 1),
        "page": 40,  # Assume adult
        "sage": 40 if inputs.filing_status in ["JOINT", "SEPARATE"] else 0,
        "depx": 0,
        # Income variables
        "pwages": 0,
        "swages": 0,
        "psemp": inputs.self_employment_income,  # Non-QBI self-employment
        "ssemp": 0,
        "dividends": 0,
        "intrec": 0,
        "stcg": 0,
        "ltcg": inputs.capital_gains,
        "otherprop": inputs.rental_income,  # Goes to data(14) -> otherprop
        "nonprop": 0,
        "pensions": 0,
        "gssi": 0,
        "pui": 0,
        "sui": 0,
        "transfers": 0,
        "rentpaid": 0,
        "proptax": 0,
        "otheritem": 0,
        "childcare": 0,
        "mortgage": 0,
        # QBI-specific (TCJA)
        "scorp": inputs.partnership_s_corp_income,  # Non-SSTB pass-through
        "pbusinc": 0,  # Active QBI for primary (we use self_employment_income)
        "sbusinc": 0,  # Active QBI for secondary
        "pprofinc": inputs.sstb_income,  # SSTB for primary
        "sprofinc": 0,  # SSTB for secondary
    }

    # Create CSV line
    csv_header = ",".join(taxsim_input.keys())
    csv_values = ",".join(str(v) for v in taxsim_input.values())

    # Note: Running TAXSIM would require the executable
    # For now, return a simulation of what TAXSIM would calculate

    # Simulate TAXSIM's QBI calculation based on the FORTRAN code
    # ptqbi = non-SSTB QBI (pbusinc + sbusinc + scorp + gssi)
    ptqbi = max(0, inputs.partnership_s_corp_income)

    # ptsst = SSTB income
    ptsst = max(0, inputs.sstb_income)

    # Total pass-through income
    # ptinc = rental + ptqbi + ptsst - fica_deduction
    # (simplified - ignoring FICA for now)
    ptinc = inputs.rental_income + ptqbi + ptsst

    # Threshold (TAXSIM uses phin function - we'll use 2023 values)
    threshold_2023 = 182100 if inputs.filing_status == "SINGLE" else 364200

    # Phase-out percentage (TAXSIM uses flat $50k)
    ptexcs = max(0, inputs.taxable_income - threshold_2023)
    perc = min(1.0, ptexcs / 50000)

    # Taxable income cap
    ptlim = max(0, 0.2 * (inputs.taxable_income - inputs.capital_gains))

    # TAXSIM QBID formula:
    # ptded = 0.2 * (ptsst*(1-perc) + ptqbi + rental - 0.5*se_tax)
    # Note: TAXSIM does NOT apply wage limitation to ptqbi!
    ptded = 0.2 * (ptsst * (1 - perc) + ptqbi + inputs.rental_income)
    ptded = max(0, min(ptded, ptlim))

    return {
        "qbid": ptded,
        "ptqbi": ptqbi,
        "ptsst": ptsst,
        "ptinc": ptinc,
        "threshold": threshold_2023,
        "perc": perc,
        "ptlim": ptlim,
        "steps": [
            {"name": "Non-SSTB QBI (ptqbi)", "value": ptqbi},
            {"name": "SSTB Income (ptsst)", "value": ptsst},
            {"name": "Rental Income", "value": inputs.rental_income},
            {"name": "Threshold", "value": threshold_2023},
            {"name": "Phase-out %", "value": perc * 100},
            {"name": "TI Cap", "value": ptlim},
            {"name": "Final QBID", "value": ptded},
        ],
        "notes": [
            "TAXSIM does NOT apply W-2 wage limitation to non-SSTB income",
            f"SSTB income ({ptsst:,.0f}) reduced by {perc*100:.1f}% phase-out",
            "Using simplified TAXSIM calculation (no actual executable run)",
        ]
    }


def run_policyengine_calculation(inputs: CalculationComparisonInput) -> Dict:
    """Run PolicyEngine-style QBI calculation."""

    # Sum QBI from all sources
    gross_qbi = (
        inputs.self_employment_income +
        inputs.partnership_s_corp_income +
        inputs.sstb_income +
        inputs.rental_income
    )

    # Base QBID (20%)
    qbid_max = 0.2 * gross_qbi

    # Threshold
    thresholds = {
        "SINGLE": 182100,
        "JOINT": 364200,
        "HEAD_OF_HOUSEHOLD": 182100,
        "SEPARATE": 182100,
    }
    phase_lengths = {
        "SINGLE": 50000,
        "JOINT": 100000,
        "HEAD_OF_HOUSEHOLD": 50000,
        "SEPARATE": 50000,
    }

    threshold = thresholds.get(inputs.filing_status, 182100)
    phase_length = phase_lengths.get(inputs.filing_status, 50000)

    # Wage/property cap
    wage_cap = 0.5 * inputs.w2_wages
    alt_cap = 0.25 * inputs.w2_wages + 0.025 * inputs.property_basis
    full_cap = max(wage_cap, alt_cap)

    # Phase-out
    reduction_rate = min(1.0, max(0, inputs.taxable_income - threshold) / phase_length)

    # SSTB handling
    sstb_ratio = inputs.sstb_income / gross_qbi if gross_qbi > 0 else 0
    applicable_rate = 1 - reduction_rate

    # Calculate QBID with limitations
    if inputs.taxable_income <= threshold:
        # Below threshold - no limitation
        qbid = qbid_max
    else:
        # Apply phase-out
        # For SSTB portion: phases out entirely
        sstb_qbid = 0.2 * inputs.sstb_income * applicable_rate

        # For non-SSTB: apply wage cap phase-in
        non_sstb_qbi = gross_qbi - inputs.sstb_income
        non_sstb_qbid_max = 0.2 * non_sstb_qbi
        non_sstb_cap = full_cap * (non_sstb_qbi / gross_qbi) if gross_qbi > 0 else 0

        if inputs.taxable_income >= threshold + phase_length:
            # Above phase-out - full limitation
            non_sstb_qbid = min(non_sstb_qbid_max, non_sstb_cap)
        else:
            # In phase-out range
            reduction = reduction_rate * max(0, non_sstb_qbid_max - non_sstb_cap)
            non_sstb_qbid = non_sstb_qbid_max - reduction

        qbid = sstb_qbid + non_sstb_qbid

    # Taxable income cap
    ti_cap = 0.2 * max(0, inputs.taxable_income - inputs.capital_gains)
    final_qbid = max(0, min(qbid, ti_cap))

    return {
        "qbid": final_qbid,
        "gross_qbi": gross_qbi,
        "qbid_max": qbid_max,
        "threshold": threshold,
        "phase_length": phase_length,
        "reduction_rate": reduction_rate,
        "wage_cap": wage_cap,
        "full_cap": full_cap,
        "ti_cap": ti_cap,
        "steps": [
            {"name": "Gross QBI", "value": gross_qbi},
            {"name": "Base QBID (20%)", "value": qbid_max},
            {"name": "Threshold", "value": threshold},
            {"name": "Phase-out Range", "value": phase_length},
            {"name": "Reduction Rate", "value": reduction_rate * 100},
            {"name": "W-2 Wage Cap", "value": full_cap},
            {"name": "TI Cap", "value": ti_cap},
            {"name": "Final QBID", "value": final_qbid},
        ],
        "notes": [
            f"W-2 wage limitation applied: cap is ${full_cap:,.0f}",
            f"Phase-out uses ${phase_length:,} range for {inputs.filing_status}",
            f"SSTB income phases out {reduction_rate*100:.1f}%",
        ]
    }


def compare_calculations(inputs: CalculationComparisonInput) -> CalculationComparisonResult:
    """Run both calculators and compare results."""

    taxsim_result = run_taxsim_calculation(inputs)
    pe_result = run_policyengine_calculation(inputs)

    diff = pe_result["qbid"] - taxsim_result["qbid"]
    diff_pct = (diff / taxsim_result["qbid"] * 100) if taxsim_result["qbid"] > 0 else None

    notes = []
    if abs(diff) > 1:
        if inputs.partnership_s_corp_income > 0 and inputs.w2_wages < inputs.partnership_s_corp_income:
            notes.append(
                "Difference likely due to W-2 wage limitation: TAXSIM doesn't apply it to non-SSTB income"
            )
        if inputs.sstb_income > 0 and inputs.filing_status == "JOINT":
            notes.append(
                "Joint filers: PolicyEngine uses $100k phase-out range vs TAXSIM's $50k"
            )

    return CalculationComparisonResult(
        policyengine_result=pe_result["qbid"],
        taxsim_result=taxsim_result["qbid"],
        difference=diff,
        difference_pct=diff_pct,
        policyengine_steps=pe_result["steps"],
        taxsim_steps=taxsim_result["steps"],
        notes=notes + taxsim_result["notes"] + pe_result["notes"]
    )
