/**
 * Single source of truth for the multizone base path and public site URL.
 *
 * `BASE_PATH` must match `basePath` in `next.config.ts` (which imports it
 * from here, so there is exactly one definition). The app is only reachable
 * under this prefix — canonicals, the sitemap, robots, and API/asset URLs
 * all need it.
 *
 * `SITE_URL` is the host used for canonical/OG/sitemap URLs. policyengine.org
 * serves this zone at `BASE_PATH` through policyengine-app-v2's rewrite, so it
 * defaults to that public host, never the Vercel deployment. Override it per
 * environment with `NEXT_PUBLIC_SITE_URL`.
 */
export const BASE_PATH = '/us/qbi-calculator';

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://policyengine.org';
