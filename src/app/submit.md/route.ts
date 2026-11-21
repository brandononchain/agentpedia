import { submitMarkdown } from "@/lib/submit-spec";

export const dynamic = "force-static";

export function GET() {
  return new Response(submitMarkdown(), {
    headers: { "content-type": "text/markdown; charset=utf-8" },
  });
}
