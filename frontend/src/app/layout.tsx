import type { Metadata, Viewport } from 'next';
import Header from './Header';
import './globals.css';

const SITE_URL = 'https://qbi-visualizer.vercel.app';
const TITLE = 'QBI Deduction Calculator (IRC §199A) | PolicyEngine';
const DESCRIPTION =
  'Free interactive Qualified Business Income Deduction calculator powered by PolicyEngine US. Models §199A phase-in, W-2 wage and UBIA limits, SSTB phase-out, and REIT/PTP income for any filing status and tax year.';
const OG_IMAGE = `${SITE_URL}/og-image.svg`;

const jsonLdGraph = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebApplication',
      name: 'QBI Deduction Calculator',
      alternateName: 'Section 199A Calculator',
      url: `${SITE_URL}/`,
      applicationCategory: 'FinanceApplication',
      operatingSystem: 'Any',
      description:
        'Interactive Qualified Business Income Deduction calculator under IRC §199A. Models phase-in, W-2 wage and UBIA limits, SSTB phase-out, and REIT/PTP income.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
      creator: {
        '@type': 'Organization',
        name: 'PolicyEngine',
        url: 'https://policyengine.org/',
      },
    },
    {
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'What is the QBI deduction?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'The Qualified Business Income (QBI) deduction is a 20% deduction on net income from pass-through businesses created by IRC §199A. It is available to sole proprietors, partnerships, S-corporations, and certain trusts and estates.',
          },
        },
        {
          '@type': 'Question',
          name: 'Who qualifies for the §199A deduction?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Owners of a qualified trade or business (a §162 trade or business other than the trade or business of being an employee) with taxable income above zero. Above the §199A(e) threshold, additional W-2 wage and UBIA limitations apply, and Specified Service Trades or Businesses (SSTBs) phase out.',
          },
        },
        {
          '@type': 'Question',
          name: 'What is an SSTB?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'A Specified Service Trade or Business under §199A(d)(2) — health, law, accounting, actuarial, performing arts, consulting, athletics, financial / brokerage services, investing, or any business whose principal asset is the reputation or skill of its owners. SSTB income phases out above the threshold.',
          },
        },
        {
          '@type': 'Question',
          name: 'What are the W-2 wage and UBIA limits?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Above the threshold, the QBI component for each business is capped at the greater of (a) 50% of W-2 wages paid by the business, or (b) 25% of W-2 wages plus 2.5% of the unadjusted basis immediately after acquisition (UBIA) of qualified property — see §199A(b)(2)(B).',
          },
        },
        {
          '@type': 'Question',
          name: 'What is the difference between Form 8995 and Form 8995-A?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Form 8995 is the simplified form for filers with taxable income below the §199A threshold. Form 8995-A is the longer form required when taxable income exceeds the threshold and the wage / UBIA limits or SSTB phase-out apply.',
          },
        },
      ],
    },
  ],
};

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  authors: [{ name: 'PolicyEngine' }],
  alternates: { canonical: `${SITE_URL}/` },
  openGraph: {
    type: 'website',
    title: 'QBI Deduction Calculator (IRC §199A)',
    description:
      'Free interactive Qualified Business Income Deduction calculator powered by PolicyEngine US. Models phase-in, W-2 wage and UBIA limits, and SSTB phase-out.',
    url: `${SITE_URL}/`,
    siteName: 'PolicyEngine',
    images: [{ url: OG_IMAGE }],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@PolicyEngine',
    title: 'QBI Deduction Calculator (IRC §199A)',
    description:
      'Free interactive Qualified Business Income Deduction calculator powered by PolicyEngine US.',
    images: [{ url: OG_IMAGE }],
  },
  icons: {
    icon: '/favicon.svg',
    apple: '/favicon.svg',
  },
};

export const viewport: Viewport = {
  themeColor: '#2C6496',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdGraph) }}
        />
      </head>
      <body>
        <div className="App flex flex-col h-screen bg-pe-bg-primary">
          <Header />
          <main className="flex-1 overflow-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}
