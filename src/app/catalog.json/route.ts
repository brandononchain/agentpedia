import { catalog } from "@/lib/catalog";

export const dynamic = "force-static";

export function GET() {
  return new Response(JSON.stringify(catalog), {
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}
