import type { Metadata } from "next";
import siteConfig from "../../config/site.json";

/** Display name. The site reads this string. */
export const SITE_NAME = "Agentpedia";

export const SITE_TAGLINE = "The reference encyclopedia of agent skills and agents.";

function trimOrigin(value: string) {
  return value.trim().replace(/\/$/, "");
}

/**
 * Public origin for canonical URLs, the sitemap, Open Graph, and embeds.
 * The default is config/site.json. Set NEXT_PUBLIC_SITE_URL to override it.
 */
export const SITE_ORIGIN = trimOrigin(process.env.NEXT_PUBLIC_SITE_URL || siteConfig.origin);

/** Relative canonical and Open Graph URL. metadataBase resolves them against SITE_ORIGIN. */
export function siteMeta(path: string): Pick<Metadata, "alternates" | "openGraph"> {
  return {
    alternates: { canonical: path },
    openGraph: { url: path },
  };
}
