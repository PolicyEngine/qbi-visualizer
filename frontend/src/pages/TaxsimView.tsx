import { useState, useEffect } from 'react';
import {
  ComparisonResult,
  ComparisonItem,
  AdjacentSectionCoverage,
} from '../types/taxsim';

const API_BASE = 'http://localhost:8000';

type TabType = 'overview' | 'adjacent' | 'code';

function TaxsimView() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchComparison();
  }, []);

  const fetchComparison = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/taxsim/comparison`);
      if (!res.ok) throw new Error('Failed to fetch comparison');
      const data = await res.json();
      setComparison(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-500">Loading TAXSIM comparison...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-slate-50">
      {/* Tab navigation */}
      <div className="bg-white border-b border-slate-200 px-6 py-2">
        <nav className="flex gap-6">
          {(['overview', 'adjacent', 'code'] as TabType[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab === 'overview' && 'Implementation Comparison'}
              {tab === 'adjacent' && 'Adjacent Sections Coverage'}
              {tab === 'code' && 'Code Side-by-Side'}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'overview' && comparison && <OverviewTab comparison={comparison} />}
        {activeTab === 'adjacent' && comparison && <AdjacentSectionsTab comparison={comparison} />}
        {activeTab === 'code' && comparison && <CodeTab comparison={comparison} />}
      </div>
    </div>
  );
}

// Overview Tab
function OverviewTab({ comparison }: { comparison: ComparisonResult }) {
  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Summary */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Comparison Summary</h2>
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{comparison.summary.none}</div>
              <div className="text-sm text-green-700">Equivalent</div>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">{comparison.summary.minor}</div>
              <div className="text-sm text-yellow-700">Minor Diff</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{comparison.summary.significant}</div>
              <div className="text-sm text-orange-700">Significant</div>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-600">{comparison.summary.critical}</div>
              <div className="text-sm text-red-700">Critical</div>
            </div>
          </div>

          {/* Methodology differences */}
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Key Methodology Differences</h3>
          <ul className="space-y-2">
            {comparison.methodology_differences.map((diff, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <span className="text-blue-500 mt-0.5">•</span>
                {diff}
              </li>
            ))}
          </ul>
        </div>

        {/* Side-by-side implementations */}
        <div className="grid grid-cols-2 gap-6">
          {/* TAXSIM */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <h2 className="text-lg font-semibold text-slate-900">TAXSIM 35</h2>
            </div>
            <div className="text-sm text-slate-500 mb-4">
              Source: {comparison.taxsim.source_file}
            </div>

            <h3 className="text-sm font-semibold text-slate-700 mb-2">Key Features</h3>
            <ul className="space-y-1 mb-4">
              {comparison.taxsim.key_features.map((f, i) => (
                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  {f}
                </li>
              ))}
            </ul>

            <h3 className="text-sm font-semibold text-slate-700 mb-2">Limitations</h3>
            <ul className="space-y-1">
              {comparison.taxsim.limitations.map((l, i) => (
                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  {l}
                </li>
              ))}
            </ul>
          </div>

          {/* PolicyEngine */}
          <div className="bg-white rounded-lg border border-slate-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
              <h2 className="text-lg font-semibold text-slate-900">PolicyEngine US</h2>
            </div>
            <div className="text-sm text-slate-500 mb-4">
              Variable: {comparison.policyengine.main_variable}
            </div>

            <h3 className="text-sm font-semibold text-slate-700 mb-2">Key Features</h3>
            <ul className="space-y-1 mb-4">
              {comparison.policyengine.key_features.map((f, i) => (
                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  {f}
                </li>
              ))}
            </ul>

            <h3 className="text-sm font-semibold text-slate-700 mb-2">Limitations</h3>
            <ul className="space-y-1">
              {comparison.policyengine.limitations.map((l, i) => (
                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  {l}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Detailed comparisons */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Detailed Comparison</h2>
          <div className="space-y-4">
            {comparison.comparisons.map((item) => (
              <ComparisonCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ComparisonCard({ item }: { item: ComparisonItem }) {
  const [expanded, setExpanded] = useState(false);

  const severityColors = {
    none: 'bg-green-100 text-green-700 border-green-200',
    minor: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    significant: 'bg-orange-100 text-orange-700 border-orange-200',
    critical: 'bg-red-100 text-red-700 border-red-200',
  };

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-4">
          <span className="text-sm font-mono text-slate-500">{item.law_section}</span>
          <span className="font-medium text-slate-900">{item.description}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-2 py-1 text-xs rounded border ${severityColors[item.severity]}`}>
            {item.severity}
          </span>
          <span className="text-slate-400">{expanded ? '▼' : '▶'}</span>
        </div>
      </button>

      {expanded && (
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <h4 className="text-xs font-semibold text-blue-600 uppercase mb-1">TAXSIM Approach</h4>
              <p className="text-sm text-slate-700">{item.taxsim_approach}</p>
            </div>
            <div>
              <h4 className="text-xs font-semibold text-emerald-600 uppercase mb-1">PolicyEngine Approach</h4>
              <p className="text-sm text-slate-700">{item.policyengine_approach}</p>
            </div>
          </div>

          <div className="bg-white rounded border border-slate-200 p-3">
            <h4 className="text-xs font-semibold text-slate-500 uppercase mb-1">Difference</h4>
            <p className="text-sm text-slate-800">{item.difference}</p>
          </div>

          {item.taxsim_code && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">TAXSIM Code</h4>
              <pre className="bg-slate-900 text-slate-100 p-3 rounded text-xs overflow-x-auto">
                <code>{item.taxsim_code.code}</code>
              </pre>
              <div className="text-xs text-slate-500 mt-1">
                {item.taxsim_code.file}:{item.taxsim_code.line_start}-{item.taxsim_code.line_end}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Adjacent Sections Tab
function AdjacentSectionsTab({ comparison }: { comparison: ComparisonResult }) {
  const [selectedSection, setSelectedSection] = useState<AdjacentSectionCoverage | null>(
    comparison.adjacent_section_coverage[0] || null
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'partial':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'missing':
        return 'bg-red-100 text-red-700 border-red-200';
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return '✓';
      case 'partial':
        return '◐';
      case 'missing':
        return '✗';
      default:
        return '—';
    }
  };

  // Calculate summary statistics
  const taxsimStats = {
    complete: comparison.adjacent_section_coverage.filter((s) => s.taxsim_status === 'complete').length,
    partial: comparison.adjacent_section_coverage.filter((s) => s.taxsim_status === 'partial').length,
    missing: comparison.adjacent_section_coverage.filter((s) => s.taxsim_status === 'missing').length,
  };
  const peStats = {
    complete: comparison.adjacent_section_coverage.filter((s) => s.policyengine_status === 'complete').length,
    partial: comparison.adjacent_section_coverage.filter((s) => s.policyengine_status === 'partial').length,
    missing: comparison.adjacent_section_coverage.filter((s) => s.policyengine_status === 'missing').length,
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Summary */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Adjacent IRC Section Coverage</h2>
          <p className="text-sm text-slate-600 mb-4">
            How each implementation handles IRC sections that §199A references or depends on.
          </p>

          <div className="grid grid-cols-2 gap-6">
            {/* TAXSIM Summary */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-blue-800 mb-3">TAXSIM 35</h3>
              <div className="flex gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{taxsimStats.complete}</div>
                  <div className="text-xs text-slate-600">Complete</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{taxsimStats.partial}</div>
                  <div className="text-xs text-slate-600">Partial</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{taxsimStats.missing}</div>
                  <div className="text-xs text-slate-600">Missing</div>
                </div>
              </div>
            </div>

            {/* PolicyEngine Summary */}
            <div className="bg-emerald-50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-emerald-800 mb-3">PolicyEngine US</h3>
              <div className="flex gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{peStats.complete}</div>
                  <div className="text-xs text-slate-600">Complete</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{peStats.partial}</div>
                  <div className="text-xs text-slate-600">Partial</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{peStats.missing}</div>
                  <div className="text-xs text-slate-600">Missing</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main content - two column layout */}
        <div className="grid grid-cols-3 gap-6">
          {/* Section list */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
              <h3 className="font-medium text-slate-900">IRC Sections</h3>
            </div>
            <div className="divide-y divide-slate-100 max-h-[600px] overflow-y-auto">
              {comparison.adjacent_section_coverage.map((section) => (
                <button
                  key={section.section_id}
                  onClick={() => setSelectedSection(section)}
                  className={`w-full px-4 py-3 text-left hover:bg-slate-50 transition-colors ${
                    selectedSection?.section_id === section.section_id ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-mono text-slate-500">{section.section_number}</div>
                      <div className="text-sm font-medium text-slate-900">{section.title}</div>
                    </div>
                    <div className="flex gap-1">
                      <span
                        className={`w-6 h-6 flex items-center justify-center text-xs rounded ${getStatusColor(
                          section.taxsim_status
                        )}`}
                        title={`TAXSIM: ${section.taxsim_status}`}
                      >
                        T
                      </span>
                      <span
                        className={`w-6 h-6 flex items-center justify-center text-xs rounded ${getStatusColor(
                          section.policyengine_status
                        )}`}
                        title={`PolicyEngine: ${section.policyengine_status}`}
                      >
                        P
                      </span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Section detail */}
          <div className="col-span-2 bg-white rounded-lg border border-slate-200 overflow-hidden">
            {selectedSection ? (
              <div>
                <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
                  <div className="text-sm font-mono text-slate-500">{selectedSection.section_number}</div>
                  <h3 className="text-lg font-semibold text-slate-900">{selectedSection.title}</h3>
                </div>

                <div className="p-6 space-y-6">
                  {/* Impact */}
                  <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                    <h4 className="text-sm font-semibold text-amber-800 mb-1">Impact on QBID</h4>
                    <p className="text-sm text-amber-700">{selectedSection.impact_on_qbid}</p>
                  </div>

                  {/* Side-by-side comparison */}
                  <div className="grid grid-cols-2 gap-4">
                    {/* TAXSIM */}
                    <div className="border border-slate-200 rounded-lg overflow-hidden">
                      <div className="px-4 py-2 bg-blue-50 border-b border-slate-200 flex items-center justify-between">
                        <span className="text-sm font-semibold text-blue-800">TAXSIM 35</span>
                        <span
                          className={`px-2 py-1 text-xs rounded border ${getStatusColor(
                            selectedSection.taxsim_status
                          )}`}
                        >
                          {getStatusIcon(selectedSection.taxsim_status)} {selectedSection.taxsim_status}
                        </span>
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-slate-700">{selectedSection.taxsim_notes}</p>
                      </div>
                    </div>

                    {/* PolicyEngine */}
                    <div className="border border-slate-200 rounded-lg overflow-hidden">
                      <div className="px-4 py-2 bg-emerald-50 border-b border-slate-200 flex items-center justify-between">
                        <span className="text-sm font-semibold text-emerald-800">PolicyEngine US</span>
                        <span
                          className={`px-2 py-1 text-xs rounded border ${getStatusColor(
                            selectedSection.policyengine_status
                          )}`}
                        >
                          {getStatusIcon(selectedSection.policyengine_status)} {selectedSection.policyengine_status}
                        </span>
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-slate-700">{selectedSection.policyengine_notes}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500">Select a section to view details</div>
            )}
          </div>
        </div>

        {/* Comparison table */}
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
          <div className="px-4 py-3 bg-slate-50 border-b border-slate-200">
            <h3 className="font-medium text-slate-900">Full Comparison Table</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50">
                  <th className="px-4 py-3 text-left font-semibold text-slate-700">Section</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700">Title</th>
                  <th className="px-4 py-3 text-center font-semibold text-blue-700">TAXSIM</th>
                  <th className="px-4 py-3 text-center font-semibold text-emerald-700">PolicyEngine</th>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700">Impact</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {comparison.adjacent_section_coverage.map((section) => (
                  <tr key={section.section_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-mono text-slate-600">{section.section_number}</td>
                    <td className="px-4 py-3 text-slate-900">{section.title}</td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded border ${getStatusColor(
                          section.taxsim_status
                        )}`}
                      >
                        {getStatusIcon(section.taxsim_status)} {section.taxsim_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded border ${getStatusColor(
                          section.policyengine_status
                        )}`}
                      >
                        {getStatusIcon(section.policyengine_status)} {section.policyengine_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate" title={section.impact_on_qbid}>
                      {section.impact_on_qbid}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Code Tab
function CodeTab({ comparison }: { comparison: ComparisonResult }) {
  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">QBI Code Comparison</h2>

        <div className="grid grid-cols-2 gap-6">
          {/* TAXSIM Code */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-blue-600 uppercase">TAXSIM FORTRAN</h3>
            {comparison.taxsim.code_blocks.map((block, i) => (
              <div key={i} className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
                  <div className="font-medium text-sm text-slate-900">{block.description}</div>
                  <div className="text-xs text-slate-500">
                    {block.file}:{block.line_start}-{block.line_end}
                  </div>
                </div>
                <pre className="bg-slate-900 text-slate-100 p-4 text-xs overflow-x-auto">
                  <code>{block.code}</code>
                </pre>
                {block.variables_used.length > 0 && (
                  <div className="px-4 py-2 bg-slate-50 border-t border-slate-200">
                    <span className="text-xs text-slate-500">Variables: </span>
                    <span className="text-xs font-mono text-slate-600">
                      {block.variables_used.join(', ')}
                    </span>
                  </div>
                )}
              </div>
            ))}

            {/* TAXSIM Variables */}
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
                <div className="font-medium text-sm text-slate-900">QBI Input Variables</div>
              </div>
              <div className="p-4">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-left text-slate-500">
                      <th className="pb-2">Var #</th>
                      <th className="pb-2">Name</th>
                      <th className="pb-2">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.taxsim.qbi_variables
                      .filter((v) => v.qbi_related)
                      .map((v) => (
                        <tr key={v.number} className="border-t border-slate-100">
                          <td className="py-2 font-mono text-slate-600">data({v.number})</td>
                          <td className="py-2 font-mono text-blue-600">{v.name}</td>
                          <td className="py-2 text-slate-700">{v.description}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* PolicyEngine Code */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-emerald-600 uppercase">PolicyEngine Python</h3>
            {comparison.policyengine.code_blocks.map((block, i) => (
              <div key={i} className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                <div className="px-4 py-2 bg-slate-50 border-b border-slate-200 flex justify-between items-start">
                  <div>
                    <div className="font-medium text-sm text-slate-900">{block.description}</div>
                    <div className="text-xs font-mono text-slate-500">{block.variable_name}</div>
                  </div>
                  {block.github_url && (
                    <a
                      href={block.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline"
                    >
                      View on GitHub
                    </a>
                  )}
                </div>
                <pre className="bg-slate-900 text-slate-100 p-4 text-xs overflow-x-auto">
                  <code>{block.code}</code>
                </pre>
              </div>
            ))}

            {/* Dependent variables */}
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
                <div className="font-medium text-sm text-slate-900">Dependent Variables</div>
              </div>
              <div className="p-4">
                <div className="flex flex-wrap gap-2">
                  {comparison.policyengine.dependent_variables.map((v) => (
                    <span
                      key={v}
                      className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs font-mono"
                    >
                      {v}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TaxsimView;
