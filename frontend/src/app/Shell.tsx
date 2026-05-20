'use client';

import { Header } from '@policyengine/ui-kit/layout';
import type { NavItemConfig, CountryConfig } from '@policyengine/ui-kit/layout';

const NAV_ITEMS: NavItemConfig[] = [
  { label: 'Research', href: 'https://policyengine.org/us/research' },
  { label: 'Model', href: 'https://policyengine.org/us/model' },
  { label: 'API', href: 'https://policyengine.org/us/api' },
  { label: 'Python', href: 'https://policyengine.org/us/python' },
  {
    label: 'About',
    href: 'https://policyengine.org/us/team',
    children: [
      { label: 'Team', href: 'https://policyengine.org/us/team' },
      { label: 'Supporters', href: 'https://policyengine.org/us/supporters' },
    ],
  },
  { label: 'Donate', href: 'https://policyengine.org/us/donate' },
];

const COUNTRIES: CountryConfig[] = [
  { id: 'us', label: 'United States' },
  { id: 'uk', label: 'United Kingdom' },
];

export function ShellHeader() {
  return (
    <Header
      navItems={NAV_ITEMS}
      countries={COUNTRIES}
      currentCountry="us"
      logoHref="https://policyengine.org/us"
      onCountryChange={(id) => {
        window.location.href = `https://policyengine.org/${id}`;
      }}
    />
  );
}
