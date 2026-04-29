// Types for law-structured QBID visualization

export type ImplementationStatus = 'complete' | 'partial' | 'missing' | 'not_applicable';

export interface LegalReference {
  section: string;
  title: string;
  url: string;
  text?: string;
}

export interface InputVariable {
  name: string;
  label: string;
  description?: string;
  unit?: string;
  default_value?: number;
  current_value?: number;
  github_url?: string;
}

export interface Parameter {
  name: string;
  label: string;
  value: any;
  unit?: string;
  year?: number;
  filing_status?: string;
  github_url?: string;
}

export interface ComputationStep {
  id: string;
  description: string;
  formula?: string;
  formula_latex?: string;
  inputs: string[];
  output?: string;
  code_reference?: string;
  github_url?: string;
}

export interface DecisionPoint {
  id: string;
  condition: string;
  condition_formula?: string;
  true_branch: string;
  false_branch: string;
  threshold_values?: Record<string, number>;
}

export interface LawSection {
  id: string;
  section_number: string;
  title: string;
  description: string;
  legal_reference: LegalReference;
  status: ImplementationStatus;
  status_notes?: string;
  inputs: InputVariable[];
  parameters: Parameter[];
  steps: ComputationStep[];
  decisions: DecisionPoint[];
  variables_used: string[];
  formula_source?: string;
  github_url?: string;
  next_sections: string[];
  depends_on: string[];
  is_adjacent?: boolean;
  parent_section?: string;
}

export interface AdjacentSection {
  id: string;
  section_number: string;
  title: string;
  description: string;
  relevance_to_qbid: string;
  legal_reference: LegalReference;
  status: ImplementationStatus;
  status_notes?: string;
  key_provisions: string[];
  variables_used: string[];
  github_url?: string;
  referenced_by: string[];
}

export interface QBIDLawStructure {
  title: string;
  effective_date: string;
  sunset_date?: string;
  total_sections: number;
  implemented_sections: number;
  partial_sections: number;
  missing_sections: number;
  sections: LawSection[];
  adjacent_sections: AdjacentSection[];
  computation_order: string[];
  policyengine_commit?: string;
  last_updated?: string;
}

