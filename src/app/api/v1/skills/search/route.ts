import { jsonBody, withBrain } from "@/lib/brain/http";
import { parseSearchParams } from "@/lib/brain/query";
import { searchEntries } from "@/lib/brain/search";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export function GET(request: Request) {
  return withBrain(request, { cache: "name" }, () => {
    const parsed = parseSearchParams(new URL(request.url));
    if (!parsed.ok) return parsed.response;
    const results = searchEntries({
      query: parsed.query,
      kind: parsed.kind,
      shelf: parsed.shelf,
      minTier: parsed.minTier,
      minGrade: parsed.minGrade,
      limit: parsed.limit,
    });
    return jsonBody({ query: parsed.query, results });
  });
}
