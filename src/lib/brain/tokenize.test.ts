import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { tokenize } from "./tokenize";

const cases = JSON.parse(readFileSync("tools/tests/brain_tokens.json", "utf8")) as { in: string; out: string[] }[];

test("tokenizer matches the locked cases", () => {
  for (const item of cases) {
    assert.deepEqual(tokenize(item.in), item.out, item.in);
  }
});
