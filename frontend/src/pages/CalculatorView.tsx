import { useState, useCallback } from 'react';

const API_BASE = 'http://localhost:8000';

interface InputDef {
  name: string;
  label: string;
  group: string;
  default: number | boolean;
  type: 'currency' | 'bool';
}

interface OutputDef {
  name: string;
  label: string;
  entity: string;
  primary?: boolean;
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

const OUTPUT_DEFS: OutputDef[] = [
  { name: 'qualified_business_income_deduction', label: 'Qualified Business Income Deduction', entity: 'tax_unit', primary: true },
  { name: 'qualified_business_income', label: 'Non-SSTB qualified business income', entity: 'person' },
  { name: 'sstb_qualified_business_income', label: 'SSTB qualified business income', entity: 'person' },
  { name: 'qbid_amount', label: 'Per-person QBID (before TI cap)', entity: 'person' },
  { name: 'taxable_income_less_qbid', label: 'Taxable income (before QBID)', entity: 'tax_unit' },
  { name: 'adjusted_net_capital_gain', label: 'Adjusted net capital gain', entity: 'tax_unit' },
  { name: 'self_employment_tax_ald_person', label: 'SE tax deduction (QBI reduction)', entity: 'person' },
  { name: 'self_employed_health_insurance_ald_person', label: 'SE health insurance deduction (QBI reduction)', entity: 'person' },
  { name: 'self_employed_pension_contribution_ald_person', label: 'SE pension deduction (QBI reduction)', entity: 'person' },
  { name: 'adjusted_gross_income', label: 'Adjusted gross income', entity: 'tax_unit' },
  { name: 'taxable_income', label: 'Taxable income (after QBID)', entity: 'tax_unit' },
  { name: 'income_tax_before_credits', label: 'Income tax before credits', entity: 'tax_unit' },
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

const formatCurrencyLarge = (val: number) =>
  val.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 });

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

export default function CalculatorView() {
  const buildDefaults = () => {
    const defaults: Record<string, any> = {
      year: 2024,
      filing_status: 'SINGLE',
      state_code: 'TX',
    };
    for (const def of INPUT_DEFS) {
      defaults[def.name] = def.default;
    }
    return defaults;
  };

  const [inputs, setInputs] = useState<Record<string, any>>(buildDefaults);
  const [result, setResult] = useState<CalcResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(['QBI Income Sources']));

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
  }, []);

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/qbi/calculate`, {
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const qbiIncomeRows = getQbiIncomeRows();
  const otherGroups = getGroups();
  const primaryOutput = result ? OUTPUT_DEFS.find((o) => o.primary) : null;

  const qbiDefs = INPUT_DEFS.filter((d) => d.group === 'QBI Income Sources');

  return (
    <div className="h-full flex bg-pe-bg-secondary">
      {/* Left: Inputs */}
      <div className="w-[460px] border-r border-pe-gray-200 bg-white overflow-y-auto flex flex-col">
        <div className="p-5 pb-3 flex-1">
          {/* Filing Status & Year — always visible */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-pe-text-tertiary mb-1">
                Filing status
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
              <label className="block text-xs font-medium text-pe-text-tertiary mb-1">
                Tax year
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
                  <span className="text-right">Amount</span>
                  <span className="text-center">Qualified</span>
                </div>
                {qbiIncomeRows.map(({ income, qualified }) => (
                  <div
                    key={income.name}
                    className="grid grid-cols-[1fr_140px_72px] gap-1 items-center px-3 py-1.5 border-t border-pe-gray-100 hover:bg-pe-gray-50"
                  >
                    <label className="text-sm text-pe-text-primary truncate">{income.label}</label>
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
                        <label className="text-sm text-pe-text-primary">{def.label}</label>
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
                        <span className="text-sm text-pe-text-primary">{def.label}</span>
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
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-red-50 border border-pe-error/20 rounded-pe-lg text-pe-error text-sm">
            {error}
          </div>
        )}

        {result ? (
          <div className="max-w-3xl mx-auto">
            {/* Primary result */}
            {primaryOutput && (
              <div className="mb-8 bg-white rounded-2xl border border-pe-gray-200 p-8 text-center shadow-sm">
                <div className="text-sm text-pe-text-secondary mb-2">{primaryOutput.label}</div>
                <div className="text-5xl font-bold text-pe-teal-500">
                  {typeof result.outputs[primaryOutput.name] === 'number'
                    ? formatCurrencyLarge(result.outputs[primaryOutput.name] as number)
                    : '$0'}
                </div>
                <div className="mt-3 text-sm text-pe-text-tertiary">
                  {result.filing_status.replace(/_/g, ' ').toLowerCase()} &middot; Tax year {result.year}
                </div>
              </div>
            )}

            {/* QBI Breakdown */}
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-pe-text-primary mb-3">QBI computation breakdown</h3>
              <div className="bg-white rounded-pe-lg border border-pe-gray-200 divide-y divide-pe-gray-100">
                {OUTPUT_DEFS.filter((o) => !o.primary).map((outputDef) => {
                  const val = result.outputs[outputDef.name];
                  const isError = typeof val === 'object' && val !== null;
                  const numVal = typeof val === 'number' ? val : 0;
                  const isZero = numVal === 0;
                  return (
                    <div
                      key={outputDef.name}
                      className={`flex items-center justify-between px-5 py-3 ${isZero ? 'opacity-50' : ''}`}
                    >
                      <div>
                        <div className="text-sm text-pe-text-primary">{outputDef.label}</div>
                        <div className="text-xs text-pe-text-tertiary font-mono">{outputDef.name}</div>
                      </div>
                      <div className="text-right">
                        {isError ? (
                          <span className="text-sm text-pe-error">Error</span>
                        ) : (
                          <span className={`text-lg font-semibold tabular-nums ${numVal < 0 ? 'text-pe-error' : 'text-pe-text-primary'}`}>
                            {formatCurrency(numVal)}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Parameters Used */}
            {result.parameters && Object.keys(result.parameters).length > 0 && (
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-pe-text-primary mb-3">
                  Model parameters ({result.year})
                </h3>
                <div className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody className="divide-y divide-pe-gray-100">
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
                </div>
              </div>
            )}

            {/* How it works */}
            <div className="bg-pe-teal-50 rounded-pe-lg border border-pe-teal-200 p-5">
              <h3 className="text-sm font-semibold text-pe-teal-800 mb-2">How this works</h3>
              <p className="text-sm text-pe-teal-700 leading-relaxed">
                This calculator runs a full PolicyEngine US simulation.
                The QBID is computed following IRC &sect;199A: 20% of QBI, subject to
                W-2 wage and property limitations, SSTB phase-out, and capped at
                20% of taxable income less net capital gains.
              </p>
            </div>
          </div>
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
