import { limitHeaders, retryAfterSeconds, type GuardResult, type LimitSnapshot } from "@/lib/brain/guard";
import { guardRequest } from "@/lib/brain/guard";
import { loadBrainIndex } from "@/lib/brain/index";

export function brainError(status: number, code: string, message: string, extra?: Headers) {
  const headers = extra ?? new Headers();
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("cache-control", "private, no-store");
  return new Response(JSON.stringify({ error: { code, message } }), { status, headers });
}

export function etagForIndex() {
  return `"${loadBrainIndex().version}"`;
}

function apply(headers: Headers, guard: Extract<GuardResult, { ok: true }>, cache: string | null, etag: string | null) {
  const limits = limitHeaders(guard.limit, guard.usage);
  limits.forEach((value, key) => headers.set(key, value));
  if (cache) headers.set("cache-control", cache);
  if (etag) headers.set("etag", etag);
  headers.set("x-brain-plan", guard.identity.plan);
  if (guard.identity.org) headers.set("x-brain-org", guard.identity.org);
}

export async function withBrain(
  request: Request,
  options: { cache?: "digest" | "name" | "none"; etag?: boolean },
  run: (guard: Extract<GuardResult, { ok: true }>) => Promise<Response> | Response,
) {
  const guard = await guardRequest(request);
  if (!guard.ok) {
    const headers = guard.limit ? limitHeaders(guard.limit, guard.limit) : new Headers();
    if (guard.limit) headers.set("retry-after", retryAfterSeconds(guard.limit));
    return brainError(guard.status, guard.code, guard.message, headers);
  }

  const etag = options.etag === false ? null : etagForIndex();
  const response = await run(guard);
  const headers = new Headers(response.headers);
  const cacheable = response.status === 200 || response.status === 304;
  apply(headers, guard, cacheable ? cacheControl(options.cache) : "private, no-store", etag);
  return new Response(response.body, { status: response.status, headers });
}

function cacheControl(mode: "digest" | "name" | "none" | undefined) {
  if (mode === "digest") return "public, max-age=31536000, immutable";
  if (mode === "name") return "public, s-maxage=300, stale-while-revalidate=300";
  return "private, no-store";
}

export function jsonBody(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

export function usageBody(guard: Extract<GuardResult, { ok: true }>, usage: LimitSnapshot) {
  return {
    org: guard.identity.org,
    plan: guard.identity.plan,
    limit: usage.limit,
    used: usage.used,
    remaining: usage.remaining,
    window: usage.window,
    reset: new Date(usage.reset).toISOString(),
  };
}
