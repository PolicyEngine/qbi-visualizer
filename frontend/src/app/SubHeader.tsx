'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { href: '/', label: 'QBID calculator' },
  { href: '/law', label: 'Law structure' },
  { href: '/forms', label: 'Tax forms' },
] as const;

/**
 * Tool brand bar shown directly under the PolicyEngine multi-zone shell.
 * Same layout the standalone qbi-visualizer had before the multizone
 * migration: PE wordmark, vertical rule, QBID title + §199A subtitle,
 * tool navigation on the right.
 */
export default function SubHeader() {
  const pathname = usePathname() || '/';

  return (
    <div className="bg-white border-b border-pe-gray-200 px-4 sm:px-6 py-4">
      <div className="flex flex-wrap items-center justify-between gap-3 max-w-7xl mx-auto">
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
        <nav
          aria-label="Application views"
          className="flex gap-1 bg-pe-gray-100 p-1 rounded-pe-lg"
        >
          {NAV_ITEMS.map(({ href, label }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                aria-current={isActive ? 'page' : undefined}
                className={`px-4 py-2 rounded-pe-md text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-white text-pe-text-primary shadow-sm'
                    : 'text-pe-text-secondary hover:text-pe-text-primary'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
