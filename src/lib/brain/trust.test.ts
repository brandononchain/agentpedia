import assert from "node:assert/strict";
import test from "node:test";
import type { BrainEntry } from "./types";
import { effectiveTier, isServable, trustFor } from "./trust";

function entry(overrides: Partial<BrainEntry> = {}): BrainEntry {
  return {
    name: "sample",
    kind: "skill",
    title: "Sample",
    description: "",
    tags: [],
    shelf: "dev-tools",
    shelfLabel: "Dev Tools",
    subShelf: "git",
    subShelfLabel: "Git",
    callNumber: "1.1",
    claimedTier: "certified",
    grade: "A",
    auditScore: 100,
    lintScore: 100,
    digest: "sha256:abc",
    lockHash: "abc",
    lockHashAlg: "skills-lock-v2",
    status: "passed",
    certStatus: "active",
    expiresAt: "2099-01-01",
    certExpiresAt: "2099-01-01",
    auditedCommit: "abc",
    sourcePath: "skills/dev-tools/sample",
    url: "/skills/sample",
    frontmatter: {},
    files: [],
    fieldLength: {},
    ...overrides,
  };
}

test("trust multipliers stack", () => {
  assert.equal(trustFor(entry(), "2026-11-21")?.multiplier, 1.25);
  assert.equal(trustFor(entry({ claimedTier: "verified", grade: "B" }), "2026-11-21")?.multiplier, 1.15 * 0.95);
  assert.equal(trustFor(entry({ status: "warning" }), "2026-11-21")?.multiplier, 1.25 * 0.8);
  assert.equal(trustFor(entry({ lintScore: 99 }), "2026-11-21")?.multiplier, 1.25 * 0.9);
  assert.equal(trustFor(entry({ grade: "C", claimedTier: "listed", lintScore: 90, status: "warning" }), "2026-11-21")?.multiplier, 1 * 0.85 * 0.8 * 0.9);
});

test("an expired audit ranks as Listed", () => {
  const expired = entry({ expiresAt: "2020-01-01", claimedTier: "certified" });
  assert.equal(effectiveTier(expired, "2026-11-21"), "listed");
  assert.equal(trustFor(expired, "2026-11-21")?.multiplier, 1);
  assert.equal(trustFor(expired, "2026-11-21")?.warning, false);
});

test("on-hold, revoked, withheld, and grade F are not servable", () => {
  assert.equal(isServable(entry({ status: "on-hold" })), false);
  assert.equal(isServable(entry({ status: "revoked" })), false);
  assert.equal(isServable(entry({ certStatus: "withheld" })), false);
  assert.equal(isServable(entry({ certStatus: "on-hold" })), false);
  assert.equal(isServable(entry({ grade: "F" })), false);
  assert.equal(trustFor(entry({ status: "on-hold" }), "2026-11-21"), null);
});
