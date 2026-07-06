import type { NextConfig } from 'next';
import { BASE_PATH } from './src/config/site';

// Production backend on Modal. Override per environment (previews,
// staging, local `next start`) by setting API_TARGET in Vercel — the
// value is only used server-side in the rewrite below, so it does not
// need the NEXT_PUBLIC_ prefix.
const DEFAULT_PROD_API_TARGET =
  'https://policyengine--qbi-visualizer-backend-web.modal.run';

const nextConfig: NextConfig = {
  basePath: BASE_PATH,
  turbopack: {
    root: process.cwd(),
  },
  // Proxy /api requests to the FastAPI backend. Vercel ignores vercel.json
  // rewrites for Next.js projects, so the production proxy lives here too.
  async rewrites() {
    const target =
      process.env.API_TARGET ??
      (process.env.NODE_ENV === 'development'
        ? 'http://localhost:8000'
        : DEFAULT_PROD_API_TARGET);
    return [{ source: '/api/:path*', destination: `${target}/api/:path*` }];
  },
  // The app is served under basePath, so the bare domain root has nothing.
  // Redirect it to the app so the standalone Vercel URL isn't a dead 404.
  // basePath: false keeps the source matched at the true origin root.
  async redirects() {
    return [
      {
        source: '/',
        destination: BASE_PATH,
        basePath: false,
        permanent: true,
      },
      // Crawlers only ever fetch /robots.txt at the origin root, but the
      // app (and its robots route) lives under the basePath. Redirect the
      // root path to it — robots.txt fetchers follow redirects — so the
      // sitemap declaration is actually seen. (A basePath-false rewrite
      // can't do this: Next only allows external destinations there.)
      {
        source: '/robots.txt',
        destination: `${BASE_PATH}/robots.txt`,
        basePath: false,
        permanent: true,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
          // The tool is intentionally iframe-embeddable from policyengine.org,
          // so allowlist frame ancestors instead of denying framing outright.
          {
            key: 'Content-Security-Policy',
            value:
              "frame-ancestors 'self' https://policyengine.org https://*.policyengine.org",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
