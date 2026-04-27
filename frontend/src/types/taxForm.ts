// Types for tax form mapping

export type FormImplementationStatus = 'complete' | 'partial' | 'missing' | 'not_applicable';

export interface FormLineMapping {
  line_number: string;
  line_label: string;
  description: string;
  status: FormImplementationStatus;
  pe_variable?: string;
  pe_formula?: string;
  gap_description?: string;
  form_instructions?: string;
}

export interface FormScheduleMapping {
  schedule_id: string;
  schedule_name: string;
  description: string;
  who_must_file: string;
  status: FormImplementationStatus;
  status_notes: string;
  lines: FormLineMapping[];
  key_requirements: string[];
}

export interface TaxFormMapping {
  form_number: string;
  form_title: string;
  tax_year: number;
  description: string;
  who_can_use: string;
  threshold_single: number;
  threshold_joint: number;
  irs_url: string;
  instructions_url: string;
  total_lines: number;
  complete_lines: number;
  partial_lines: number;
  missing_lines: number;
  lines: FormLineMapping[];
  schedules: FormScheduleMapping[];
}

export interface CriticalGap {
  id: string;
  title: string;
  form_lines: string;
  description: string;
  impact: string;
  fix_complexity: string;
}

export interface WorkingCorrectly {
  id: string;
  title: string;
  form_lines: string;
  description: string;
}

export interface FormMappingResponse {
  forms: TaxFormMapping[];
  summary: {
    total_elements: number;
    complete: number;
    partial: number;
    missing: number;
    implementation_pct: number;
  };
  critical_gaps: CriticalGap[];
  working_correctly: WorkingCorrectly[];
}
