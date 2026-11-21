import { shelfList } from "@/lib/brain/detail";
import { etagForIndex, jsonBody, withBrain } from "@/lib/brain/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export function GET(request: Request) {
  return withBrain(request, { cache: "name" }, () => {
    if (request.headers.get("if-none-match") === etagForIndex()) return new Response(null, { status: 304 });
    return jsonBody({ shelves: shelfList() });
  });
}
