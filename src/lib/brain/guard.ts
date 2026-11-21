import { createHash } from "node:crypto";
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";
import { ANON_DAILY_LIMIT, isPlan, monthlyLimit, yyyymm, type PlanId } from "@/lib/brain/plans";

export type KeyRecord = {
  org: string;
  plan: PlanId;
  created: string;
  last_used: string | null;
  scopes: string[];
  monthlyLimit?: number;
  revoked?: boolean;
};

export type LimitSnapshot = {
  ok: boolean;
  name: "daily" | "monthly" | "sliding";
  limit: number;
  remaining: number;
  reset: number;
  used: number;
  window: "day" | "month";
};

export type GuardIdentity =
  | { kind: "anonymous"; ip: string; org: null; plan: "anonymous" }
  | { kind: "key"; ip: string; org: string; plan: PlanId; record: KeyRecord; keyHash: string };

type MemoryState = {
  hits: Map<string, number[]>;
  months: Map<string, number>;
  keys: Map<string, KeyRecord>;
};

const memory: MemoryState = {
  hits: new Map(),
  months: new Map(),
  keys: new Map(),
};

let redisClient: Redis | null | undefined;
const slidingLimiters = new Map<string, Ratelimit>();

export function resetBrainGuard() {
  memory.hits.clear();
  memory.months.clear();
  memory.keys.clear();
  slidingLimiters.clear();
  redisClient = undefined;
}

export function hashApiKey(key: string) {
  return createHash("sha256").update(key).digest("hex");
}

export function rememberKeyForTests(rawKey: string, record: KeyRecord) {
  memory.keys.set(hashApiKey(rawKey), record);
}

function redis() {
  if (redisClient !== undefined) return redisClient;
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  redisClient = url && token ? new Redis({ url, token }) : null;
  return redisClient;
}

export function brainUsesRedis() {
  return redis() !== null;
}

function clientIp(request: Request) {
  const forwarded = request.headers.get("x-forwarded-for");
  if (forwarded) {
    const first = forwarded.split(",")[0]?.trim();
    if (first) return first;
  }
  return request.headers.get("x-real-ip")?.trim() || "local";
}

function slidingMemory(key: string, limit: number, windowMs: number, now: number): LimitSnapshot {
  const fresh = (memory.hits.get(key) ?? []).filter((stamp) => now - stamp < windowMs);
  const reset = (fresh[0] ?? now) + windowMs;
  if (fresh.length >= limit) {
    memory.hits.set(key, fresh);
    return { ok: false, name: windowMs > 86_400_000 ? "sliding" : "daily", limit, remaining: 0, reset, used: fresh.length, window: windowMs > 86_400_000 ? "month" : "day" };
  }
  fresh.push(now);
  memory.hits.set(key, fresh);
  return {
    ok: true,
    name: windowMs > 86_400_000 ? "sliding" : "daily",
    limit,
    remaining: limit - fresh.length,
    reset,
    used: fresh.length,
    window: windowMs > 86_400_000 ? "month" : "day",
  };
}

function monthMemory(key: string, limit: number, now: number): LimitSnapshot {
  const used = memory.months.get(key) ?? 0;
  const reset = monthReset(now);
  if (used >= limit) {
    return { ok: false, name: "monthly", limit, remaining: 0, reset, used, window: "month" };
  }
  const next = used + 1;
  memory.months.set(key, next);
  return { ok: true, name: "monthly", limit, remaining: limit - next, reset, used: next, window: "month" };
}

function monthReset(now: number) {
  const date = new Date(now);
  return Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + 1, 1);
}

async function loadKey(hash: string): Promise<KeyRecord | null> {
  const client = redis();
  if (!client) return memory.keys.get(hash) ?? null;
  const value = await client.get<KeyRecord | string>(`brain:key:${hash}`);
  if (!value) return null;
  if (typeof value === "string") {
    try {
      return JSON.parse(value) as KeyRecord;
    } catch {
      return null;
    }
  }
  return value;
}

async function touchKey(hash: string, record: KeyRecord) {
  const next = { ...record, last_used: new Date().toISOString() };
  const client = redis();
  if (!client) {
    memory.keys.set(hash, next);
    return;
  }
  await client.set(`brain:key:${hash}`, next);
}

function limiter(prefix: string, tokens: number, window: "1 d" | "30 d") {
  const client = redis();
  if (!client) return null;
  const cacheKey = `${prefix}:${tokens}:${window}`;
  const existing = slidingLimiters.get(cacheKey);
  if (existing) return existing;
  const created = new Ratelimit({
    redis: client,
    limiter: Ratelimit.slidingWindow(tokens, window),
    prefix: `brain:rl:${prefix}`,
    analytics: false,
  });
  slidingLimiters.set(cacheKey, created);
  return created;
}

