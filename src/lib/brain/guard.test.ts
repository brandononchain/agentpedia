import assert from "node:assert/strict";
import test from "node:test";
import { guardRequest, rememberKeyForTests, resetBrainGuard } from "./guard";

function request(headers: Record<string, string> = {}) {
  return new Request("https://agentpedia.sh/api/v1/skills/search", { headers });
}

test("anonymous callers stop at 100 a day", async () => {
  resetBrainGuard();
  delete process.env.UPSTASH_REDIS_REST_URL;
  delete process.env.UPSTASH_REDIS_REST_TOKEN;
  for (let index = 0; index < 100; index += 1) {
    const result = await guardRequest(request({ "x-forwarded-for": "203.0.113.9" }));
    assert.equal(result.ok, true, `call ${index}`);
  }
  const blocked = await guardRequest(request({ "x-forwarded-for": "203.0.113.9" }));
  assert.equal(blocked.ok, false);
  if (!blocked.ok) {
    assert.equal(blocked.status, 429);
    assert.equal(blocked.limit?.name, "daily");
    assert.match(blocked.message, /Daily limit of 100/);
  }
});

test("a key is metered against the monthly plan", async () => {
  resetBrainGuard();
  delete process.env.UPSTASH_REDIS_REST_URL;
  delete process.env.UPSTASH_REDIS_REST_TOKEN;
  const raw = `ap_live_${"a".repeat(32)}`;
  rememberKeyForTests(raw, {
    org: "example",
    plan: "enterprise",
    created: "2026-11-21T00:00:00Z",
    last_used: null,
    scopes: ["read"],
    monthlyLimit: 2,
  });
  const first = await guardRequest(request({ authorization: `Bearer ${raw}` }));
  const second = await guardRequest(request({ authorization: `Bearer ${raw}` }));
  const third = await guardRequest(request({ authorization: `Bearer ${raw}` }));
  assert.equal(first.ok, true);
  assert.equal(second.ok, true);
  assert.equal(third.ok, false);
  if (!third.ok) {
    assert.equal(third.status, 429);
    assert.ok(third.limit?.name === "monthly" || third.limit?.name === "sliding");
    assert.match(third.message, /enterprise/);
  }
});

test("a revoked key is rejected", async () => {
  resetBrainGuard();
  const raw = `ap_live_${"b".repeat(32)}`;
  rememberKeyForTests(raw, {
    org: "example",
    plan: "builder",
    created: "2026-11-21T00:00:00Z",
    last_used: null,
    scopes: ["read"],
    revoked: true,
  });
  const result = await guardRequest(request({ authorization: `Bearer ${raw}` }));
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.status, 401);
});
