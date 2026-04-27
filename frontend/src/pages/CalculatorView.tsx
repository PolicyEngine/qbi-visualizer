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

// Input definitions matching the backend
const INPUT_DEFS: InputDef[] = [
  { name: 'self_employment_income', label: 'Self-employment income', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'self_employment_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'partnership_s_corp_income', label: 'Partnership / S-corp income', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'partnership_s_corp_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'farm_operations_income', label: 'Farm operations income', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'farm_operations_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'farm_rent_income', label: 'Farm rental income', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'farm_rent_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'rental_income', label: 'Rental income', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'rental_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'estate_income', label: 'Estate / trust income', group: 'QBI Income Sources', default: 0, type: 'currency' },
  { name: 'estate_income_would_be_qualified', label: 'Qualified', group: 'QBI Income Sources', default: true, type: 'bool' },
  { name: 'sstb_self_employment_income', label: 'SSTB self-employment income', group: 'SSTB Income', default: 0, type: 'currency' },
  { name: 'sstb_self_employment_income_would_be_qualified', label: 'SSTB SE income is qualified', group: 'SSTB Income', default: true, type: 'bool' },
  { name: 'business_is_sstb', label: 'Business is SSTB (legacy flag)', group: 'SSTB Income', default: false, type: 'bool' },
  { name: 'w2_wages_from_qualified_business', label: 'W-2 wages from qualified business', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'unadjusted_basis_qualified_property', label: 'UBIA of qualified property', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'sstb_w2_wages_from_qualified_business', label: 'SSTB allocable W-2 wages', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'sstb_unadjusted_basis_qualified_property', label: 'SSTB allocable UBIA', group: 'Wage & Property Limitation', default: 0, type: 'currency' },
  { name: 'qualified_reit_and_ptp_income', label: 'Qualified REIT dividends & PTP income', group: 'REIT & PTP', default: 0, type: 'currency' },
  { name: 'employment_income', label: 'W-2 employment income', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'long_term_capital_gains', label: 'Long-term capital gains', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'short_term_capital_gains', label: 'Short-term capital gains', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'qualified_dividend_income', label: 'Qualified dividend income', group: 'Other Income', default: 0, type: 'currency' },
  { name: 'taxable_interest_income', label: 'Taxable interest income', group: 'Other Income', default: 0, type: 'currency' },
];

const OUTPUT_DEFS: OutputDef[] = [
  { name: 'qualified_business_income_deduction', label: 'Qualified Business Income Deduction', entity: 'tax_unit', primary: true },
  { name: 'qualified_business_income', label: 'Non-SSTB Qualified Business Income', entity: 'person' },
  { name: 'sstb_qualified_business_income', label: 'SSTB Qualified Business Income', entity: 'person' },
  { name: 'qbid_amount', label: 'Per-Person QBID (before TI cap)', entity: 'person' },
  { name: 'taxable_income_less_qbid', label: 'Taxable Income (before QBID)', entity: 'tax_unit' },
  { name: 'adjusted_net_capital_gain', label: 'Adjusted Net Capital Gain', entity: 'tax_unit' },
  { name: 'self_employment_tax_ald_person', label: 'SE Tax Deduction (QBI reduction)', entity: 'person' },
  { name: 'self_employed_health_insurance_ald_person', label: 'SE Health Insurance Deduction (QBI reduction)', entity: 'person' },
  { name: 'self_employed_pension_contribution_ald_person', label: 'SE Pension Deduction (QBI reduction)', entity: 'person' },
  { name: 'adjusted_gross_income', label: 'Adjusted Gross Income', entity: 'tax_unit' },
  { name: 'taxable_income', label: 'Taxable Income (after QBID)', entity: 'tax_unit' },
  { name: 'income_tax_before_credits', label: 'Income Tax Before Credits', entity: 'tax_unit' },
];

// Group inputs for display - pair each currency input with its _would_be_qualified toggle
function getQbiIncomeRows() {
  const incomeVars = INPUT_DEFS.filter(
    (d) => d.group === 'QBI Income Sources' && d.type === 'currency'
  );
  return incomeVars.map((inc) => {
    const qualifiedName = inc.name + '_would_be_qualified';
    return { income: inc, qualified: INPUT_DEFS.find((d) => d.name === qualifiedName) };
  });
}

function getGroups() {
  const groups: { name: string; inputs: InputDef[] }[] = [];
  const seen = new Set<string>();
  for (const def of INPUT_DEFS) {
    if (def.group === 'QBI Income Sources') continue; // handled separately
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

interface CalcResult {
  outputs: Record<string, number | { error: string }>;
  parameters: Record<string, number>;
  year: number;
  filing_status: string;
}

export default function CalculatorView() {
  // Build default inputs
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

  return (
    <div className="h-full flex bg-slate-50">
      {/* Left: Inputs */}
      <div className="w-[420px] border-r border-slate-200 bg-white overflow-y-auto flex flex-col">
        <div className="p-6 flex-1">
          <h2 className="text-lg font-semibold text-slate-900 mb-1">Calculator Inputs</h2>
          <p className="text-sm text-slate-500 mb-6">
            All values flow directly into the PolicyEngine US model.
          </p>

          {/* Filing Status & Year */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                Filing Status
              </label>
              <select
                value={inputs.filing_status}
                onChange={(e) => handleChange('filing_status', e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="SINGLE">Single</option>
                <option value="JOINT">Married Filing Jointly</option>
                <option value="SEPARATE">Married Filing Separately</option>
                <option value="HEAD_OF_HOUSEHOLD">Head of Household</option>
                <option value="SURVIVING_SPOUSE">Surviving Spouse</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                Tax Year
              </label>
              <select
                value={inputs.year}
                onChange={(e) => handleChange('year', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[2024, 2025, 2026].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
          </div>

          {/* QBI Income Sources - paired with qualified toggles */}
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
              QBI Income Sources
            </h3>
            <div className="space-y-3">
              {qbiIncomeRows.map(({ income, qualified }) => (
                <div key={income.name}>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-sm font-medium text-slate-700">{income.label}</label>
                    {qualified && (
                      <label className="flex items-center gap-1.5 text-xs text-slate-500 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={inputs[qualified.name] ?? true}
                          onChange={(e) => handleChange(qualified.name, e.target.checked)}
                          className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        />
                        Qualified
                      </label>
                    )}
                  </div>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
                    <input
                      type="number"
                      value={inputs[income.name] ?? 0}
                      onChange={(e) => handleChange(income.name, parseFloat(e.target.value) || 0)}
                      className="w-full pl-7 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Other input groups */}
          {otherGroups.map((group) => (
            <div key={group.name} className="mb-6">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
                {group.name}
              </h3>
              <div className="space-y-3">
                {group.inputs.map((def) =>
                  def.type === 'currency' ? (
                    <div key={def.name}>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        {def.label}
                      </label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
                        <input
                          type="number"
                          value={inputs[def.name] ?? 0}
                          onChange={(e) => handleChange(def.name, parseFloat(e.target.value) || 0)}
                          className="w-full pl-7 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  ) : (
                    <label
                      key={def.name}
                      className="flex items-center gap-2.5 p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={inputs[def.name] ?? def.default}
                        onChange={(e) => handleChange(def.name, e.target.checked)}
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-700">{def.label}</span>
                    </label>
                  )
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Sticky calculate button */}
        <div className="sticky bottom-0 bg-white border-t border-slate-200 p-4">
          <button
            onClick={handleCalculate}
            disabled={loading}
            className="w-full py-3 bg-slate-900 text-white rounded-lg font-medium hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Computing...' : 'Calculate QBID'}
          </button>
        </div>
      </div>

      {/* Right: Results */}
      <div className="flex-1 overflow-y-auto p-8">
        {error && (
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {result ? (
          <div className="max-w-3xl mx-auto">
            {/* Primary result */}
            {primaryOutput && (
              <div className="mb-8 bg-white rounded-2xl border border-slate-200 p-8 text-center shadow-sm">
                <div className="text-sm text-slate-500 mb-2">{primaryOutput.label}</div>
                <div className="text-5xl font-bold text-emerald-600">
                  {typeof result.outputs[primaryOutput.name] === 'number'
                    ? formatCurrencyLarge(result.outputs[primaryOutput.name] as number)
                    : '$0'}
                </div>
                <div className="mt-3 text-sm text-slate-500">
                  {result.filing_status.replace(/_/g, ' ')} &middot; Tax Year {result.year}
                </div>
              </div>
            )}

            {/* QBI Breakdown */}
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">QBI Computation Breakdown</h3>
              <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
                {OUTPUT_DEFS.filter((o) => !o.primary).map((outputDef) => {
                  const val = result.outputs[outputDef.name];
                  const isError = typeof val === 'object' && val !== null;
                  const numVal = typeof val === 'number' ? val : 0;
                  const isZero = numVal === 0;
                  return (
                    <div
                      key={outputDef.name}
                      className={`flex items-center justify-between px-5 py-3 ${isZero ? 'opacity-60' : ''}`}
                    >
                      <div>
                        <div className="text-sm text-slate-700">{outputDef.label}</div>
                        <div className="text-xs text-slate-400 font-mono">{outputDef.name}</div>
                      </div>
                      <div className="text-right">
                        {isError ? (
                          <span className="text-sm text-red-500">Error</span>
                        ) : (
                          <span className={`text-lg font-semibold tabular-nums ${numVal < 0 ? 'text-red-600' : 'text-slate-900'}`}>
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
                <h3 className="text-sm font-semibold text-slate-700 mb-3">
                  Model Parameters ({result.year})
                </h3>
                <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody className="divide-y divide-slate-100">
                      {Object.entries(result.parameters).map(([key, val]) => {
                        const isRate = key.includes('rate');
                        const label = key
                          .replace(/_/g, ' ')
                          .replace(/\b\w/g, (c) => c.toUpperCase());
                        return (
                          <tr key={key}>
                            <td className="px-5 py-2.5 text-slate-600">{label}</td>
                            <td className="px-5 py-2.5 text-right font-mono text-slate-900">
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
            <div className="bg-blue-50 rounded-xl border border-blue-200 p-5">
              <h3 className="text-sm font-semibold text-blue-800 mb-2">How this works</h3>
              <p className="text-sm text-blue-700 leading-relaxed">
                This calculator runs a full PolicyEngine US simulation (v1.669.0).
                The QBID is computed following IRC &sect;199A: 20% of QBI, subject to
                W-2 wage and property limitations, SSTB phase-out, and capped at
                20% of taxable income less net capital gains.
              </p>
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md">
              <svg className="w-16 h-16 mx-auto mb-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <p className="text-lg font-medium text-slate-500 mb-1">QBID Calculator</p>
              <p className="text-sm text-slate-400">
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
