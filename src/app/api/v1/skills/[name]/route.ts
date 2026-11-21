import { digestMatches, entryDetail, findEntry } from "@/lib/brain/detail";
import { brainError, etagForIndex, jsonBody, withBrain } from "@/lib/brain/http";
import { wantsFiles } from "@/lib/brain/query";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export function GET(request: Request, context: { params: Promise<{ name: string }> }) {
  const url = new URL(request.url);
  const digest = url.searchParams.get("digest");
  return withBrain(request, { cache: digest ? "digest" : "name" }, async () => {
    const { name } = await context.params;
    const entry = findEntry("skill", name);
    if (!entry) return brainError(404, "not_found", `No served skill named ${name}.`);
    if (!digestMatches(entry, digest)) {
      return brainError(404, "digest_mismatch", `The pinned digest does not match the current skill ${name}.`);
    }
    if (request.headers.get("if-none-match") === etagForIndex()) return new Response(null, { status: 304 });
    const body = entryDetail(entry, { includeFiles: wantsFiles(url) });
    if (!body) return brainError(404, "not_found", `No served skill named ${name}.`);
    return jsonBody(body);
  });
}
