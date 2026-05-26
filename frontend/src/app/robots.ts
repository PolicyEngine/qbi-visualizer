import type { MetadataRoute } from 'next';

const SITE_URL = 'https://qbi-visualizer.vercel.app';
const BASE_PATH = '/us/qbi-calculator';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/' },
    sitemap: `${SITE_URL}${BASE_PATH}/sitemap.xml`,
  };
}
