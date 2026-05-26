import type { MetadataRoute } from 'next';

/**
 * Dynamic sitemap.
 *
 * URLs MUST include the multizone `basePath` (`/us/qbi-calculator`) — the
 * app is only reachable under that prefix. Without it, crawlers hit the
 * Vercel host root and `/law` / `/forms`, which all return 404.
 *
 * `next.config.ts#basePath` is not surfaced via a public API at build
 * time, so the prefix is duplicated here. Keep this constant in sync
 * with the one in `next.config.ts` and `src/utils/api.ts`.
 */
const SITE_URL = 'https://qbi-visualizer.vercel.app';
const BASE_PATH = '/us/qbi-calculator';

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
