import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Not found | QBI Deduction Calculator (IRC §199A) | PolicyEngine',
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center max-w-md p-8">
        <p className="text-sm font-mono text-pe-text-tertiary mb-2">404</p>
        <h2 className="text-2xl font-semibold text-pe-text-primary mb-3">Page not found</h2>
        <p className="text-sm text-pe-text-secondary mb-6">
          The page you&apos;re looking for doesn&apos;t exist. Try the QBID calculator instead.
        </p>
        <Link
          href="/"
          className="inline-block px-4 py-2 bg-pe-teal-500 text-white rounded-pe-lg font-medium hover:bg-pe-teal-600 transition-colors"
        >
          Go to calculator
        </Link>
      </div>
    </div>
  );
}
