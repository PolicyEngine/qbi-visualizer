import type { NextConfig } from 'next';

const basePath =
  process.env.NEXT_PUBLIC_BASE_PATH === ''
    ? undefined
    : process.env.NEXT_PUBLIC_BASE_PATH || '/us/qbi-calculator';

const nextConfig: NextConfig = {
  ...(basePath ? { basePath } : {}),
  turbopack: {
    root: process.cwd(),
  },
  // Proxy /api requests to the FastAPI backend in development.
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      const target = process.env.NEXT_PUBLIC_API_TARGET || 'http://localhost:8000';
      return [{ source: '/api/:path*', destination: `${target}/api/:path*` }];
    }
    return [];
  },
};

export default nextConfig;
