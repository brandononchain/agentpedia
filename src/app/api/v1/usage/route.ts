import { usageBody, withBrain, jsonBody } from "@/lib/brain/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export function GET(request: Request) {
  return withBrain(request, { cache: "none", etag: false }, (guard) => jsonBody(usageBody(guard, guard.usage)));
}
