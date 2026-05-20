import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  basePath: '/us/qbi-calculator',
  turbopack: {
    root: process.cwd(),
  },
  // Proxy /api requests to the FastAPI backend. Vercel ignores vercel.json
  // rewrites for Next.js projects, so the production proxy lives here too.
  async rewrites() {
    const target =
      process.env.NODE_ENV === 'development'
        ? process.env.NEXT_PUBLIC_API_TARGET || 'http://localhost:8000'
        : 'https://policyengine--qbi-visualizer-backend-web.modal.run';
    return [{ source: '/api/:path*', destination: `${target}/api/:path*` }];
  },
};

export default nextConfig;
