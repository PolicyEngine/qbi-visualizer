import { ImageResponse } from 'next/og';

export const runtime = 'nodejs';
// Statically generated at build time so social crawlers hit a CDN cache.
export const dynamic = 'force-static';

const SIZE = { width: 1200, height: 630 } as const;

/**
 * Open Graph / Twitter card image rendered as a real PNG (1200x630) so
 * social platforms that reject SVG OG (Twitter, LinkedIn, Slack,
 * iMessage) display it correctly.
 *
 * We expose this as an explicit route — rather than the
 * `opengraph-image.tsx` file convention — because Next.js's auto-emitted
 * `og:image` tag resolves the file-convention URL against `metadataBase`
 * and omits the multizone basePath, so crawlers would 404. By owning
 * the route here we can pin the `og:image` URL to the basePath-aware
 * absolute URL in `layout.tsx`.
 */
export async function GET() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          backgroundColor: '#2C6496',
          padding: '80px',
          color: '#ffffff',
          fontFamily: 'sans-serif',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: 8,
              backgroundColor: '#ffffff',
              color: '#2C6496',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 44,
              fontWeight: 700,
            }}
          >
            P
          </div>
          <div
            style={{
              marginLeft: 24,
              fontSize: 28,
              fontWeight: 500,
              color: '#9CC8E8',
            }}
          >
            PolicyEngine US
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontSize: 88, fontWeight: 700, lineHeight: 1.05 }}>
            QBI Deduction
          </div>
          <div style={{ fontSize: 88, fontWeight: 700, lineHeight: 1.05 }}>
            Calculator
          </div>
          <div
            style={{
              marginTop: 32,
              fontSize: 36,
              fontWeight: 500,
              color: '#9CC8E8',
            }}
          >
            26 U.S.C. § 199A
          </div>
        </div>

        <div style={{ fontSize: 24, color: '#9CC8E8' }}>
          policyengine.org/us/qbi-calculator
        </div>
      </div>
    ),
    { ...SIZE },
  );
}
