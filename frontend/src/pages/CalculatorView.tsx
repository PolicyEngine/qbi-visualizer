import { useState, useCallback } from 'react';
import { InfoTooltip } from '../components/InfoTooltip';
import { INPUT_DEFINITIONS, QUALIFIED_FLAG_DEFINITION } from '../data/inputDefinitions';

interface InputDef {
  name: string;
  label: string;
  group: string;
  default: number | boolean;
  type: 'currency' | 'bool';
}

const INPUT_DEFS: InputDef[] = [
  { name: 'self_employment_income', label: 'Self-employment', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'self_employment_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'partnership_s_corp_income', label: 'Partnership / S-corp', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'partnership_s_corp_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'farm_operations_income', label: 'Farm operations', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'farm_operations_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'farm_rent_income', label: 'Farm rental', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'farm_rent_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'rental_income', label: 'Rental', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'rental_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'estate_income', label: 'Estate / trust', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'estate_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'sstb_self_employment_income', label: 'SSTB self-employment income', group: 'SSTB Income', default: 0, type: 'currency' },
  { name: 'sstb_self_employment_income_would_be_qualified', label: 'SSTB SE income is qualified', group: 'SSTB Income', default: true, type: 'bool' },
  { name: 'w2_wages_from_qualified_business', label: 'W-2 wages from qualified business', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'unadjusted_basis_qualified_property', label: 'UBIA of qualified property', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'sstb_w2_wages_from_qualified_business', label: 'SSTB allocable W-2 wages', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'sstb_unadjusted_basis_qualified_property', label: 'SSTB allocable UBIA', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'qualified_reit_and_ptp_income', label: 'Qualified REIT dividends & PTP income', group: 'REIT & PTP', default: 0, type: 'currency' },
  { name: 'employment_income', label: 'W-2 employment income', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'long_term_capital_gains', label: 'Long-term capital gains', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'short_term_capital_gains', label: 'Short-term capital gains', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'qualified_dividend_income', label: 'Qualified dividends', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'taxable_interest_income', label: 'Taxable interest', group: 'Other Income', default: 0, type: 'currency' },
];

function getQbiIncomeRows() {
  const incomeVars = INPUT_DEFS.filter(
    (d) => d.group === 'QBI Income Sources' && d.type === 'currency'
  );
  return incomeVars.map((inc) => {
    const qualifiedName = inc.name + '_would_be_qualified';
    return { income: inc, qualified: INPUT_DEFS.find((d) => d.name === qualifiedName) };
  });
}

interface GroupDef {
  name: string;
  inputs: InputDef[];
}

function getGroups(): GroupDef[] {
  const groups: GroupDef[] = [];
  const seen = new Set<string>();
  for (const def of INPUT_DEFS) {
    if (def.group === 'QBI Income Sources') continue;
    if (!seen.has(def.group)) {
      seen.add(def.group);
      groups.push({ name: def.group, inputs: [] });
    }
    groups.find((g) => g.name === def.group)!.inputs.push(def);
  }
  return groups;
}

const formatCurrency = (val: number) =>
  val.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

const Chevron = ({ open }: { open: boolean }) => (
  <svg
    className={`w-4 h-4 text-pe-text-tertiary transition-transform ${open ? 'rotate-90' : ''}`}
    fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
  </svg>
);

function countNonDefault(inputs: Record<string, any>, defs: InputDef[]): number {
  return defs.filter((d) => {
    const val = inputs[d.name];
    if (d.type === 'currency') return val !== 0 && val !== undefined;
    return val !== d.default && val !== undefined;
  }).length;
}

interface CalcResult {
  outputs: Record<string, number | { error: string }>;
  parameters: Record<string, number>;
  year: number;
  filing_status: string;
}

type Outputs = CalcResult['outputs'];

const num = (outputs: Outputs, name: string): number => {
  const v = outputs[name];
  return typeof v === 'number' ? v : 0;
};

interface StageRow {
  name?: string; // PolicyEngine variable name (omitted for computed rows)
  label: string;
  formLine?: string; // e.g. "Form 8995 L10"
  value: number;
  negative?: boolean; // Display with leading minus
  emphasis?: boolean; // Render as a final/result row
}

interface Stage {
  id: string;
  title: string;
  caption?: string;
  total?: number;
  totalLabel?: string;
  rows: StageRow[];
}

function buildStages(outputs: Outputs): Stage[] {
  const nonSstb = num(outputs, 'qualified_business_income');
  const sstb = num(outputs, 'sstb_qualified_business_income');
  const totalQbi = nonSstb + sstb;
  const reitPtp = num(outputs, 'qualified_reit_and_ptp_income');
  const seTax = num(outputs, 'self_employment_tax_ald_person');
  const seHealth = num(outputs, 'self_employed_health_insurance_ald_person');
  const sePension = num(outputs, 'self_employed_pension_contribution_ald_person');
  const qbidAmount = num(outputs, 'qbid_amount');
  const tiBefore = num(outputs, 'taxable_income_less_qbid');
  const netCapGain = num(outputs, 'adjusted_net_capital_gain');

  // Form 8995 derived values
  const qbiComponentMax = 0.20 * Math.max(0, totalQbi); // L5 if no caps
  const reitPtpComponent = 0.20 * Math.max(0, reitPtp); // L9
  const tiLessCapGain = Math.max(0, tiBefore - netCapGain); // L13
  const incomeLimit = 0.20 * tiLessCapGain; // L14
  const finalQbid = Math.min(qbidAmount, incomeLimit); // L15

  // Detect whether wage caps or SSTB phase-out reduced qbid_amount below
  // 20% × Total QBI (plus the REIT/PTP component, which has no cap).
  const unconstrainedQbi = qbiComponentMax + reitPtpComponent;
  const reductionFromCaps = Math.max(0, unconstrainedQbi - qbidAmount);

  return [
    {
      id: 'qbi-buildup',
      title: 'Qualified business income',
      caption: 'Per-person QBI components after SE-tax / health / retirement allocations',
      total: totalQbi,
      totalLabel: 'Total QBI (L4)',
      rows: [
        { name: 'qualified_business_income', label: 'Non-SSTB QBI', formLine: 'Form 8995 L2 (non-SSTB)', value: nonSstb },
        { name: 'sstb_qualified_business_income', label: 'SSTB QBI', formLine: 'Form 8995-A Part I (SSTB)', value: sstb },
        { name: 'self_employment_tax_ald_person', label: 'SE tax deduction (allocable)', value: seTax, negative: true },
        { name: 'self_employed_health_insurance_ald_person', label: 'SE health insurance (allocable)', value: seHealth, negative: true },
        { name: 'self_employed_pension_contribution_ald_person', label: 'SE retirement contribution (allocable)', value: sePension, negative: true },
      ],
    },
    {
      id: 'qbi-components',
      title: 'QBI components (Form 8995 L5 + L9)',
      caption: '20% applied to Total QBI and to REIT/PTP income; per-business wage/UBIA caps and SSTB phase-out reduce the QBI side above the threshold (Form 8995-A Part II/III)',
      rows: [
        { label: '20% × Total QBI (no limits)', formLine: 'Form 8995 L5', value: qbiComponentMax },
        ...(reductionFromCaps > 0
          ? [{ label: '− Wage/UBIA cap and SSTB phase-out (§199A(b)(2), (d)(3))', value: reductionFromCaps, negative: true } as StageRow]
          : []),
        { name: 'qualified_reit_and_ptp_income', label: 'Qualified REIT/PTP income', formLine: 'Form 8995 L6', value: reitPtp },
        { label: '20% × REIT/PTP = REIT/PTP component', formLine: 'Form 8995 L9', value: reitPtpComponent },
        { name: 'qbid_amount', label: 'QBI deduction before income limit', formLine: 'Form 8995 L10', value: qbidAmount, emphasis: true },
      ],
    },
    {
      id: 'min-comparison',
      title: 'Income limit and final QBID',
      caption: 'Form 8995 Lines 11–15 / Form 8995-A Part IV',
      rows: [
        { name: 'taxable_income_less_qbid', label: 'Taxable income (before QBID)', formLine: 'Form 8995 L11', value: tiBefore },
        { name: 'adjusted_net_capital_gain', label: 'Net capital gain + qualified dividends', formLine: 'Form 8995 L12', value: netCapGain },
        { label: 'TI − net capital gain', formLine: 'Form 8995 L13', value: tiLessCapGain },
        { label: '20% × (TI − net capital gain) = income limit', formLine: 'Form 8995 L14', value: incomeLimit },
        { label: 'Final QBID = min(QBI deduction, income limit)', formLine: 'Form 8995 L15', value: finalQbid, emphasis: true },
      ],
    },
    {
      id: 'tax-impact',
      title: 'Tax impact',
      caption: 'How the QBID flows through to the final tax bill',
      rows: [
        { name: 'adjusted_gross_income', label: 'Adjusted gross income', value: num(outputs, 'adjusted_gross_income') },
        { name: 'taxable_income', label: 'Taxable income (after QBID)', value: num(outputs, 'taxable_income') },
        { name: 'income_tax_before_credits', label: 'Income tax before credits', value: num(outputs, 'income_tax_before_credits') },
      ],
    },
  ];
}

