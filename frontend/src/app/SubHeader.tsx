'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * Tool brand bar shown directly under the PolicyEngine multi-zone shell.
 * Same layout the standalone qbi-visualizer had before the multizone
 * migration: PE wordmark, vertical rule, QBID title + §199A subtitle,
 * tool tab on the right.
 */
export default function SubHeader() {
  const pathname = usePathname() || '/';
  const isActive = pathname === '/';

  return (
    <div className="bg-white border-b border-pe-gray-200 px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center">
            {/* next/image auto-prefixes the multizone basePath for
             * root-relative paths, so the raw `/policyengine-logo.png`
             * resolves under `/us/qbi-calculator/...`. */}
            <Image
              src="/policyengine-logo.png"
              alt="PolicyEngine"
              width={154}
              height={32}
              className="h-8 w-auto"
              priority
            />
          </Link>
          <div className="border-l border-pe-gray-200 pl-4">
            <h1 className="text-lg font-semibold text-pe-text-primary">
              Qualified Business Income Deduction
            </h1>
            <p className="text-xs text-pe-text-tertiary">26 U.S.C. &sect; 199A</p>
          </div>
        </div>
        <div
          role="tablist"
          aria-label="Application views"
          className="flex gap-1 bg-pe-gray-100 p-1 rounded-pe-lg"
        >
          <Link
            role="tab"
            aria-selected={isActive}
            href="/"
            className={`px-4 py-2 rounded-pe-md text-sm font-medium transition-all ${
              isActive
                ? 'bg-white text-pe-text-primary shadow-sm'
                : 'text-pe-text-secondary hover:text-pe-text-primary'
            }`}
          >
            QBID calculator
          </Link>
        </div>
      </div>
    </div>
  );
}
