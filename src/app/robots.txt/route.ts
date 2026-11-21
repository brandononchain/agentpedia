import { SITE_ORIGIN } from "@/lib/site";

export const dynamic = "force-static";

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

export function GET() {
  const groups = AGENTS.map((userAgent) => `User-agent: ${userAgent}\nAllow: /`).join("\n\n");
  const body = `${groups}\n\nHost: ${SITE_ORIGIN}\nSitemap: ${SITE_ORIGIN}/sitemap.xml\n# llms.txt: ${SITE_ORIGIN}/llms.txt\n`;
  return new Response(body, {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}
