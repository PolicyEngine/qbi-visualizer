import type { MetadataRoute } from 'next';
import { BASE_PATH, SITE_URL } from '@/config/site';

/**
 * Dynamic sitemap.
 *
 * URLs MUST include the multizone `basePath` (`/us/qbi-calculator`) — the
 * app is only reachable under that prefix. Without it, crawlers hit the
 * Vercel host root and `/law` / `/forms`, which all return 404.
 */

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();
  const base = `${SITE_URL}${BASE_PATH}`;

  return [
    {
      url: `${base}/`,
      lastModified,
      changeFrequency: 'monthly',
      priority: 1.0,
    },
    {
      url: `${base}/law`,
      lastModified,
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    {
      url: `${base}/forms`,
      lastModified,
      changeFrequency: 'monthly',
      priority: 0.6,
    },
  ];
}
