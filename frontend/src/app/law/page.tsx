import type { Metadata } from 'next';
import LawView from '@/views/LawView';

export const metadata: Metadata = {
  title: 'Law structure | QBI Deduction Calculator (IRC §199A) | PolicyEngine',
};

export default function LawPage() {
  return <LawView />;
}
