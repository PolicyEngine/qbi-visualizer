import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
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
