import type { Metadata } from "next";
import siteConfig from "../../config/site.json";

/** Display name. The site reads this string. */
export const SITE_NAME = "Agentpedia";

export const SITE_TAGLINE = "The open encyclopedia of agents and skills";

export const REPO_URL = "https://github.com/brandononchain/agentpedia";

function trimOrigin(value: string) {
  return value.trim().replace(/\/$/, "");
}

/**
 * Public origin for canonical URLs, the sitemap, Open Graph, badge embeds,
 * and certificate records. The default is config/site.json.
 * Set NEXT_PUBLIC_SITE_URL to override it.
 */
export const SITE_ORIGIN = trimOrigin(process.env.NEXT_PUBLIC_SITE_URL || siteConfig.origin);

/** Relative canonical and Open Graph URL. metadataBase resolves them against SITE_ORIGIN. */
export function siteMeta(path: string): Pick<Metadata, "alternates" | "openGraph"> {
  return {
    alternates: { canonical: path },
    openGraph: {
      url: path,
      images: [
        {
          url: "/og.png",
          width: 1200,
          height: 630,
          alt: `${SITE_NAME}. ${SITE_TAGLINE}`,
        },
      ],
    },
  };
}
