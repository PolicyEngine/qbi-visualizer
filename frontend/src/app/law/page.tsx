import type { Metadata } from 'next';
import LawView from '@/views/LawView';

// Canonical must include the multizone basePath; without it, sub-pages
// inherit the homepage canonical from the root layout and end up
// de-indexed by search engines.
export const metadata: Metadata = {
  title: 'Law structure | QBI Deduction Calculator (IRC §199A) | PolicyEngine',
  alternates: {
    canonical: 'https://qbi-visualizer.vercel.app/us/qbi-calculator/law',
  },
};

export default function LawPage() {
  return <LawView />;
}
