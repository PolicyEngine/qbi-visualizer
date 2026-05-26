import type { Metadata } from 'next';
import TaxFormView from '@/views/TaxFormView';

// Canonical must include the multizone basePath; without it, sub-pages
// inherit the homepage canonical from the root layout and end up
// de-indexed by search engines.
export const metadata: Metadata = {
  title: 'Tax forms | QBI Deduction Calculator (IRC §199A) | PolicyEngine',
  alternates: {
    canonical: 'https://qbi-visualizer.vercel.app/us/qbi-calculator/forms',
  },
};

export default function FormsPage() {
  return <TaxFormView />;
}
