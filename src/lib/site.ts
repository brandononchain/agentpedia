import type { Metadata } from "next";
import siteConfig from "../../config/site.json";

/** Display name. The site reads this string. */
export const SITE_NAME = "Agentpedia";

export const SITE_TAGLINE = "The open encyclopedia of agents and skills";

export const REPO_URL = "https://github.com/brandononchain/agentpedia";

export const TWITTER_HANDLE = "@brandononchain";

export const ORGANIZATION_SAME_AS = [
  REPO_URL,
  "https://x.com/brandononchain",
  "https://brandononchain.com",
];

function trimOrigin(value: string) {
  return value.trim().replace(/\/$/, "");
}

/**
 * Public origin for canonical URLs, the sitemap, Open Graph, badge embeds,
 * and certificate records. The default is config/site.json.
 * Set NEXT_PUBLIC_SITE_URL to override it.
 */
export const SITE_ORIGIN = trimOrigin(process.env.NEXT_PUBLIC_SITE_URL || siteConfig.origin);

export function absoluteUrl(path: string) {
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${SITE_ORIGIN}${suffix}`;
}

type PageMetaOptions = {
  title?: string;
  absoluteTitle?: string;
  description?: string;
  keywords?: string[];
  image?: string;
  imageAlt?: string;
  noindex?: boolean;
  /** Preferred URL when this page should consolidate to another, such as a chapter to its book. */
  canonicalPath?: string;
  openGraphType?: "website" | "article";
  publishedTime?: string;
  modifiedTime?: string;
};

/** Canonical, social, and robots tags for one page. Titles use the layout template unless absoluteTitle is set. */
export function siteMeta(path: string, options: PageMetaOptions = {}): Metadata {
  const url = absoluteUrl(options.canonicalPath ?? path);
  const fullTitle = options.absoluteTitle ?? (options.title ? `${options.title} · ${SITE_NAME}` : undefined);
  const image = options.image ?? "/og.png";
  const imageAlt = options.imageAlt ?? `${SITE_NAME}. ${SITE_TAGLINE}`;
  const images = [{ url: image, width: 1200, height: 630, alt: imageAlt }];
  const openGraph: Metadata["openGraph"] =
    options.openGraphType === "article"
      ? {
          type: "article",
          siteName: SITE_NAME,
          url,
          title: fullTitle,
          description: options.description,
          images,
          publishedTime: options.publishedTime,
          modifiedTime: options.modifiedTime,
        }
      : {
          type: "website",
          siteName: SITE_NAME,
          url,
          title: fullTitle,
          description: options.description,
          images,
        };
  const metadata: Metadata = {
    alternates: {
      canonical: url,
      languages: { en: url },
      types: {
        "application/rss+xml": absoluteUrl("/feed.xml"),
        "application/atom+xml": absoluteUrl("/atom.xml"),
      },
    },
    robots: options.noindex
      ? { index: false, follow: false }
      : { index: true, follow: true, googleBot: { index: true, follow: true, "max-image-preview": "large" } },
    openGraph,
    twitter: {
      card: "summary_large_image",
      site: TWITTER_HANDLE,
      creator: TWITTER_HANDLE,
      title: fullTitle,
      description: options.description,
      images: [image],
    },
  };
  if (options.absoluteTitle) metadata.title = { absolute: options.absoluteTitle };
  else if (options.title) metadata.title = options.title;
  if (options.description) metadata.description = options.description;
  if (options.keywords?.length) metadata.keywords = options.keywords;
  return metadata;
}
