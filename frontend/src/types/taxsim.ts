// Types for TAXSIM comparison

export interface TaxsimInputVariable {
  number: number;
  name: string;
  description: string;
  qbi_related: boolean;
}

export interface TaxsimCodeBlock {
  file: string;
  line_start: number;
  line_end: number;
  code: string;
  description: string;
  variables_used: string[];
}

export interface PolicyEngineCodeBlock {
  file: string;
  variable_name: string;
  code: string;
  description: string;
  github_url?: string;
}

export interface ComparisonItem {
  id: string;
  law_section: string;
  description: string;
  taxsim_approach: string;
  policyengine_approach: string;
  taxsim_code?: TaxsimCodeBlock;
  policyengine_code?: PolicyEngineCodeBlock;
  difference: string;
  severity: 'none' | 'minor' | 'significant' | 'critical';
}

export interface TaxsimQBIImplementation {
  version: string;
  source_file: string;
  qbi_variables: TaxsimInputVariable[];
  code_blocks: TaxsimCodeBlock[];
  key_features: string[];
  limitations: string[];
}

export interface PolicyEngineQBIImplementation {
  version: string;
  main_variable: string;
  dependent_variables: string[];
  code_blocks: PolicyEngineCodeBlock[];
  key_features: string[];
  limitations: string[];
}

export interface AdjacentSectionCoverage {
  section_id: string;
  section_number: string;
  title: string;
  taxsim_status: 'complete' | 'partial' | 'missing' | 'not_applicable';
  taxsim_notes: string;
  policyengine_status: 'complete' | 'partial' | 'missing' | 'not_applicable';
  policyengine_notes: string;
  impact_on_qbid: string;
}

export interface ComparisonResult {
  taxsim: TaxsimQBIImplementation;
  policyengine: PolicyEngineQBIImplementation;
  comparisons: ComparisonItem[];
  adjacent_section_coverage: AdjacentSectionCoverage[];
  summary: {
    none: number;
    minor: number;
    significant: number;
    critical: number;
  };
  methodology_differences: string[];
}

export interface CalculationStep {
  name: string;
  value: number;
}

export interface CalculationComparisonInput {
  self_employment_income: number;
  partnership_s_corp_income: number;
  sstb_income: number;
  rental_income: number;
  filing_status: string;
  taxable_income: number;
  w2_wages: number;
  property_basis: number;
  capital_gains: number;
  year: number;
}

export interface CalculationComparisonResult {
  policyengine_result: number;
  taxsim_result: number;
  difference: number;
  difference_pct: number | null;
  policyengine_steps: CalculationStep[];
  taxsim_steps: CalculationStep[];
  notes: string[];
}
