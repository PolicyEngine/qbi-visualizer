import type { Metadata } from 'next';
import TaxFormView from '@/views/TaxFormView';

export const metadata: Metadata = {
  title: 'Tax forms | QBI Deduction Calculator (IRC §199A) | PolicyEngine',
};

export default function FormsPage() {
  return <TaxFormView />;
}
