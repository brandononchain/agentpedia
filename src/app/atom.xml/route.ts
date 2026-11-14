import { atomXml } from "@/lib/machine";

export const dynamic = "force-static";

export function GET() {
  return new Response(atomXml(), {
    headers: { "content-type": "application/atom+xml; charset=utf-8" },
  });
}
