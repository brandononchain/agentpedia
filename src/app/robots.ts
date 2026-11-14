import type { MetadataRoute } from "next";
import { SITE_ORIGIN } from "@/lib/site";

const AGENTS = [
  "*",
  "GPTBot",
  "ChatGPT-User",
  "OAI-SearchBot",
  "ClaudeBot",
  "Claude-SearchBot",
  "Claude-User",
  "PerplexityBot",
  "Perplexity-User",
  "Google-Extended",
  "Googlebot",
  "CCBot",
  "Applebot-Extended",
  "Applebot",
  "Bingbot",
  "Amazonbot",
  "Bytespider",
  "Meta-ExternalAgent",
  "DuckAssistBot",
  "cohere-ai",
];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: AGENTS.map((userAgent) => ({ userAgent, allow: "/" })),
    host: SITE_ORIGIN,
    sitemap: `${SITE_ORIGIN}/sitemap.xml`,
  };
}
