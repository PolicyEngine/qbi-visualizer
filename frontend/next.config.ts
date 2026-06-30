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
  // The app is served under basePath, so the bare domain root has nothing.
  // Redirect it to the app so the standalone Vercel URL isn't a dead 404.
  // basePath: false keeps the source matched at the true origin root.
  async redirects() {
    return [
      {
        source: '/',
        destination: '/us/qbi-calculator',
        basePath: false,
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
