import { BASE_PATH } from '@/config/site';

/**
 * Prepend the multizone `basePath` to a root-relative URL.
 *
 * When the app is served under a basePath (e.g. `/us/qbi-calculator`),
 * raw fetch/img URLs that start with `/` resolve against the page
 * origin without the prefix, bypassing the host's multizone rewrite
 * that proxies the embed traffic. Use these helpers anywhere that
 * needs to reach an API endpoint or a static asset by path.
 */
function withBasePath(path: string): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  return `${BASE_PATH}${clean}`;
}

export const apiUrl = withBasePath;
export const assetUrl = withBasePath;