// =====================================================================
// BoxLineDiagram — flowchart of the §199A computation graph
// =====================================================================

interface DiagramBox {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  value?: number;
  valueFormat?: 'currency' | 'percent';
  formLine?: string;
  kind: 'input' | 'op' | 'final';
  binds?: boolean;
  subtitle?: string | string[]; // small line(s) below the value
}

type BoxSide = 'top' | 'right' | 'bottom' | 'left';

interface DiagramEdge {
  from: string;
  to: string;
  op?: string; // optional inline label, e.g. "×0.20", "−", "MIN"
  // Anchor sides default to bottom (exit) → top (enter) for top-down
  // flow. Override when an edge crosses zones and the standard anchors
  // would push the line through unrelated boxes.
  exitSide?: BoxSide;
  enterSide?: BoxSide;
}

function BoxLineDiagram({
  outputs,
  inputs,
  parameters,
  stale,
}: {
  outputs: Outputs;
  inputs: Record<string, any>;
  parameters?: Record<string, number>;
  stale?: boolean;
}) {
  const nonSstb = num(outputs, 'qualified_business_income');
  const sstb = num(outputs, 'sstb_qualified_business_income');
  const totalQbi = nonSstb + sstb;
  // REIT/PTP is a pure input passthrough — read it from inputs directly
  // so the box reflects what the user typed without waiting for a
  // calculation round-trip.
  const reitPtp = Number(inputs['qualified_reit_and_ptp_income'] ?? 0);
  const qbidAmount = num(outputs, 'qbid_amount');
  const tiBefore = num(outputs, 'taxable_income_less_qbid');
  const netCapGain = num(outputs, 'adjusted_net_capital_gain');

  const qbiComponentMax = 0.20 * Math.max(0, totalQbi);
  const reitPtpComponent = 0.20 * Math.max(0, reitPtp);
  const tiLessCapGain = Math.max(0, tiBefore - netCapGain);
  const incomeLimit = 0.20 * tiLessCapGain;
  const finalQbid = Math.min(qbidAmount, incomeLimit);
  const reitPtpComponentValue = reitPtpComponent;
  const businessComponents = Math.max(0, qbidAmount - reitPtpComponentValue);
  const reductionFromCaps = Math.max(0, qbiComponentMax - businessComponents);
  // Treat sub-dollar deltas as floating-point noise rather than a real cap.
  const meaningfulReduction = reductionFromCaps >= 1;
  // Don't mark anything as binding when both candidates are zero (stale state).
  const hasOutputs = qbidAmount > 0 || incomeLimit > 0;
  const qbiDeductionBinds = hasOutputs && qbidAmount <= incomeLimit;
  const incomeLimitBinds = hasOutputs && !qbiDeductionBinds;

  // Build raw-input feeders aligned to Form 8995 Line 1 / Line 6 / Line 12.
  // Only non-zero, qualified inputs render. Each feeder hangs above its
  // target QBI bucket and is connected by an arrow.
  type Feeder = { name: string; label: string; value: number; formLine: string };
  const isQualified = (name: string) =>
    inputs[`${name}_would_be_qualified`] === undefined ||
    inputs[`${name}_would_be_qualified`] === true;
  const inputVal = (name: string): number => Number(inputs[name] ?? 0);

  const feedersFor = (target: 'non_sstb' | 'sstb' | 'cap_gain' | 'ti'): Feeder[] => {
    if (target === 'non_sstb') {
      return [
        { name: 'self_employment_income', label: 'Self-employment', formLine: 'L1' },
        { name: 'partnership_s_corp_income', label: 'Partnership / S-corp', formLine: 'L1' },
        { name: 'farm_operations_income', label: 'Farm operations', formLine: 'L1' },
        { name: 'farm_rent_income', label: 'Farm rental', formLine: 'L1' },
        { name: 'rental_income', label: 'Rental', formLine: 'L1' },
        { name: 'estate_income', label: 'Estate / trust', formLine: 'L1' },
      ]
        .filter((f) => inputVal(f.name) > 0 && isQualified(f.name))
        .map((f) => ({ ...f, value: inputVal(f.name) }));
    }
    if (target === 'sstb') {
      return [{ name: 'sstb_self_employment_income', label: 'SSTB SE income', formLine: 'L1 (SSTB)' }]
        .filter((f) => inputVal(f.name) > 0 && isQualified(f.name))
        .map((f) => ({ ...f, value: inputVal(f.name) }));
    }
    if (target === 'cap_gain') {
      return [
        { name: 'long_term_capital_gains', label: 'Long-term capital gains', formLine: 'L12' },
        { name: 'qualified_dividend_income', label: 'Qualified dividends', formLine: 'L12' },
      ]
        .filter((f) => inputVal(f.name) > 0)
        .map((f) => ({ ...f, value: inputVal(f.name) }));
    }
    // ti feeders — non-QBI income that flows into TI alongside the
    // QBI/cap-gain pieces already shown elsewhere in the diagram.
    return [
      { name: 'employment_income', label: 'W-2 wages', formLine: '1040 L1' },
      { name: 'taxable_interest_income', label: 'Interest', formLine: '1040 L2b' },
      { name: 'short_term_capital_gains', label: 'Short-term gains', formLine: 'Sch D' },
    ]
      .filter((f) => inputVal(f.name) > 0)
      .map((f) => ({ ...f, value: inputVal(f.name) }));
  };

  const nonSstbFeeders = feedersFor('non_sstb');
  const sstbFeeders = feedersFor('sstb');
  const capGainFeeders = feedersFor('cap_gain');
  const tiFeeders = feedersFor('ti');

  // Wage / UBIA cap area (§199A(b)(2)(B)). Each input has a FIXED grid
  // position (col 0 = wages, col 1 = property; row 0 = total, row 1 =
  // SSTB allocable) so users see consistent placement across edits.
  // Only W-2 wages renders by default; the others appear when non-zero.
  // If the right column has no entries, the grid collapses to one
  // column to avoid an empty half.
  type WageInput = {
    name: string;
    label: string;
    value: number;
    col: 0 | 1;
    row: 0 | 1;
    alwaysShow?: boolean;
  };
  const wageCapInputs: WageInput[] = ([
    { name: 'w2_wages_from_qualified_business', label: 'W-2 wages', col: 0 as const, row: 0 as const, alwaysShow: true },
    { name: 'unadjusted_basis_qualified_property', label: 'UBIA', col: 1 as const, row: 0 as const },
    { name: 'sstb_w2_wages_from_qualified_business', label: 'SSTB W-2', col: 0 as const, row: 1 as const },
    { name: 'sstb_unadjusted_basis_qualified_property', label: 'SSTB UBIA', col: 1 as const, row: 1 as const },
  ] as Omit<WageInput, 'value'>[])
    .map((f) => ({ ...f, value: inputVal(f.name) }))
    .filter((f) => f.alwaysShow || f.value > 0);
  // Wage cap is a COMPUTED value, not a raw input — so when the result
  // is stale (user edited inputs after a calc), zero it out alongside
  // the other computed boxes. The W-2 / UBIA feeder boxes still show
  // current input values because they're inputs.
  const w2 = stale ? 0 : inputVal('w2_wages_from_qualified_business');
  const ubiaVal = stale ? 0 : inputVal('unadjusted_basis_qualified_property');
  const wageCap = stale ? 0 : Math.max(0.50 * w2, 0.25 * w2 + 0.025 * ubiaVal);
  const showWageCap = true; // always show the wage / UBIA cap path

  // §199A(b)(3)(B) phase-in: between threshold and threshold + length the
  // wage cap binds proportionally. reduction_rate = (TI − threshold) /
  // length, clamped to [0, 1]. Computed from server-supplied parameters
  // when available; otherwise undefined (no phase-in viz).
  const threshold = parameters?.phase_out_start;
  const phaseInLength = parameters?.phase_out_length;
  const reductionRate =
    threshold !== undefined && phaseInLength !== undefined && phaseInLength > 0
      ? Math.max(0, Math.min(1, (tiBefore - threshold) / phaseInLength))
      : undefined;
  const inPhaseIn = reductionRate !== undefined && reductionRate > 0 && reductionRate < 1;
  const aboveRange = reductionRate !== undefined && reductionRate >= 1;
  // The wage cap is "actually contributing" when the reduction is larger
  // than what SSTB phase-out alone could explain (max SSTB reduction =
  // 20% × SSTB QBI when applicable_rate hits 0). Below threshold this
  // is always false, so the dashed cap edge stays hidden.
  const sstbMaxPossibleReduction = 0.20 * Math.max(0, sstb);
  const wageCapActuallyBinds =
    showWageCap && wageCap < qbiComponentMax && reductionFromCaps > sstbMaxPossibleReduction + 1;

  // Vertical space the feeder area needs (max stack height across columns).
  // Box height needs to clear both the label (y=18 baseline) and the value
  // (y=36 baseline) — at 36 the value glyphs were spilling past the bottom.
  const FEEDER_BH = 46;
  const FEEDER_GAP = 8;
  const BW = 150; // box width
  const BH = 52;  // box height
  // Wage / UBIA cap inputs render in a horizontal 2-col grid so users
  // see them as separate parameters feeding one formula, not a stacked
  // chain. With 1 input it's 1 box wide; with 2-4 it's 2 boxes wide.
  const WAGE_HGAP = 10;
  // Determine which input columns / rows are actually populated so the
  // input grid collapses cleanly. The alternative boxes (50% × W-2 and
  // 25% W-2 + 2.5% UBIA) are always rendered side-by-side, so the area
  // is always at least 2-cells wide regardless of how many inputs there
  // are — otherwise the right alternative box would collide with the
  // main diagram's level1 row.
  const wageCol1Active = wageCapInputs.some((f) => f.col === 1);
  const wageRow1Active = wageCapInputs.some((f) => f.row === 1);
  const wageRows = wageRow1Active ? 2 : 1;
  const ALTS_WIDTH = 2 * BW + WAGE_HGAP;
  const inputGridWidth = (wageCol1Active ? 2 : 1) * BW + (wageCol1Active ? WAGE_HGAP : 0);
  const wageGridWidth = showWageCap ? Math.max(ALTS_WIDTH, inputGridWidth) : 0;

  const maxFeederStack = Math.max(
    nonSstbFeeders.length,
    sstbFeeders.length,
    capGainFeeders.length,
    tiFeeders.length,
    wageRows,
  );
  const feederAreaH = maxFeederStack > 0 ? maxFeederStack * (FEEDER_BH + FEEDER_GAP) + 24 : 0;

  // Three vertical zones, left to right:
  //   1. Income-limit zone — TI / cap gain → ti_less_cg → income limit.
  //      Always shown; two boxes wide so it matches the standard zone.
  //   2. Wage-cap zone — only when showWageCap. Houses W-2 / UBIA feeders,
  //      the 50%/25%+UBIA alternatives, the wage cap node, and the
  //      Excess / Phase-in stack below it.
  //   3. QBI zone — non-SSTB / SSTB / REIT-PTP and everything that flows
  //      into qbi_deduction.
  // Putting both QBID limitations (income limit, wage cap) to the LEFT of
  // the QBI side mirrors how they constrain the deduction in §199A.
  const ZONE_GAP = 30;
  const INCOME_WIDTH = 2 * BW + WAGE_HGAP;
  const INCOME_X = 10;
  const WAGE_X = INCOME_X + INCOME_WIDTH + ZONE_GAP;
  const WAGE_CAP_X = showWageCap ? WAGE_X + (wageGridWidth - BW) / 2 : WAGE_X;
  // SHIFT is the extra offset applied to the historical "10 + SHIFT" QBI
  // box positions so the QBI zone starts where the income / wage zones
  // leave off.
  const QBI_X = showWageCap
    ? WAGE_X + wageGridWidth + ZONE_GAP
    : INCOME_X + INCOME_WIDTH + ZONE_GAP;
  const SHIFT = QBI_X - 10;
  // When the phase-in math binds, an explicit "After phase-in" box (L26)
  // sits between L5 and qbi_deduction so users can see the post-reduction
  // value as a node, not a subtitle. That insertion adds one vertical
  // level of spacing; downstream levels shift down accordingly.
  const showAfterPhaseInBox = inPhaseIn && wageCapActuallyBinds;
  // Above the phase-in range the wage cap fully replaces L5; surface the
  // post-cap value as its own node too so both reduction paths (phase-in
  // and above-range full cap) land in a labeled box rather than an L5
  // subtitle. Both cases reuse the qbi_comp_after id.
  const showAfterCapBox = wageCapActuallyBinds && aboveRange;
  const showQbiAfterBox = showAfterPhaseInBox || showAfterCapBox;
  const phaseInExtraSpace = showQbiAfterBox ? 90 : 0;
  const level0Y = feederAreaH + 10;
  const level1Y = level0Y + 120;
  const level2Y = level1Y + 120;
  const afterPhaseInY = level2Y + 130;
  const level3Y = level2Y + 130 + phaseInExtraSpace;
  const level4Y = level3Y + 130;
  const H = level4Y + 80;

  const boxes: DiagramBox[] = [
    // Level 0 — Income-limit chain (TI / cap gain) on the LEFT, QBI
    // buckets on the RIGHT. The income-limit chain mirrors the wage-cap
    // chain that lives further left, so both QBID limitations sit on the
    // same side of the diagram.
    // Income zone (far left). cap_gain sits on the OUTER edge and TI on
    // the INNER edge so TI is closest to the wage / phase-in zone — the
    // TI → Phase-in rate edge can hop directly across the zone gap.
    { id: 'cap_gain', x: INCOME_X, y: level0Y, w: BW, h: BH, label: 'Net capital gain', value: netCapGain, formLine: 'L12', kind: 'input' },
    { id: 'ti', x: INCOME_X + BW + WAGE_HGAP, y: level0Y, w: BW, h: BH, label: 'Taxable income', value: tiBefore, formLine: 'L11', kind: 'input' },
    // QBI zone (right)
    { id: 'non_sstb', x: 10 + SHIFT, y: level0Y, w: BW, h: BH, label: 'Non-SSTB QBI', value: nonSstb, formLine: 'L2', kind: 'input' },
    { id: 'sstb', x: 170 + SHIFT, y: level0Y, w: BW, h: BH, label: 'SSTB QBI', value: sstb, formLine: 'L2 (SSTB)', kind: 'input' },
    { id: 'reit_ptp', x: 330 + SHIFT, y: level0Y, w: BW, h: BH, label: 'REIT/PTP income', value: reitPtp, formLine: 'L6', kind: 'input' },
    // Level 1 — first ops
    { id: 'ti_less_cg', x: INCOME_X + (INCOME_WIDTH - BW) / 2, y: level1Y, w: BW, h: BH, label: 'TI − net cap gain', value: tiLessCapGain, formLine: 'L13', kind: 'op' },
    { id: 'total_qbi', x: 90 + SHIFT, y: level1Y, w: BW, h: BH, label: 'Total QBI', value: totalQbi, formLine: 'L4', kind: 'op' },
    // Level 2 — × 20%
    {
      id: 'qbi_comp_max',
      x: 90 + SHIFT,
      y: level2Y,
      w: BW,
      h: meaningfulReduction && !showQbiAfterBox ? 68 : BH,
      label: '20% × Total QBI',
      value: qbiComponentMax,
      formLine: 'L5',
      kind: 'op',
      // When wage caps and/or SSTB phase-out trim the QBI side before it
      // merges into QBI deduction, the post-cap value is shown either as
      // a subtitle here (SSTB-only reduction cases) or as a dedicated
      // qbi_comp_after box downstream (phase-in or above-range full
      // cap). Avoid double-display.
      subtitle:
        meaningfulReduction && !showQbiAfterBox
          ? `→ ${formatCurrency(businessComponents)} after caps`
          : undefined,
    },
    { id: 'reit_ptp_comp', x: 330 + SHIFT, y: level2Y, w: BW, h: BH, label: '20% × REIT/PTP', value: reitPtpComponent, formLine: 'L9', kind: 'op' },
    { id: 'income_limit', x: INCOME_X + (INCOME_WIDTH - BW) / 2, y: level2Y, w: BW, h: BH, label: 'Income limit', value: incomeLimit, formLine: 'L14', kind: 'op', binds: incomeLimitBinds },
    // Level 3 — sum into QBI deduction
    {
      id: 'qbi_deduction',
      x: 210 + SHIFT,
      y: level3Y,
      w: BW,
      h: BH,
      label: 'QBI deduction',
      value: qbidAmount,
      formLine: 'L10',
      kind: 'op',
      binds: qbiDeductionBinds,
    },
    // Level 4 — final min
    // Center final_qbid between income_limit (left zone) and qbi_deduction
    // (right zone) since it MIN's the two.
    {
      id: 'final_qbid',
      x: (INCOME_X + INCOME_WIDTH / 2 + 210 + SHIFT + BW / 2) / 2 - 90,
      y: level4Y,
      w: 180,
      h: 60,
      label: 'Final QBID',
      value: finalQbid,
      formLine: 'L15',
      kind: 'final',
    },
  ];

  // Add feeder boxes (non-zero raw inputs) above their target QBI bucket.
  // Bottom-align: single feeders sit just above the target rather than
  // floating at the top of the feeder area.
  const addFeederColumn = (feeders: Feeder[], targetX: number) => {
    const offset = maxFeederStack - feeders.length; // empty rows above
    feeders.forEach((f, i) => {
      boxes.push({
        id: `feeder_${f.name}`,
        x: targetX,
        y: 10 + (offset + i) * (FEEDER_BH + FEEDER_GAP),
        w: BW,
        h: FEEDER_BH,
        label: f.label,
        value: f.value,
        formLine: f.formLine,
        kind: 'input',
      });
    });
  };
  addFeederColumn(capGainFeeders, INCOME_X);
  addFeederColumn(tiFeeders, INCOME_X + BW + WAGE_HGAP);
  addFeederColumn(nonSstbFeeders, 10 + SHIFT);
  addFeederColumn(sstbFeeders, 170 + SHIFT);
  // Wage cap inputs sit in fixed grid positions: col 0 = wages, col 1
  // = property; row 0 = total, row 1 = SSTB allocable. Each input
  // always lands in its own slot regardless of which others are entered.
  if (showWageCap) {
    const offsetRows = maxFeederStack - wageRows;
    wageCapInputs.forEach((f) => {
      boxes.push({
        id: `feeder_${f.name}`,
        x: WAGE_X + f.col * (BW + WAGE_HGAP),
        y: 10 + (offsetRows + f.row) * (FEEDER_BH + FEEDER_GAP),
        w: BW,
        h: FEEDER_BH,
        label: f.label,
        value: f.value,
        kind: 'input',
      });
    });
  }

  // Tag the Non-SSTB QBI box with the SE-tax / health / retirement
  // allocation reduction (when gross > net) so the shrinkage is visible
  // without overloading individual feeder edges.
  const grossNonSstb = nonSstbFeeders.reduce((s, f) => s + f.value, 0);
  if (grossNonSstb > nonSstb && nonSstb > 0) {
    const nonSstbBox = boxes.find((b) => b.id === 'non_sstb')!;
    nonSstbBox.subtitle = `−${formatCurrency(grossNonSstb - nonSstb)} SE alloc.`;
    nonSstbBox.h = 68;
  }
  const grossSstb = sstbFeeders.reduce((s, f) => s + f.value, 0);
  if (grossSstb > sstb && sstb > 0) {
    const sstbBox = boxes.find((b) => b.id === 'sstb')!;
    sstbBox.subtitle = `−${formatCurrency(grossSstb - sstb)} SE alloc.`;
    sstbBox.h = 68;
  }

  // Wage cap node (informational): shows the computed wage / UBIA cap
  // value. It connects to L10 with a dashed "caps" edge — the cap only
  // actually binds above the threshold, but surfacing it always lets
  // users see how their W-2 / UBIA inputs relate to the deduction.
  const wageOnly = 0.50 * w2;
  const wageUbia = 0.25 * w2 + 0.025 * ubiaVal;
  const wageOnlyWins = wageOnly >= wageUbia;
  if (showWageCap) {
    // Form 8995-A Part II breaks the wage cap into two explicit alternatives
    // — Line 13 (50% × W-2) and Line 16 (25% × W-2 + 2.5% × UBIA). Render
    // them as their own boxes so users see the comparison upstream of the
    // max(). A small "max" annotation sits on the merge.
    const wageCapStatusLine: string | undefined = (() => {
      if (reductionRate === undefined) {
        return wageCapActuallyBinds ? undefined : '(not binding here)';
      }
      if (reductionRate === 0) return '(below threshold — cap not applied)';
      if (inPhaseIn) return undefined; // shown in dedicated phase-in box
      if (aboveRange && wageCap < qbiComponentMax) return '(above range — full cap)';
      if (wageCap >= qbiComponentMax) return '(not binding here)';
      return undefined;
    })();

    // Two alternative boxes positioned at level1Y (between feeders above
    // and the Wage cap node at level2Y).
    boxes.push({
      id: 'wage_alt_50',
      x: WAGE_X,
      y: level1Y,
      w: BW,
      h: 64,
      label: 'Wage-only',
      value: wageOnly,
      formLine: 'L13',
      kind: 'op',
      binds: wageOnlyWins && wageCap > 0,
      subtitle: ['50% × W-2'],
    });
    boxes.push({
      id: 'wage_alt_25_ubia',
      x: WAGE_X + BW + WAGE_HGAP,
      y: level1Y,
      w: BW,
      h: 64,
      label: 'Wage + capital',
      value: wageUbia,
      formLine: 'L16',
      kind: 'op',
      binds: !wageOnlyWins && wageCap > 0,
      subtitle: ['25% × W-2 + 2.5% × UBIA'],
    });

    // Status lines longer than ~22 chars overflow at fontSize 9, so split
    // an em-dash status into two lines and grow the box accordingly.
    const wageCapStatusLines: string[] | undefined = (() => {
      if (!wageCapStatusLine) return undefined;
      if (wageCapStatusLine.length <= 24) return [wageCapStatusLine];
      const dashIdx = wageCapStatusLine.indexOf(' — ');
      if (dashIdx < 0) return [wageCapStatusLine];
      return [
        wageCapStatusLine.slice(0, dashIdx + 2),
        wageCapStatusLine.slice(dashIdx + 3),
      ];
    })();
    const wageCapH = !wageCapStatusLines
      ? BH
      : wageCapStatusLines.length > 1
      ? 76
      : 64;
    boxes.push({
      id: 'wage_cap',
      x: WAGE_CAP_X,
      y: level2Y,
      w: BW,
      h: wageCapH,
      label: 'Wage cap',
      value: wageCap,
      formLine: 'L17',
      kind: 'op',
      subtitle: wageCapStatusLines,
    });

    // Phase-in stack — three vertically stacked boxes that mirror
    // Form 8995-A Part III line by line:
    //   Excess        (L19 − L20): how much QBID exceeds the wage cap
    //   Phase-in rate (L24/L26)  : (TI − threshold) / phase-in length
    //   Reduction     (L25/L27)  : Excess × Phase-in rate
    // The Reduction box's value is what gets subtracted from L5
    // (qbi_comp_max), so the edge label there just reads "−$X".
    if (inPhaseIn && reductionRate !== undefined) {
      const excess = Math.max(0, qbiComponentMax - wageCap);
      const excessY = level2Y + wageCapH + 24;
      const phaseY = excessY + 64 + 24;
      boxes.push({
        id: 'phase_in_excess',
        x: WAGE_CAP_X,
        y: excessY,
        w: BW,
        h: 64,
        label: 'Excess',
        value: excess,
        formLine: 'L21',
        kind: 'op',
        subtitle: ['L5 − wage cap'],
      });
      boxes.push({
        id: 'phase_in_rate',
        x: WAGE_CAP_X,
        y: phaseY,
        w: BW,
        h: 80,
        label: 'Phase-in rate',
        value: reductionRate * 100,
        valueFormat: 'percent',
        formLine: 'L23',
        kind: 'op',
        subtitle: [
          `TI ${formatCurrency(tiBefore)}`,
          `into ${formatCurrency(threshold!)}–${formatCurrency(threshold! + phaseInLength!)}`,
        ],
      });
    }
  }

  // After-cap / after-phase-in box: the reduced QBI component value
  // that flows into qbi_deduction. Sits directly below L5. In the
  // phase-in case it takes L5 + Phase-in rate as inputs; in the
  // above-range case it takes L5 + Wage cap (smaller of the two). When
  // this box is shown, L5 → qbi_deduction is rerouted through it.
  if (showQbiAfterBox) {
    boxes.push({
      id: 'qbi_comp_after',
      x: 90 + SHIFT,
      y: afterPhaseInY,
      w: BW,
      h: BH,
      label: showAfterPhaseInBox ? 'After phase-in' : 'After cap',
      value: businessComponents,
      formLine: showAfterPhaseInBox ? 'L26' : 'L28',
      kind: 'op',
    });
  }

  const edges: DiagramEdge[] = [
    // Feeders → QBI buckets. Multi-feeder columns get a Σ on the second-
    // and-later edges to mark the merge; the SE-tax allocation reduction
    // shows up as a subtitle on the destination box, not on an edge.
    ...nonSstbFeeders.map((f, i) => ({ from: `feeder_${f.name}`, to: 'non_sstb', op: i > 0 ? 'Σ' : undefined })),
    ...sstbFeeders.map((f) => ({ from: `feeder_${f.name}`, to: 'sstb' })),
    ...capGainFeeders.map((f, i) => ({ from: `feeder_${f.name}`, to: 'cap_gain', op: i > 0 ? 'Σ' : undefined })),
    ...tiFeeders.map((f, i) => ({ from: `feeder_${f.name}`, to: 'ti', op: i > 0 ? 'Σ' : undefined })),
    // Wage cap routing — feeders go through the 50% W-2 and
    // 25% W-2 + 2.5% UBIA alternative boxes (Form 8995-A L13 / L16)
    // before merging at Wage cap (max). SSTB-allocable feeders bypass
    // the alternatives since they only matter for per-bucket caps.
    ...(showWageCap
      ? [
          { from: 'feeder_w2_wages_from_qualified_business', to: 'wage_alt_50' } as DiagramEdge,
          { from: 'feeder_w2_wages_from_qualified_business', to: 'wage_alt_25_ubia' } as DiagramEdge,
          ...(inputVal('unadjusted_basis_qualified_property') > 0
            ? [{ from: 'feeder_unadjusted_basis_qualified_property', to: 'wage_alt_25_ubia' } as DiagramEdge]
            : []),
          { from: 'wage_alt_50', to: 'wage_cap' } as DiagramEdge,
          { from: 'wage_alt_25_ubia', to: 'wage_cap', op: 'max' } as DiagramEdge,
          ...wageCapInputs
            .filter((f) => f.name.startsWith('sstb_'))
            .map((f) => ({ from: `feeder_${f.name}`, to: 'wage_cap' } as DiagramEdge)),
          // Route the dashed cap path through Excess → Phase-in rate
          // when the filer is in the §199A(b)(3)(B) phase-in range so
          // the multiplication that produces the dollar reduction is
          // visible: Excess × rate = the −$X label landing on L5.
          ...(wageCapActuallyBinds && inPhaseIn
            ? [
                // TI is the basis for the phase-in rate ((TI − threshold)
                // / phase-in length). Route the edge from TI's right side
                // into Phase-in rate's left side so it crosses the zone
                // gap directly without grazing other boxes.
                {
                  from: 'ti',
                  to: 'phase_in_rate',
                  exitSide: 'right',
                  enterSide: 'left',
                } as DiagramEdge,
                // Both operands of the L5 − wage_cap subtraction feed
                // the Excess box. L5 (minuend) sits in the QBI zone to
                // the right, so route its arrow into Excess's right
                // side rather than its top. wage_cap (subtrahend) is
                // directly above and uses default top entry with op '−'.
                {
                  from: 'qbi_comp_max',
                  to: 'phase_in_excess',
                  exitSide: 'left',
                  enterSide: 'right',
                } as DiagramEdge,
                { from: 'wage_cap', to: 'phase_in_excess', op: '−' } as DiagramEdge,
                { from: 'phase_in_excess', to: 'phase_in_rate', op: '×' } as DiagramEdge,
                // Phase-in rate × Excess = the reduction landing on the
                // After-phase-in (L26) box, where L5 also flows in as the
                // minuend.
                {
                  from: 'phase_in_rate',
                  to: 'qbi_comp_after',
                  op: `−${formatCurrency(Math.max(0, qbiComponentMax - businessComponents))}`,
                  exitSide: 'right',
                  enterSide: 'left',
                } as DiagramEdge,
              ]
            : showAfterCapBox
            ? [
                // Above the phase-in range, the wage cap fully replaces
                // L5: After-cap = min(L5, wage_cap). Both operands feed
                // the After-cap box from their respective sides.
                {
                  from: 'wage_cap',
                  to: 'qbi_comp_after',
                  op: 'MIN',
                  exitSide: 'right',
                  enterSide: 'left',
                } as DiagramEdge,
              ]
            : []),
        ]
      : []),
    // Level 0 → first ops
    { from: 'non_sstb', to: 'total_qbi' },
    { from: 'sstb', to: 'total_qbi', op: 'Σ' },
    { from: 'ti', to: 'ti_less_cg' },
    { from: 'cap_gain', to: 'ti_less_cg', op: '−' },
    // First ops & REIT/PTP → ×20%
    { from: 'total_qbi', to: 'qbi_comp_max', op: '×0.20' },
    { from: 'reit_ptp', to: 'reit_ptp_comp', op: '×0.20' },
    { from: 'ti_less_cg', to: 'income_limit', op: '×0.20' },
    // QBI components → QBI deduction (sum implied by the merge). When
    // the after-cap / after-phase-in box exists, route L5 through it
    // so the post-reduction value flows in instead of the raw L5.
    ...(showQbiAfterBox
      ? [
          { from: 'qbi_comp_max', to: 'qbi_comp_after' } as DiagramEdge,
          { from: 'qbi_comp_after', to: 'qbi_deduction' } as DiagramEdge,
        ]
      : [{ from: 'qbi_comp_max', to: 'qbi_deduction' } as DiagramEdge]),
    { from: 'reit_ptp_comp', to: 'qbi_deduction', op: 'Σ' },
    // Final min
    // Both branches enter Final QBID from their respective sides so the
    // bezier doesn't overshoot — without side anchors, income_limit's
    // top-down curve dips into the Phase-in rate box.
    { from: 'qbi_deduction', to: 'final_qbid', exitSide: 'left', enterSide: 'right' },
    { from: 'income_limit', to: 'final_qbid', op: 'MIN', exitSide: 'right', enterSide: 'left' },
  ];

  const boxById = (id: string) => boxes.find((b) => b.id === id)!;

  // Anchor a point on a given side of a box, and produce a control-point
  // offset that points OUTWARD from that side (used both for the bezier
  // tangent and for the marker pull-back at the line end).
  const anchorOn = (b: DiagramBox, side: BoxSide) => {
    switch (side) {
      case 'top': return { x: b.x + b.w / 2, y: b.y };
      case 'bottom': return { x: b.x + b.w / 2, y: b.y + b.h };
      case 'left': return { x: b.x, y: b.y + b.h / 2 };
      case 'right': return { x: b.x + b.w, y: b.y + b.h / 2 };
    }
  };
  const outward = (side: BoxSide, mag: number) => {
    switch (side) {
      case 'top': return { x: 0, y: -mag };
      case 'bottom': return { x: 0, y: mag };
      case 'left': return { x: -mag, y: 0 };
      case 'right': return { x: mag, y: 0 };
    }
  };

  // Tighten the viewBox to the actual content extent so the diagram
  // is centered horizontally within whatever container width Tailwind
  // gives us (no empty gutters on the right).
  const contentRight = Math.max(...boxes.map((b) => b.x + b.w));
  const tightW = contentRight + 10;

  return (
    <div className="mb-6 bg-white rounded-pe-lg border border-pe-gray-200 p-4">
      <h3 className="text-sm font-semibold text-pe-text-primary mb-3">Computation graph</h3>
      <svg viewBox={`0 0 ${tightW} ${H}`} className="w-full" preserveAspectRatio="xMidYMid meet">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#9CA3AF" />
          </marker>
          <marker id="arrow-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#319795" />
          </marker>
          <marker id="arrow-amber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#D97706" />
          </marker>
        </defs>

        {/* Edges */}
        {edges.map((e, i) => {
          const from = boxById(e.from);
          const to = boxById(e.to);
          const exitSide: BoxSide = e.exitSide ?? 'bottom';
          const enterSide: BoxSide = e.enterSide ?? 'top';
          const a = anchorOn(from, exitSide);
          const b = anchorOn(to, enterSide);
          // Tangent magnitude scales with edge length so short edges get
          // gentle curves and long ones get pronounced ones. Floor at 40
          // so even tiny edges have a visible bend off the box face.
          const dist = Math.hypot(b.x - a.x, b.y - a.y);
          const mag = Math.max(40, dist * 0.4);
          const o1 = outward(exitSide, mag);
          const o2 = outward(enterSide, mag);
          const cp1 = { x: a.x + o1.x, y: a.y + o1.y };
          const cp2 = { x: b.x + o2.x, y: b.y + o2.y };
          // Pull the line endpoint back from the box edge by 6px in the
          // outward direction so the arrow marker sits flush.
          const pullBack = outward(enterSide, 6);
          const lineEnd = { x: b.x + pullBack.x, y: b.y + pullBack.y };
          const isFinalEdge = e.to === 'final_qbid';
          const isConstraint = e.from === 'wage_cap' || e.from === 'phase_in_rate';
          const stroke = isFinalEdge ? '#319795' : isConstraint ? '#D97706' : '#9CA3AF';
          const marker = isFinalEdge ? 'url(#arrow-teal)' : isConstraint ? 'url(#arrow-amber)' : 'url(#arrow)';
          const opLabelW = e.op && e.op.length > 4 ? Math.max(36, e.op.length * 7) : 36;
          return (
            <g key={i}>
              <path
                d={`M ${a.x} ${a.y} C ${cp1.x} ${cp1.y}, ${cp2.x} ${cp2.y}, ${lineEnd.x} ${lineEnd.y}`}
                stroke={stroke}
                strokeWidth={isFinalEdge ? 2 : 1.5}
                strokeDasharray={isConstraint ? '5 4' : undefined}
                fill="none"
                markerEnd={marker}
                opacity={isFinalEdge ? 1 : 0.85}
              />
              {e.op && (
                <g transform={`translate(${(a.x + b.x) / 2}, ${(a.y + b.y) / 2})`}>
                  <rect x={-opLabelW / 2} y={-9} width={opLabelW} height={18} rx={9} fill="white" stroke="#E2E8F0" strokeWidth={1} />
                  <text x={0} y={4} textAnchor="middle" fontSize="10" fontFamily="ui-monospace, monospace" fill={isConstraint ? '#D97706' : '#4B5563'}>
                    {e.op}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Boxes */}
        {boxes.map((b) => {
          const fill = b.kind === 'final' ? '#319795' : b.binds ? '#E6FFFA' : 'white';
          const stroke = b.kind === 'final' ? '#319795' : b.binds ? '#319795' : '#CBD5E1';
          const labelColor = b.kind === 'final' ? '#FFFFFF' : '#000000';
          const valueColor = b.kind === 'final' ? '#FFFFFF' : b.binds ? '#319795' : '#000000';
          const subColor = b.kind === 'final' ? '#B2F5EA' : '#9CA3AF';
          return (
            <g key={b.id}>
              <rect
                x={b.x}
                y={b.y}
                width={b.w}
                height={b.h}
                rx={6}
                fill={fill}
                stroke={stroke}
                strokeWidth={b.kind === 'final' || b.binds ? 2 : 1}
              />
              <text x={b.x + b.w / 2} y={b.y + 18} textAnchor="middle" fontSize="11" fill={labelColor} fontWeight={b.kind === 'final' ? 600 : 500}>
                {b.label}
                {b.formLine && <tspan dx={4} fontSize="9" fill={subColor} fontFamily="ui-monospace, monospace">{b.formLine}</tspan>}
              </text>
              {b.value !== undefined && (
                <text x={b.x + b.w / 2} y={b.y + 36} textAnchor="middle" fontSize="13" fontWeight={600} fill={valueColor} fontFamily="ui-monospace, monospace">
                  {b.valueFormat === 'percent' ? `${b.value.toFixed(1)}%` : formatCurrency(b.value)}
                </text>
              )}
              {b.subtitle &&
                (Array.isArray(b.subtitle) ? b.subtitle : [b.subtitle]).map((line, i) => {
                  // Status notes wrapped in parens — e.g. "(not binding here)" —
                  // get bolder/darker styling so the user notices them.
                  const isStatus = line.trim().startsWith('(');
                  return (
                    <text
                      key={i}
                      x={b.x + b.w / 2}
                      y={b.y + 52 + i * 11}
                      textAnchor="middle"
                      fontSize="9"
                      fill={isStatus ? '#374151' : '#9CA3AF'}
                      fontWeight={isStatus ? 600 : 400}
                    >
                      {line}
                    </text>
                  );
                })}
              {b.binds && b.kind !== 'final' && (
                <text x={b.x + b.w - 4} y={b.y + 11} textAnchor="end" fontSize="8" fill="#319795" fontWeight={700}>★ BINDS</text>
              )}
            </g>
          );
        })}

      </svg>
    </div>
  );
}

function BreakdownStaged({ outputs }: { outputs: Outputs }) {
  const stages = buildStages(outputs);
  return (
    <div className="mb-6 space-y-4">
      <h3 className="text-sm font-semibold text-pe-text-primary">QBI computation breakdown</h3>
      {stages.map((stage) => (
        <div key={stage.id} className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
          <div className="px-5 py-3 bg-pe-gray-50 border-b border-pe-gray-200 flex items-baseline justify-between gap-4">
            <div>
              <div className="text-sm font-semibold text-pe-text-primary">{stage.title}</div>
              {stage.caption && (
                <div className="text-xs text-pe-text-tertiary mt-0.5">{stage.caption}</div>
              )}
            </div>
            {stage.total !== undefined && (
              <div className="text-right whitespace-nowrap">
                <div className="text-[10px] uppercase tracking-wider text-pe-text-tertiary">{stage.totalLabel ?? 'Total'}</div>
                <div className="text-lg font-semibold tabular-nums text-pe-teal-600">{formatCurrency(stage.total)}</div>
              </div>
            )}
          </div>
          <div className="divide-y divide-pe-gray-100">
            {stage.rows.map((row, idx) => {
              const display = row.negative ? -Math.abs(row.value) : row.value;
              const isZero = row.value === 0;
              const dim = isZero && !row.emphasis;
              return (
                <div
                  key={row.name ?? `computed-${idx}`}
                  className={`flex items-baseline justify-between gap-4 px-5 py-2.5 ${dim ? 'opacity-50' : ''} ${row.emphasis ? 'bg-pe-teal-50/40' : ''}`}
                  title={row.name}
                >
                  <div className="min-w-0">
                    <span className={`text-sm ${row.emphasis ? 'font-semibold' : ''} text-pe-text-primary`}>{row.label}</span>
                    {row.formLine && (
                      <span className="ml-2 text-[10px] text-pe-text-tertiary font-mono">{row.formLine}</span>
                    )}
                  </div>
                  <span className={`tabular-nums whitespace-nowrap ${row.emphasis ? 'text-lg font-semibold text-pe-teal-600' : 'text-base font-medium'} ${!row.emphasis && display < 0 ? 'text-pe-error' : ''} ${!row.emphasis && display >= 0 ? 'text-pe-text-primary' : ''}`}>
                    {display < 0 ? `−${formatCurrency(Math.abs(display))}` : formatCurrency(display)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function CalculatorView() {
  const buildDefaults = () => {
    const defaults: Record<string, any> = {
      year: 2025,
      filing_status: 'SINGLE',
      state_code: 'TX',
    };
    for (const def of INPUT_DEFS) {
      defaults[def.name] = def.default;
    }
    // Realistic seed: a single filer with $100k of non-SSTB self-employment
    // income, below the 2025 threshold ($197,300), so no wage/UBIA cap and
    // no SSTB phase-out — yields ~$18.6k QBID, capped only by taxable income.
    defaults.self_employment_income = 100_000;
    defaults.w2_wages_from_qualified_business = 1_000_000;
    return defaults;
  };

  const [inputs, setInputs] = useState<Record<string, any>>(buildDefaults);
  const [result, setResult] = useState<CalcResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(['QBI Income Sources']));
  const [parametersOpen, setParametersOpen] = useState(false);
  const [resultTab, setResultTab] = useState<'breakdown' | 'diagram'>('diagram');
  // Track whether the user has ever clicked Calculate. Lets us keep the
  // result-panel structure visible after the first calc, even when the
  // user edits inputs and the computed values get cleared.
  const [hasCalculated, setHasCalculated] = useState(false);

  const toggleSection = (name: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const handleChange = useCallback((name: string, value: any) => {
    setInputs((prev) => ({ ...prev, [name]: value }));
    // Stale-result protection: any input change blanks the displayed
    // result until the user hits Calculate again.
    setResult(null);
    setError(null);
  }, []);

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/qbi/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(detail?.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
      setHasCalculated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const qbiIncomeRows = getQbiIncomeRows();
  const otherGroups = getGroups();

  const qbiDefs = INPUT_DEFS.filter((d) => d.group === 'QBI Income Sources');

  return (
    <div className="h-full flex bg-pe-bg-secondary">
      {/* Left: Inputs */}
      <div className="w-[460px] border-r border-pe-gray-200 bg-white overflow-y-auto flex flex-col">
        <div className="p-5 pb-3 flex-1">
          {/* Filing Status & Year — always visible */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="col-span-2">
              <label className="flex items-center text-xs font-medium text-pe-text-tertiary mb-1">
                Filing status
                <InfoTooltip definition={INPUT_DEFINITIONS.filing_status} />
              </label>
              <select
                value={inputs.filing_status}
                onChange={(e) => handleChange('filing_status', e.target.value)}
                className="w-full px-2.5 py-1.5 border border-pe-gray-200 rounded-pe-md text-sm bg-white focus:outline-none focus:ring-1 focus:ring-pe-teal-500"
              >
                <option value="SINGLE">Single</option>
                <option value="JOINT">Married filing jointly</option>
                <option value="SEPARATE">Married filing separately</option>
                <option value="HEAD_OF_HOUSEHOLD">Head of household</option>
                <option value="SURVIVING_SPOUSE">Surviving spouse</option>
              </select>
            </div>
            <div>
              <label className="flex items-center text-xs font-medium text-pe-text-tertiary mb-1">
                Tax year
                <InfoTooltip definition={INPUT_DEFINITIONS.year} />
              </label>
              <select
                value={inputs.year}
                onChange={(e) => handleChange('year', parseInt(e.target.value))}
                className="w-full px-2.5 py-1.5 border border-pe-gray-200 rounded-pe-md text-sm bg-white focus:outline-none focus:ring-1 focus:ring-pe-teal-500"
              >
                {[2024, 2025, 2026].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>

          {/* QBI Income Sources — compact table */}
          <div className="border border-pe-gray-200 rounded-pe-lg mb-2 overflow-hidden">
            <button
              onClick={() => toggleSection('QBI Income Sources')}
              className="w-full flex items-center justify-between px-3 py-2 bg-pe-gray-50 hover:bg-pe-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Chevron open={openSections.has('QBI Income Sources')} />
                <span className="text-xs font-semibold text-pe-text-secondary uppercase tracking-wide">
                  QBI income sources
                </span>
              </div>
              {!openSections.has('QBI Income Sources') && countNonDefault(inputs, qbiDefs) > 0 && (
                <span className="text-xs text-pe-teal-600 font-medium">
                  {countNonDefault(inputs, qbiDefs)} set
                </span>
              )}
            </button>
            {openSections.has('QBI Income Sources') && (
              <div>
                {/* Header row */}
                <div className="grid grid-cols-[1fr_140px_72px] gap-1 px-3 py-1 border-t border-pe-gray-100 text-[10px] text-pe-text-tertiary uppercase tracking-wider">
                  <span>Source</span>
                  <span>Amount</span>
                  <span className="text-center inline-flex items-center justify-center">
                    Qualified
                    <InfoTooltip definition={QUALIFIED_FLAG_DEFINITION} />
                  </span>
                </div>
                {qbiIncomeRows.map(({ income, qualified }) => (
                  <div
                    key={income.name}
                    className="grid grid-cols-[1fr_140px_72px] gap-1 items-center px-3 py-1.5 border-t border-pe-gray-100 hover:bg-pe-gray-50"
                  >
                    <label className="text-sm text-pe-text-primary truncate inline-flex items-center">
                      {income.label}
                      {INPUT_DEFINITIONS[income.name] && <InfoTooltip definition={INPUT_DEFINITIONS[income.name]} />}
                    </label>
                    <div className="relative">
                      <span className="absolute left-2 top-1/2 -translate-y-1/2 text-pe-text-tertiary text-xs">$</span>
                      <input
                        type="number"
                        value={inputs[income.name] ?? 0}
                        onChange={(e) => handleChange(income.name, parseFloat(e.target.value) || 0)}
                        className="w-full pl-5 pr-1.5 py-1 border border-pe-gray-200 rounded text-sm text-right tabular-nums focus:outline-none focus:ring-1 focus:ring-pe-teal-500"
                      />
                    </div>
                    <div className="flex justify-center">
                      {qualified && (
                        <input
                          type="checkbox"
                          checked={inputs[qualified.name] ?? true}
                          onChange={(e) => handleChange(qualified.name, e.target.checked)}
                          title="Qualified business income"
                          className="rounded border-pe-gray-300 text-pe-teal-500 focus:ring-pe-teal-500"
                        />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Other groups as collapsible sections */}
          {otherGroups.map((group) => {
            const isOpen = openSections.has(group.name);
            const currencyInputs = group.inputs.filter((d) => d.type === 'currency');
            const boolInputs = group.inputs.filter((d) => d.type === 'bool');
            const nonDefaultCount = countNonDefault(inputs, group.inputs);

            return (
              <div key={group.name} className="border border-pe-gray-200 rounded-pe-lg mb-2 overflow-hidden">
                <button
                  onClick={() => toggleSection(group.name)}
                  className="w-full flex items-center justify-between px-3 py-2 bg-pe-gray-50 hover:bg-pe-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Chevron open={isOpen} />
                    <span className="text-xs font-semibold text-pe-text-secondary uppercase tracking-wide">
                      {group.name}
                    </span>
                  </div>
                  {!isOpen && nonDefaultCount > 0 && (
                    <span className="text-xs text-pe-teal-600 font-medium">
                      {nonDefaultCount} set
                    </span>
                  )}
                </button>
                {isOpen && (
                  <div className="border-t border-pe-gray-100">
                    {currencyInputs.map((def) => (
                      <div
                        key={def.name}
                        className="grid grid-cols-[1fr_140px] gap-2 items-center px-3 py-1.5 border-t first:border-t-0 border-pe-gray-100 hover:bg-pe-gray-50"
                      >
                        <label className="text-sm text-pe-text-primary inline-flex items-center">
                          {def.label}
                          {INPUT_DEFINITIONS[def.name] && <InfoTooltip definition={INPUT_DEFINITIONS[def.name]} />}
                        </label>
                        <div className="relative">
                          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-pe-text-tertiary text-xs">$</span>
                          <input
                            type="number"
                            value={inputs[def.name] ?? 0}
                            onChange={(e) => handleChange(def.name, parseFloat(e.target.value) || 0)}
                            className="w-full pl-5 pr-1.5 py-1 border border-pe-gray-200 rounded text-sm text-right tabular-nums focus:outline-none focus:ring-1 focus:ring-pe-teal-500"
                          />
                        </div>
                      </div>
                    ))}
                    {boolInputs.map((def) => (
                      <label
                        key={def.name}
                        className="flex items-center gap-2 px-3 py-1.5 border-t border-pe-gray-100 hover:bg-pe-gray-50 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={inputs[def.name] ?? def.default}
                          onChange={(e) => handleChange(def.name, e.target.checked)}
                          className="rounded border-pe-gray-300 text-pe-teal-500 focus:ring-pe-teal-500"
                        />
                        <span className="text-sm text-pe-text-primary inline-flex items-center">
                          {def.label}
                          {def.name.endsWith('_would_be_qualified') && <InfoTooltip definition={QUALIFIED_FLAG_DEFINITION} />}
                        </span>
                      </label>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Sticky calculate button */}
        <div className="sticky bottom-0 bg-white border-t border-pe-gray-200 p-4">
          <button
            onClick={handleCalculate}
            disabled={loading}
            className="w-full py-2.5 bg-pe-teal-500 text-white rounded-pe-lg font-medium hover:bg-pe-teal-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Computing...' : 'Calculate QBID'}
          </button>
        </div>
      </div>

      {/* Right: Results */}
      <div className="flex-1 overflow-y-auto p-8">
        {error && (
          <div className="max-w-6xl mx-auto mb-6 p-4 bg-red-50 border border-pe-error/20 rounded-pe-lg text-pe-error text-sm">
            {error}
          </div>
        )}

        {(result || hasCalculated) ? (
          (() => {
            const isStale = !result;
            const displayOutputs: Outputs = result?.outputs ?? {};
            return (
              <div className="max-w-6xl mx-auto">
                {isStale && (
                  <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-pe-lg text-sm text-amber-800 flex items-center justify-between gap-4">
                    <span>Inputs changed — click <span className="font-semibold">Calculate</span> to refresh the computed values.</span>
                  </div>
                )}

                {/* Tabs: numerical breakdown vs computation graph */}
                <div className="mb-3 flex items-center gap-1 bg-pe-gray-100 p-1 rounded-pe-lg w-fit">
                  {[
                    { id: 'diagram' as const, label: 'Diagram' },
                    { id: 'breakdown' as const, label: 'Breakdown' },
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setResultTab(tab.id)}
                      className={`px-3 py-1.5 rounded-pe-md text-xs font-medium transition-all ${
                        resultTab === tab.id
                          ? 'bg-white text-pe-text-primary shadow-sm'
                          : 'text-pe-text-secondary hover:text-pe-text-primary'
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                {resultTab === 'breakdown' ? (
                  <BreakdownStaged outputs={displayOutputs} />
                ) : (
                  <BoxLineDiagram outputs={displayOutputs} inputs={inputs} parameters={result?.parameters} stale={isStale} />
                )}

                {/* Parameters Used — collapsible (hidden when stale) */}
                {result && result.parameters && Object.keys(result.parameters).length > 0 && (
                  <div className="mb-6 bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
                    <button
                      onClick={() => setParametersOpen((v) => !v)}
                      className="w-full flex items-center justify-between px-5 py-3 bg-pe-gray-50 hover:bg-pe-gray-100 transition-colors text-left"
                    >
                      <div className="flex items-center gap-2">
                        <Chevron open={parametersOpen} />
                        <span className="text-sm font-semibold text-pe-text-primary">
                          Model parameters ({result.year})
                        </span>
                        <span className="text-xs text-pe-text-tertiary">
                          ({Object.keys(result.parameters).length})
                        </span>
                      </div>
                    </button>
                    {parametersOpen && (
                      <table className="w-full text-sm">
                        <tbody className="divide-y divide-pe-gray-100 border-t border-pe-gray-100">
                          {Object.entries(result.parameters).map(([key, val]) => {
                            const isRate = key.includes('rate');
                            const label = key
                              .replace(/_/g, ' ')
                              .replace(/^\w/, (c) => c.toUpperCase());
                            return (
                              <tr key={key}>
                                <td className="px-5 py-2.5 text-pe-text-secondary">{label}</td>
                                <td className="px-5 py-2.5 text-right font-mono text-pe-text-primary">
                                  {isRate ? `${(val * 100).toFixed(1)}%` : formatCurrency(val)}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}
              </div>
            );
          })()
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-pe-teal-50 flex items-center justify-center">
                <svg className="w-8 h-8 text-pe-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-lg font-semibold text-pe-text-primary mb-1">QBID calculator</p>
              <p className="text-sm text-pe-text-secondary">
                Enter your income details on the left and click Calculate to see your
                Qualified Business Income Deduction computed by the PolicyEngine US model.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
