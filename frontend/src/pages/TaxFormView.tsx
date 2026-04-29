import { useState, useEffect } from 'react';
import {
  FormMappingResponse,
  TaxFormMapping,
  FormLineMapping,
  FormScheduleMapping,
  FormImplementationStatus,
} from '../types/taxForm';

type TabType = 'overview' | 'form8995' | 'form8995a' | 'gaps';

function TaxFormView() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [data, setData] = useState<FormMappingResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFormMapping();
  }, []);

  const fetchFormMapping = async () => {
    try {
      const res = await fetch('/api/forms/mapping');
      if (!res.ok) throw new Error('Failed to fetch form mapping');
      const result = await res.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-pe-gray-50">
        <div className="text-pe-text-tertiary">Loading tax form mapping...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-full bg-pe-gray-50">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  const form8995 = data.forms.find((f) => f.form_number === '8995');
  const form8995a = data.forms.find((f) => f.form_number === '8995-A');

  return (
    <div className="h-full flex flex-col bg-pe-gray-50">
      {/* Tab navigation */}
      <div className="bg-white border-b border-pe-gray-200 px-6">
        <nav className="flex gap-8">
          {(['overview', 'form8995', 'form8995a', 'gaps'] as TabType[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-pe-text-primary text-pe-text-primary'
                  : 'border-transparent text-pe-text-tertiary hover:text-pe-text-secondary hover:border-pe-gray-300'
              }`}
            >
              {tab === 'overview' && 'Overview'}
              {tab === 'form8995' && 'Form 8995 (Simplified)'}
              {tab === 'form8995a' && 'Form 8995-A (Complex)'}
              {tab === 'gaps' && 'Gaps & Fixes'}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'overview' && <OverviewTab data={data} />}
        {activeTab === 'form8995' && form8995 && <FormDetailTab form={form8995} />}
        {activeTab === 'form8995a' && form8995a && <FormDetailTab form={form8995a} />}
        {activeTab === 'gaps' && <GapsTab data={data} />}
      </div>
    </div>
  );
}

// Status badge component
function StatusBadge({ status }: { status: FormImplementationStatus }) {
  const styles = {
    complete: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    partial: 'bg-amber-50 text-amber-700 border-amber-200',
    missing: 'bg-red-50 text-red-700 border-red-200',
    not_applicable: 'bg-pe-gray-50 text-pe-text-tertiary border-pe-gray-200',
  };
  const labels = {
    complete: 'Complete',
    partial: 'Partial',
    missing: 'Missing',
    not_applicable: 'N/A',
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-pe-md text-xs font-medium border ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}

// Overview Tab
function OverviewTab({ data }: { data: FormMappingResponse }) {
  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-pe-lg border border-pe-gray-200 p-6">
          <h2 className="text-xl font-semibold text-pe-text-primary mb-2">IRS Form to PolicyEngine Mapping</h2>
          <p className="text-pe-text-secondary">
            Cross-reference of IRS Form 8995 and Form 8995-A with PolicyEngine's QBID implementation.
            This shows which form lines are correctly implemented, partially implemented, or missing.
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-white rounded-pe-lg border border-pe-gray-200 p-4 text-center">
            <div className="text-3xl font-bold text-pe-text-primary">{data.summary.total_elements}</div>
            <div className="text-sm text-pe-text-tertiary">Total Elements</div>
          </div>
          <div className="bg-emerald-50 rounded-pe-lg border border-emerald-200 p-4 text-center">
            <div className="text-3xl font-bold text-emerald-600">{data.summary.complete}</div>
            <div className="text-sm text-emerald-700">Complete</div>
          </div>
          <div className="bg-amber-50 rounded-pe-lg border border-amber-200 p-4 text-center">
            <div className="text-3xl font-bold text-amber-600">{data.summary.partial}</div>
            <div className="text-sm text-amber-700">Partial</div>
          </div>
          <div className="bg-red-50 rounded-pe-lg border border-red-200 p-4 text-center">
            <div className="text-3xl font-bold text-red-600">{data.summary.missing}</div>
            <div className="text-sm text-red-700">Missing</div>
          </div>
          <div className="bg-pe-teal-50 rounded-pe-lg border border-pe-teal-200 p-4 text-center">
            <div className="text-3xl font-bold text-pe-teal-600">{data.summary.implementation_pct}%</div>
            <div className="text-sm text-pe-teal-700">Implemented</div>
          </div>
        </div>

        {/* Forms Summary */}
        <div className="grid grid-cols-2 gap-6">
          {data.forms.map((form) => (
            <div key={form.form_number} className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
              <div className="px-6 py-4 bg-pe-gray-50 border-b border-pe-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-pe-text-primary">Form {form.form_number}</h3>
                    <p className="text-sm text-pe-text-tertiary">{form.form_title}</p>
                  </div>
                  <a
                    href={form.irs_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-pe-teal-600 hover:text-pe-teal-700 hover:underline"
                  >
                    View Form
                  </a>
                </div>
              </div>
              <div className="p-6">
                <p className="text-sm text-pe-text-secondary mb-4">{form.who_can_use}</p>

                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center p-2 bg-emerald-50 rounded-pe-md">
                    <div className="text-lg font-semibold text-emerald-600">{form.complete_lines}</div>
                    <div className="text-xs text-emerald-700">Complete</div>
                  </div>
                  <div className="text-center p-2 bg-amber-50 rounded-pe-md">
                    <div className="text-lg font-semibold text-amber-600">{form.partial_lines}</div>
                    <div className="text-xs text-amber-700">Partial</div>
                  </div>
                  <div className="text-center p-2 bg-red-50 rounded-pe-md">
                    <div className="text-lg font-semibold text-red-600">{form.missing_lines}</div>
                    <div className="text-xs text-red-700">Missing</div>
                  </div>
                </div>

                <div className="text-sm text-pe-text-tertiary">
                  <div>Thresholds (2024):</div>
                  <div className="font-mono">
                    Single: ${form.threshold_single.toLocaleString()} | Joint: ${form.threshold_joint.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* What's Working */}
        <div className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-emerald-50 border-b border-pe-gray-200">
            <h3 className="font-semibold text-emerald-800">What's Working Correctly</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              {data.working_correctly.map((item) => (
                <div key={item.id} className="flex items-start gap-3 p-3 bg-emerald-50/50 rounded-pe-md">
                  <span className="text-emerald-500 mt-0.5">✓</span>
                  <div>
                    <div className="font-medium text-pe-text-primary">{item.title}</div>
                    <div className="text-sm text-pe-text-secondary">{item.description}</div>
                    <div className="text-xs text-pe-text-tertiary mt-1">{item.form_lines}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Form Detail Tab
function FormDetailTab({ form }: { form: TaxFormMapping }) {
  const [expandedLine, setExpandedLine] = useState<string | null>(null);

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Form Header */}
        <div className="bg-white rounded-pe-lg border border-pe-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-semibold text-pe-text-primary">Form {form.form_number}</h2>
              <p className="text-pe-text-secondary">{form.form_title}</p>
              <p className="text-sm text-pe-text-tertiary mt-2">{form.description}</p>
            </div>
            <div className="flex gap-2">
              <a
                href={form.irs_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-pe-teal-50 text-pe-teal-700 rounded-pe-md text-sm font-medium hover:bg-pe-teal-100"
              >
                View Form PDF
              </a>
              <a
                href={form.instructions_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 bg-pe-gray-100 text-pe-text-secondary rounded-pe-md text-sm font-medium hover:bg-pe-gray-200"
              >
                Instructions
              </a>
            </div>
          </div>
        </div>

        {/* Line-by-Line Mapping */}
        <div className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-pe-gray-50 border-b border-pe-gray-200">
            <h3 className="font-semibold text-pe-text-primary">Line-by-Line Mapping</h3>
          </div>
          <div className="divide-y divide-pe-gray-100">
            {form.lines.map((line) => (
              <LineRow
                key={line.line_number}
                line={line}
                expanded={expandedLine === line.line_number}
                onToggle={() => setExpandedLine(expandedLine === line.line_number ? null : line.line_number)}
              />
            ))}
          </div>
        </div>

        {/* Schedules */}
        {form.schedules.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-pe-text-primary">Schedules</h3>
            {form.schedules.map((schedule) => (
              <ScheduleCard key={schedule.schedule_id} schedule={schedule} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Line Row Component
function LineRow({
  line,
  expanded,
  onToggle,
}: {
  line: FormLineMapping;
  expanded: boolean;
  onToggle: () => void;
}) {
  const isMissing = line.status === 'missing';
  const isPartial = line.status === 'partial';

  return (
    <div className={`group ${isMissing ? 'bg-red-50/30' : ''}`}>
      <button onClick={onToggle} className="w-full px-6 py-4 flex items-center gap-4 hover:bg-pe-gray-50 text-left">
        <div className="w-20 font-mono text-sm text-pe-text-tertiary shrink-0">{line.line_number}</div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-pe-text-primary truncate">{line.line_label}</div>
          <div className="text-sm text-pe-text-tertiary truncate">{line.description}</div>
          {(isMissing || isPartial) && line.gap_description && (
            <div className={`text-xs mt-1 truncate ${isMissing ? 'text-red-600' : 'text-amber-600'}`}>
              {isMissing ? 'Missing: ' : 'Gap: '}{line.gap_description}
            </div>
          )}
        </div>
        <StatusBadge status={line.status} />
        <span className="text-pe-text-tertiary text-sm">{expanded ? '▼' : '▶'}</span>
      </button>

      {expanded && (
        <div className="px-6 py-4 bg-pe-gray-50 border-t border-pe-gray-100">
          <div className="grid grid-cols-2 gap-6">
            {/* IRS Instructions */}
            <div>
              <h4 className="text-xs font-semibold text-pe-text-tertiary uppercase mb-2">IRS Instructions</h4>
              <p className="text-sm text-pe-text-secondary">{line.form_instructions || 'No specific instructions'}</p>
            </div>

            {/* PolicyEngine Implementation */}
            <div>
              <h4 className="text-xs font-semibold text-pe-text-tertiary uppercase mb-2">PolicyEngine Implementation</h4>
              {line.status === 'complete' && (
                <div className="mb-2 p-2 bg-emerald-50 rounded-pe-md border border-emerald-200">
                  <p className="text-sm text-emerald-700">Fully implemented</p>
                </div>
              )}
              {line.pe_variable && (
                <div className="mb-2">
                  <span className="text-xs text-pe-text-tertiary">Variable: </span>
                  <code className="text-xs bg-pe-gray-200 px-1.5 py-0.5 rounded-pe-sm">{line.pe_variable}</code>
                </div>
              )}
              {line.pe_formula && <p className="text-sm text-pe-text-secondary font-mono text-xs mb-2">{line.pe_formula}</p>}
              {isMissing && !line.pe_variable && (
                <div className="mb-2 p-2 bg-red-50 rounded-pe-md border border-red-200">
                  <p className="text-sm text-red-700 font-medium">Not implemented in PolicyEngine</p>
                </div>
              )}
              {line.gap_description && (
                <div className={`mt-2 p-2 rounded-pe-md border ${isMissing ? 'bg-red-50 border-red-200' : 'bg-amber-50 border-amber-200'}`}>
                  <p className={`text-xs font-semibold uppercase mb-1 ${isMissing ? 'text-red-800' : 'text-amber-800'}`}>
                    {isMissing ? 'What\'s Missing' : 'Implementation Gap'}
                  </p>
                  <p className={`text-sm ${isMissing ? 'text-red-700' : 'text-amber-700'}`}>{line.gap_description}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Schedule Card Component
function ScheduleCard({ schedule }: { schedule: FormScheduleMapping }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-pe-gray-50"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-pe-gray-100 rounded-pe-md flex items-center justify-center font-semibold text-pe-text-secondary">
            {schedule.schedule_id}
          </div>
          <div className="text-left">
            <div className="font-medium text-pe-text-primary">{schedule.schedule_name}</div>
            <div className="text-sm text-pe-text-tertiary">{schedule.description}</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={schedule.status} />
          <span className="text-pe-text-tertiary">{expanded ? '▼' : '▶'}</span>
        </div>
      </button>

      {expanded && (
        <div className="px-6 py-4 border-t border-pe-gray-200 bg-pe-gray-50">
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-pe-text-tertiary uppercase mb-1">Who Must File</h4>
            <p className="text-sm text-pe-text-secondary">{schedule.who_must_file}</p>
          </div>

          <div className="mb-4">
            <h4 className="text-xs font-semibold text-pe-text-tertiary uppercase mb-1">Implementation Status</h4>
            <p className="text-sm text-pe-text-secondary">{schedule.status_notes}</p>
          </div>

          {schedule.key_requirements.length > 0 && (
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-pe-text-tertiary uppercase mb-2">Key Requirements</h4>
              <ul className="space-y-1">
                {schedule.key_requirements.map((req, i) => (
                  <li key={i} className="text-sm text-pe-text-secondary flex items-start gap-2">
                    <span className="text-pe-text-tertiary">•</span>
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {schedule.lines.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-pe-text-tertiary uppercase mb-2">Lines</h4>
              <div className="space-y-2">
                {schedule.lines.map((line) => (
                  <div key={line.line_number} className="p-3 bg-white rounded-pe-md border border-pe-gray-200">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-sm text-pe-text-tertiary">{line.line_number}</span>
                      <StatusBadge status={line.status} />
                    </div>
                    <div className="text-sm font-medium text-pe-text-primary">{line.line_label}</div>
                    {line.gap_description && (
                      <div className="text-sm text-red-600 mt-1">{line.gap_description}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Gaps Tab
function GapsTab({ data }: { data: FormMappingResponse }) {
  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-pe-lg border border-pe-gray-200 p-6">
          <h2 className="text-xl font-semibold text-pe-text-primary mb-2">Implementation Gaps & Recommended Fixes</h2>
          <p className="text-pe-text-secondary">
            Priority list of missing features that should be added to PolicyEngine to fully support Form 8995/8995-A.
          </p>
        </div>

        {/* Critical Gaps */}
        <div className="space-y-4">
          {data.critical_gaps.map((gap, index) => (
            <div key={gap.id} className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
              <div className="px-6 py-4 bg-red-50 border-b border-red-100 flex items-center gap-4">
                <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center text-red-600 font-semibold">
                  {index + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-red-900">{gap.title}</h3>
                  <div className="text-sm text-red-700">{gap.form_lines}</div>
                </div>
              </div>
              <div className="p-6">
                <p className="text-pe-text-secondary mb-4">{gap.description}</p>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-amber-50 rounded-pe-md border border-amber-200">
                    <div className="text-xs font-semibold text-amber-800 uppercase mb-1">Impact</div>
                    <div className="text-sm text-amber-900">{gap.impact}</div>
                  </div>
                  <div className="p-3 bg-pe-teal-50 rounded-pe-md border border-pe-teal-200">
                    <div className="text-xs font-semibold text-pe-teal-700 uppercase mb-1">Fix Complexity</div>
                    <div className="text-sm text-pe-teal-700">{gap.fix_complexity}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Priority Recommendation */}
        {data.critical_gaps.length > 0 && (
          <div className="bg-pe-teal-50 rounded-pe-lg border border-pe-teal-200 p-6">
            <h3 className="font-semibold text-pe-teal-700 mb-3">Recommended Fix Priority</h3>
            <ol className="space-y-2">
              {data.critical_gaps.map((gap, idx) => (
                <li key={gap.id} className="flex items-start gap-3">
                  <span className="w-6 h-6 bg-pe-teal-600 text-white rounded-full flex items-center justify-center text-sm font-medium shrink-0">
                    {idx + 1}
                  </span>
                  <div>
                    <span className="font-medium text-pe-text-primary">{gap.title}</span>
                    <span className="text-pe-text-secondary"> — {gap.fix_complexity}</span>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  );
}

export default TaxFormView;
