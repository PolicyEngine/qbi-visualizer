import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  QBIDLawStructure,
  LawSection,
  ImplementationStatus,
} from '../types/law';

type ViewMode = 'flowchart' | 'code-mapping' | 'adjacent';

const StatusBadge = ({ status }: { status: ImplementationStatus }) => {
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
};

const SectionCard = ({
  section,
  isActive,
  onClick,
}: {
  section: LawSection;
  isActive: boolean;
  onClick: () => void;
}) => {
  const borderColors = {
    complete: 'border-l-emerald-500',
    partial: 'border-l-amber-500',
    missing: 'border-l-red-500',
    not_applicable: 'border-l-pe-gray-300',
  };

  return (
    <div
      className={`bg-white border border-pe-gray-200 border-l-4 ${borderColors[section.status]} rounded-pe-lg p-4 cursor-pointer transition-all hover:shadow-md ${
        isActive ? 'ring-2 ring-pe-teal-500 shadow-md' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex justify-between items-start gap-3 mb-2">
        <div className="min-w-0">
          <div className="text-xs font-mono text-pe-text-tertiary mb-1">{section.section_number}</div>
          <h3 className="font-medium text-pe-text-primary leading-tight">{section.title}</h3>
        </div>
        <StatusBadge status={section.status} />
      </div>
      <p className="text-sm text-pe-text-secondary line-clamp-2">{section.description}</p>
    </div>
  );
};

const FlowchartView = ({
  structure,
  selectedSection,
  onSelectSection,
}: {
  structure: QBIDLawStructure;
  selectedSection: string | null;
  onSelectSection: (id: string) => void;
}) => {
  const stages = [
    {
      title: 'Define Qualified Business Income',
      subtitle: '§199A(c) & (d)',
      sections: structure.sections.filter((s) =>
        ['sec_c_qbi_definition', 'sec_c2_loss_carryover', 'sec_c3_exclusions', 'sec_d_qualified_business'].includes(s.id)
      ),
    },
    {
      title: 'Apply Wage & Property Limitations',
      subtitle: '§199A(b)(2) & (b)(3)',
      sections: structure.sections.filter((s) =>
        ['sec_b2_wage_limitation', 'sec_b3_phaseout', 'sec_e_thresholds'].includes(s.id)
      ),
    },
    {
      title: 'SSTB Treatment',
      subtitle: '§199A(d)(2)',
      sections: structure.sections.filter((s) => ['sec_d2_sstb'].includes(s.id)),
    },
    {
      title: 'Combine & Apply Final Cap',
      subtitle: '§199A(a) & (b)(1)',
      sections: structure.sections.filter((s) =>
        ['sec_b1_combined_qbi', 'sec_a_allowance', 'sec_i_minimum'].includes(s.id)
      ),
    },
    {
      title: 'Special Provisions',
      subtitle: '§199A(g)',
      sections: structure.sections.filter((s) => ['sec_g_cooperatives'].includes(s.id)),
    },
  ];

  const selectedSectionData = structure.sections.find((s) => s.id === selectedSection);

  return (
    <div className="flex h-full">
      {/* Left: Flow diagram */}
      <div className="flex-1 overflow-y-auto p-6 bg-pe-gray-50">
        <div className="max-w-3xl mx-auto">
          {/* Summary */}
          <div className="mb-8 bg-white rounded-pe-lg border border-pe-gray-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-pe-text-primary">{structure.title}</h2>
                <p className="text-sm text-pe-text-tertiary mt-1">
                  Effective {structure.effective_date}
                  {structure.sunset_date && <span className="text-amber-600"> &middot; Sunsets {structure.sunset_date}</span>}
                </p>
              </div>
              <div className="flex gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-emerald-600">{structure.implemented_sections}</div>
                  <div className="text-xs text-pe-text-tertiary">Complete</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-amber-600">{structure.partial_sections}</div>
                  <div className="text-xs text-pe-text-tertiary">Partial</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{structure.missing_sections}</div>
                  <div className="text-xs text-pe-text-tertiary">Missing</div>
                </div>
              </div>
            </div>
            {/* Progress bar */}
            <div className="mt-4 h-2 bg-pe-gray-100 rounded-full overflow-hidden flex">
              <div
                className="bg-emerald-500 h-full"
                style={{ width: `${(structure.implemented_sections / structure.total_sections) * 100}%` }}
              />
              <div
                className="bg-amber-500 h-full"
                style={{ width: `${(structure.partial_sections / structure.total_sections) * 100}%` }}
              />
              <div
                className="bg-red-500 h-full"
                style={{ width: `${(structure.missing_sections / structure.total_sections) * 100}%` }}
              />
            </div>
          </div>

          {/* Stages */}
          {stages.map((stage, idx) => (
            <div key={idx} className="mb-8">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-pe-text-primary text-white flex items-center justify-center text-sm font-semibold">
                  {idx + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-pe-text-primary">{stage.title}</h3>
                  <span className="text-xs text-pe-text-tertiary">{stage.subtitle}</span>
                </div>
              </div>
              <div className="ml-4 pl-7 border-l-2 border-pe-gray-200 space-y-3">
                {stage.sections.map((section) => (
                  <SectionCard
                    key={section.id}
                    section={section}
                    isActive={selectedSection === section.id}
                    onClick={() => onSelectSection(section.id)}
                  />
                ))}
              </div>
              {idx < stages.length - 1 && (
                <div className="flex justify-center my-4">
                  <svg className="w-5 h-5 text-pe-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Right: Details */}
      <div className="w-[420px] border-l border-pe-gray-200 bg-white overflow-y-auto">
        {selectedSectionData ? (
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm text-pe-teal-600">{selectedSectionData.section_number}</span>
                <StatusBadge status={selectedSectionData.status} />
              </div>
              <h2 className="text-xl font-semibold text-pe-text-primary">{selectedSectionData.title}</h2>
            </div>

            <p className="text-pe-text-secondary mb-6 leading-relaxed">{selectedSectionData.description}</p>

            {selectedSectionData.status_notes && (
              <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-pe-lg">
                <div className="flex gap-2">
                  <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-sm text-amber-800">{selectedSectionData.status_notes}</p>
                </div>
              </div>
            )}

            {/* Legal text */}
            {selectedSectionData.legal_reference.text && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-pe-text-primary mb-3">Legal Text</h4>
                <blockquote className="text-sm text-pe-text-secondary italic border-l-2 border-pe-gray-300 pl-4 py-2 bg-pe-gray-50 rounded-r-pe-lg">
                  "{selectedSectionData.legal_reference.text}"
                </blockquote>
                <a
                  href={selectedSectionData.legal_reference.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-pe-teal-600 hover:text-pe-teal-700 mt-2"
                >
                  Read full text on Cornell Law
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            )}

            {/* Parameters */}
            {selectedSectionData.parameters.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-pe-text-primary mb-3">Parameters</h4>
                <div className="space-y-2">
                  {selectedSectionData.parameters.map((param, idx) => (
                    <div key={idx} className="flex justify-between items-center py-2 px-3 bg-pe-gray-50 rounded-pe-md">
                      <span className="text-sm text-pe-text-secondary">{param.label}</span>
                      <span className="text-sm font-mono font-medium text-pe-text-primary">
                        {typeof param.value === 'number'
                          ? param.unit === 'rate'
                            ? `${(param.value * 100).toFixed(0)}%`
                            : `$${param.value.toLocaleString()}`
                          : Array.isArray(param.value)
                            ? `${param.value.length} items`
                            : String(param.value)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Computation steps */}
            {selectedSectionData.steps.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-pe-text-primary mb-3">Computation Steps</h4>
                <div className="space-y-3">
                  {selectedSectionData.steps.map((step, idx) => (
                    <div key={idx} className="p-3 bg-pe-gray-50 rounded-pe-md border border-pe-gray-100">
                      <div className="flex items-start gap-2 mb-2">
                        <span className="flex-shrink-0 w-5 h-5 rounded-full bg-pe-gray-200 text-pe-text-secondary text-xs flex items-center justify-center font-medium">
                          {idx + 1}
                        </span>
                        <span className="text-sm text-pe-text-secondary">{step.description}</span>
                      </div>
                      {step.formula && (
                        <code className="block text-xs bg-white p-2 rounded-pe-sm border border-pe-gray-200 text-pe-text-secondary font-mono">
                          {step.formula}
                        </code>
                      )}
                      {step.code_reference && (
                        <div className="mt-2 text-xs text-amber-700 bg-amber-50 p-2 rounded-pe-sm">
                          {step.code_reference}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* GitHub link */}
            {selectedSectionData.github_url && (
              <a
                href={selectedSectionData.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-pe-text-secondary hover:text-pe-text-primary py-2 px-3 bg-pe-gray-50 rounded-pe-md border border-pe-gray-200 hover:border-pe-gray-300 transition-colors"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                View Source on GitHub
              </a>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-pe-text-tertiary">
            <div className="text-center p-6">
              <svg className="w-12 h-12 mx-auto mb-3 text-pe-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
              </svg>
              <p className="text-sm">Select a section to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const AdjacentSectionsView = ({ structure }: { structure: QBIDLawStructure }) => {
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

  const adjacentSections = structure.adjacent_sections || [];

  // Group by implementation status
  const complete = adjacentSections.filter((s) => s.status === 'complete');
  const partial = adjacentSections.filter((s) => s.status === 'partial');
  const missing = adjacentSections.filter((s) => s.status === 'missing');

  const selectedAdj = adjacentSections.find((s) => s.id === selectedSection);

  return (
    <div className="flex h-full">
      {/* Left: List of adjacent sections */}
      <div className="flex-1 overflow-y-auto p-6 bg-pe-gray-50">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-6 bg-white rounded-pe-lg border border-pe-gray-200 p-5">
            <h2 className="text-lg font-semibold text-pe-text-primary">Adjacent IRC Sections</h2>
            <p className="text-sm text-pe-text-tertiary mt-1">
              Other IRC sections that §199A references or depends on for complete QBID calculation
            </p>
            <div className="mt-4 flex gap-6">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
                <span className="text-sm text-pe-text-secondary">{complete.length} Complete</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
                <span className="text-sm text-pe-text-secondary">{partial.length} Partial</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-sm text-pe-text-secondary">{missing.length} Missing</span>
              </div>
            </div>
          </div>

          {/* Sections grouped by category */}
          {[
            { title: 'Income Qualification', sections: adjacentSections.filter((s) => ['sec_162', 'sec_469', 'sec_707'].includes(s.id)) },
            { title: 'SSTB Definition', sections: adjacentSections.filter((s) => ['sec_1202', 'sec_475'].includes(s.id)) },
            { title: 'REIT & PTP Income', sections: adjacentSections.filter((s) => ['sec_857', 'sec_7704'].includes(s.id)) },
            { title: 'Limitations & Aggregation', sections: adjacentSections.filter((s) => ['sec_1_h', 'sec_167_168', 'sec_52', 'sec_6051', 'sec_1_f'].includes(s.id)) },
            { title: 'Special Provisions', sections: adjacentSections.filter((s) => ['sec_1382_1385'].includes(s.id)) },
          ].map((group) => (
            <div key={group.title} className="mb-6">
              <h3 className="text-sm font-semibold text-pe-text-primary mb-3">
                {group.title}
              </h3>
              <div className="space-y-3">
                {group.sections.map((section) => (
                  <div
                    key={section.id}
                    onClick={() => setSelectedSection(section.id)}
                    className={`bg-white border rounded-pe-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                      selectedSection === section.id
                        ? 'ring-2 ring-pe-teal-500 border-pe-teal-300'
                        : 'border-pe-gray-200'
                    }`}
                  >
                    <div className="flex justify-between items-start gap-3 mb-2">
                      <div>
                        <div className="text-xs font-mono text-pe-teal-600 mb-1">{section.section_number}</div>
                        <h4 className="font-medium text-pe-text-primary">{section.title}</h4>
                      </div>
                      <StatusBadge status={section.status} />
                    </div>
                    <p className="text-sm text-pe-text-secondary line-clamp-2">{section.description}</p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {section.referenced_by.map((ref) => (
                        <span key={ref} className="text-xs bg-pe-gray-100 text-pe-text-secondary px-2 py-0.5 rounded-pe-sm">
                          {ref}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Details panel */}
      <div className="w-[450px] border-l border-pe-gray-200 bg-white overflow-y-auto">
        {selectedAdj ? (
          <div className="p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm text-pe-teal-600">{selectedAdj.section_number}</span>
                <StatusBadge status={selectedAdj.status} />
              </div>
              <h2 className="text-xl font-semibold text-pe-text-primary">{selectedAdj.title}</h2>
            </div>

            <p className="text-pe-text-secondary mb-6 leading-relaxed">{selectedAdj.description}</p>

            {/* Relevance to QBID */}
            <div className="mb-6 p-4 bg-pe-teal-50 border border-pe-teal-200 rounded-pe-lg">
              <h4 className="text-sm font-semibold text-pe-teal-700 mb-2">Relevance to §199A</h4>
              <p className="text-sm text-pe-teal-700">{selectedAdj.relevance_to_qbid}</p>
            </div>

            {/* Status notes */}
            {selectedAdj.status_notes && (
              <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-pe-lg">
                <div className="flex gap-2">
                  <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <p className="text-sm text-amber-800">{selectedAdj.status_notes}</p>
                </div>
              </div>
            )}

            {/* Key provisions */}
            {selectedAdj.key_provisions.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-pe-text-primary mb-3">Key Provisions</h4>
                <ul className="space-y-2">
                  {selectedAdj.key_provisions.map((provision, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-pe-text-secondary">
                      <span className="text-pe-text-tertiary mt-0.5">•</span>
                      {provision}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Legal text */}
            {selectedAdj.legal_reference.text && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-pe-text-primary mb-3">Legal Text</h4>
                <blockquote className="text-sm text-pe-text-secondary italic border-l-2 border-pe-gray-300 pl-4 py-2 bg-pe-gray-50 rounded-r-pe-lg">
                  "{selectedAdj.legal_reference.text}"
                </blockquote>
                <a
                  href={selectedAdj.legal_reference.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-pe-teal-600 hover:text-pe-teal-700 mt-2"
                >
                  Read full text on Cornell Law
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            )}

            {/* Variables used */}
            {selectedAdj.variables_used.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-pe-text-primary mb-3">PolicyEngine Variables</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAdj.variables_used.map((v) => (
                    <span key={v} className="px-2 py-1 bg-pe-teal-50 text-pe-teal-700 rounded-pe-sm text-xs font-mono">
                      {v}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Referenced by */}
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-pe-text-primary mb-3">Referenced By</h4>
              <div className="flex flex-wrap gap-2">
                {selectedAdj.referenced_by.map((ref) => (
                  <span key={ref} className="px-2 py-1 bg-pe-gray-100 text-pe-text-secondary rounded-pe-sm text-xs font-mono">
                    §{ref}
                  </span>
                ))}
              </div>
            </div>

            {/* Links */}
            <div className="flex gap-3">
              <a
                href={selectedAdj.legal_reference.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-pe-text-secondary hover:text-pe-text-primary py-2 px-3 bg-pe-gray-50 rounded-pe-md border border-pe-gray-200 hover:border-pe-gray-300 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                View Law
              </a>
              {selectedAdj.github_url && (
                <a
                  href={selectedAdj.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-pe-text-secondary hover:text-pe-text-primary py-2 px-3 bg-pe-gray-50 rounded-pe-md border border-pe-gray-200 hover:border-pe-gray-300 transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                  </svg>
                  View Code
                </a>
              )}
            </div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-pe-text-tertiary">
            <div className="text-center p-6">
              <svg className="w-12 h-12 mx-auto mb-3 text-pe-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              <p className="text-sm">Select a section to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const CodeMappingView = ({ structure }: { structure: QBIDLawStructure }) => {
  return (
    <div className="h-full overflow-y-auto p-6 bg-pe-gray-50">
      <div className="max-w-6xl mx-auto pb-6">
        <div className="bg-white rounded-pe-lg border border-pe-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-pe-gray-200">
            <h2 className="text-lg font-semibold text-pe-text-primary">Code-to-Law Mapping</h2>
            <p className="text-sm text-pe-text-tertiary mt-1">How each section of §199A maps to PolicyEngine implementation</p>
          </div>

          <table className="min-w-full divide-y divide-pe-gray-200">
            <thead className="bg-pe-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-pe-text-tertiary uppercase tracking-wide">
                  Section
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-pe-text-tertiary uppercase tracking-wide">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-pe-text-tertiary uppercase tracking-wide">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-pe-text-tertiary uppercase tracking-wide">
                  Variables
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-pe-text-tertiary uppercase tracking-wide">
                  Links
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-pe-gray-100">
              {structure.sections.map((section) => (
                <tr key={section.id} className="hover:bg-pe-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-mono text-sm text-pe-teal-600">{section.section_number}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-pe-text-primary">{section.title}</div>
                    {section.status_notes && (
                      <div className="text-xs text-pe-text-tertiary mt-1 max-w-xs">{section.status_notes}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={section.status} />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {section.variables_used.slice(0, 2).map((v) => (
                        <span key={v} className="inline-block px-2 py-0.5 bg-pe-gray-100 text-xs font-mono rounded-pe-sm text-pe-text-secondary">
                          {v.length > 25 ? v.slice(0, 25) + '...' : v}
                        </span>
                      ))}
                      {section.variables_used.length > 2 && (
                        <span className="text-xs text-pe-text-tertiary">+{section.variables_used.length - 2}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-3">
                      <a
                        href={section.legal_reference.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-pe-teal-600 hover:text-pe-teal-700"
                      >
                        Law
                      </a>
                      {section.github_url && (
                        <a
                          href={section.github_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-pe-text-secondary hover:text-pe-text-primary"
                        >
                          Code
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default function LawView() {
  const [viewMode, setViewMode] = useState<ViewMode>('flowchart');
  const [structure, setStructure] = useState<QBIDLawStructure | null>(null);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStructure();
  }, []);

  const fetchStructure = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/law/structure');
      setStructure(response.data);
    } catch (err) {
      setError('Failed to load law structure');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-pe-gray-50">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-pe-gray-300 border-t-pe-text-secondary rounded-full animate-spin mx-auto mb-3"></div>
          <div className="text-pe-text-tertiary">Loading §199A structure...</div>
        </div>
      </div>
    );
  }

  if (error || !structure) {
    return (
      <div className="flex items-center justify-center h-full bg-pe-gray-50">
        <div className="text-center">
          <div className="text-red-500 mb-2">Failed to load</div>
          <p className="text-pe-text-tertiary text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="border-b border-pe-gray-200 bg-white px-6">
        <nav className="flex gap-8" aria-label="Tabs">
          {[
            { id: 'flowchart', label: 'Law Flowchart' },
            { id: 'adjacent', label: 'Adjacent Sections' },
            { id: 'code-mapping', label: 'Code Mapping' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setViewMode(tab.id as ViewMode)}
              className={`py-4 border-b-2 text-sm font-medium transition-colors ${
                viewMode === tab.id
                  ? 'border-pe-text-primary text-pe-text-primary'
                  : 'border-transparent text-pe-text-tertiary hover:text-pe-text-secondary hover:border-pe-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'flowchart' && (
          <FlowchartView
            structure={structure}
            selectedSection={selectedSection}
            onSelectSection={setSelectedSection}
          />
        )}
        {viewMode === 'code-mapping' && <CodeMappingView structure={structure} />}
        {viewMode === 'adjacent' && <AdjacentSectionsView structure={structure} />}
      </div>
    </div>
  );
}
