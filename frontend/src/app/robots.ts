import type { MetadataRoute } from 'next';
import { BASE_PATH, SITE_URL } from '@/config/site';

// Served at `${BASE_PATH}/robots.txt` by Next; a basePath-false rewrite in
// next.config.ts also surfaces it at the origin root `/robots.txt`, which
// is the only place crawlers look for it.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/' },
    sitemap: `${SITE_URL}${BASE_PATH}/sitemap.xml`,
  };
}