async function slidingRemote(prefix: string, id: string, tokens: number, window: "1 d" | "30 d", name: LimitSnapshot["name"]): Promise<LimitSnapshot> {
  const gate = limiter(prefix, tokens, window);
  if (!gate) {
    const windowMs = window === "1 d" ? 86_400_000 : 30 * 86_400_000;
    return slidingMemory(`${prefix}:${id}`, tokens, windowMs, Date.now());
  }
  const result = await gate.limit(id);
  return {
    ok: result.success,
    name,
    limit: result.limit,
    remaining: result.remaining,
    reset: result.reset,
    used: result.limit - result.remaining,
    window: window === "1 d" ? "day" : "month",
  };
}

async function monthRemote(org: string, limit: number): Promise<LimitSnapshot> {
  const client = redis();
  const now = Date.now();
  const key = `usage:${org}:${yyyymm()}`;
  if (!client) return monthMemory(key, limit, now);
  const current = Number((await client.get<number | string>(key)) ?? 0);
  const reset = monthReset(now);
  if (current >= limit) {
    return { ok: false, name: "monthly", limit, remaining: 0, reset, used: current, window: "month" };
  }
  const used = await client.incr(key);
  if (used === 1) await client.expire(key, 60 * 60 * 24 * 40);
  return { ok: true, name: "monthly", limit, remaining: Math.max(0, limit - used), reset, used, window: "month" };
}

export type GuardResult =
  | { ok: true; identity: GuardIdentity; limit: LimitSnapshot; usage: LimitSnapshot }
  | { ok: false; status: number; code: string; message: string; limit?: LimitSnapshot };

export async function guardRequest(request: Request): Promise<GuardResult> {
  const ip = clientIp(request);
  const header = request.headers.get("authorization");
  if (!header) {
    const daily = await slidingRemote("anon", ip, ANON_DAILY_LIMIT, "1 d", "daily");
    if (!daily.ok) {
      return {
        ok: false,
        status: 429,
        code: "rate_limited",
        message: `Daily limit of ${ANON_DAILY_LIMIT} anonymous calls reached for this IP.`,
        limit: daily,
      };
    }
    return { ok: true, identity: { kind: "anonymous", ip, org: null, plan: "anonymous" }, limit: daily, usage: daily };
  }

  const match = /^Bearer\s+(ap_live_[A-Za-z0-9]{32})$/.exec(header.trim());
  if (!match) {
    return { ok: false, status: 401, code: "invalid_key", message: "Authorization must be Bearer ap_live_ followed by 32 letters or digits." };
  }
  const keyHash = hashApiKey(match[1]);
  const record = await loadKey(keyHash);
  if (!record || record.revoked || !isPlan(record.plan)) {
    return { ok: false, status: 401, code: "invalid_key", message: "This API key is unknown or revoked." };
  }
  if (record.scopes?.length && !record.scopes.includes("read")) {
    return { ok: false, status: 403, code: "forbidden", message: "This API key does not include the read scope." };
  }
  const cap = monthlyLimit(record.plan, record.monthlyLimit);
  const sliding = await slidingRemote(`plan:${record.plan}`, record.org, cap, "30 d", "sliding");
  if (!sliding.ok) {
    return {
      ok: false,
      status: 429,
      code: "rate_limited",
      message: `Sliding window of ${cap} calls for the ${record.plan} plan is exhausted.`,
      limit: sliding,
    };
  }
  const usage = await monthRemote(record.org, cap);
  if (!usage.ok) {
    return {
      ok: false,
      status: 429,
      code: "rate_limited",
      message: `Monthly limit of ${cap} calls reached for the ${record.plan} plan.`,
      limit: usage,
    };
  }
  await touchKey(keyHash, record);
  return {
    ok: true,
    identity: { kind: "key", ip, org: record.org, plan: record.plan, record, keyHash },
    limit: sliding,
    usage,
  };
}

export function limitHeaders(limit: LimitSnapshot, usage: LimitSnapshot) {
  const headers = new Headers();
  headers.set("x-ratelimit-limit", String(limit.limit));
  headers.set("x-ratelimit-remaining", String(limit.remaining));
  headers.set("x-ratelimit-reset", String(Math.ceil(limit.reset / 1000)));
  headers.set("x-usage-limit", String(usage.limit));
  headers.set("x-usage-remaining", String(usage.remaining));
  headers.set("x-usage-used", String(usage.used));
  headers.set("x-usage-window", usage.window);
  return headers;
}

export function retryAfterSeconds(limit: LimitSnapshot) {
  return String(Math.max(1, Math.ceil((limit.reset - Date.now()) / 1000)));
}
