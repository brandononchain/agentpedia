import { rssXml } from "@/lib/machine";

export const dynamic = "force-static";

export function GET() {
  return new Response(rssXml(), {
    headers: { "content-type": "application/rss+xml; charset=utf-8" },
  });
}
