import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { loadBrainIndex } from "./index";
import { searchEntries } from "./search";

const cases = JSON.parse(readFileSync("tools/tests/brain_golden.json", "utf8")) as { query: string; expect: string }[];

test("golden queries land the expected entry in the top 3", () => {
  assert.ok(cases.length >= 30, `need 30 queries, have ${cases.length}`);
  const index = loadBrainIndex();
  assert.equal(index.entries.some((entry) => entry.grade === "F" || entry.status === "on-hold" || entry.certStatus === "on-hold"), false);
  let hits = 0;
  const misses: { query: string; expect: string; got: string[] }[] = [];
  for (const item of cases) {
    const results = searchEntries({ query: item.query, limit: 3 }, index);
    const names = results.map((result) => result.name);
    if (names.includes(item.expect)) hits += 1;
    else misses.push({ query: item.query, expect: item.expect, got: names });
  }
  const rate = hits / cases.length;
  assert.ok(rate >= 0.8, `${hits}/${cases.length} (${rate.toFixed(2)})\n${JSON.stringify(misses, null, 2)}`);
});
