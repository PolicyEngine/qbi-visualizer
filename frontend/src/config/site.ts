/**
 * Single source of truth for the multizone base path and public site URL.
 *
 * `BASE_PATH` must match `basePath` in `next.config.ts` (which imports it
 * from here, so there is exactly one definition). The app is only reachable
 * under this prefix — canonicals, the sitemap, robots, and API/asset URLs
 * all need it.
 *
 * `SITE_URL` is the host used for canonical/OG/sitemap URLs. Override it
 * per environment with `NEXT_PUBLIC_SITE_URL` (e.g. set it to
 * `https://policyengine.org` once the multizone mount on policyengine.org
 * is live, so ranking signal consolidates on the real public host).
 */
export const BASE_PATH = '/us/qbi-calculator';

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://qbi-visualizer.vercel.app';
