import assert from "node:assert/strict";
import test from "node:test";
import { searchEntries } from "./search";
import type { BrainIndex, BrainEntry } from "./types";
import { tokenize } from "./tokenize";

function doc(partial: Partial<BrainEntry> & Pick<BrainEntry, "name" | "title">): BrainEntry {
  return {
    kind: "skill",
    description: "",
    tags: [],
    shelf: "dev-tools",
    shelfLabel: "Dev Tools",
    subShelf: "git",
    subShelfLabel: "Git",
    callNumber: "1.1",
    claimedTier: "listed",
    grade: "A",
    auditScore: 100,
    lintScore: 100,
    digest: `sha256:${partial.name}`,
    lockHash: "abc",
    lockHashAlg: "skills-lock-v2",
    status: "passed",
    certStatus: "active",
    expiresAt: "2099-01-01",
    certExpiresAt: "2099-01-01",
    auditedCommit: "abc",
    sourcePath: `skills/dev-tools/${partial.name}`,
    url: `/skills/${partial.name}`,
    frontmatter: {},
    files: [],
    fieldLength: {},
    ...partial,
  };
}

function indexOf(entries: BrainEntry[]): BrainIndex {
  const fields = ["name", "title", "description", "tags", "shelf", "body"] as const;
  const texts = entries.map((entry) => ({
    name: tokenize(entry.name),
    title: tokenize(entry.title),
    description: tokenize(entry.description),
    tags: tokenize(entry.tags.join(" ")),
    shelf: tokenize(`${entry.shelfLabel} ${entry.subShelfLabel}`),
    body: tokenize(entry.description),
  }));
  entries.forEach((entry, index) => {
    entry.fieldLength = Object.fromEntries(fields.map((field) => [field, texts[index][field].length]));
  });
  const postings: BrainIndex["postings"] = {};
  const totals: Record<string, number> = {};
  texts.forEach((tokens, docIndex) => {
    fields.forEach((field, fieldIndex) => {
      totals[field] = (totals[field] ?? 0) + tokens[field].length;
      const counts = new Map<string, number>();
      for (const term of tokens[field]) counts.set(term, (counts.get(term) ?? 0) + 1);
      for (const [term, count] of counts) {
        const row = postings[term]?.find((item) => item[0] === docIndex) ?? [docIndex, 0, 0, 0, 0, 0, 0];
        if (!postings[term]?.includes(row)) (postings[term] ??= []).push(row);
        row[fieldIndex + 1] = count;
      }
    });
  });
  return {
    schema: "agentpedia.brain-index.v1",
    version: "test",
    generatedAt: "2026-11-21T00:00:00Z",
    tokenizer: "brain-v1",
    bm25: { k1: 1.2, b: 0.75 },
    fieldWeights: { name: 3, title: 3, description: 2, tags: 2, shelf: 1.5, body: 1 },
    fields: [...fields],
    avgFieldLength: Object.fromEntries(fields.map((field) => [field, (totals[field] ?? 0) / entries.length || 1])),
    docCount: entries.length,
    entries,
    postings,
    shelves: [],
  };
}

test("a name match outranks a passing mention, and on-hold is dropped", () => {
  const held = doc({ name: "alpha-held", title: "Alpha", status: "on-hold" });
  const named = doc({ name: "alpha-tool", title: "Alpha tool" });
  const mentioned = doc({ name: "other-tool", title: "Notes", description: "alpha alpha alpha alpha" });
  const hits = searchEntries({ query: "alpha", limit: 5, today: "2026-11-21" }, indexOf([held, named, mentioned]));
  assert.equal(hits.some((hit) => hit.name === "alpha-held"), false);
  assert.equal(hits[0]?.name, "alpha-tool");
  assert.ok(hits[0].why.some((line) => line.startsWith("matched ")));
  assert.ok(hits[0].digest.startsWith("sha256:"));
  assert.equal(hits[0].tier, "listed");
  assert.equal(hits[0].audit.grade, "A");
  assert.equal(hits[0].status, "passed");
});

test("certified ranks above an equal relevance listed entry", () => {
  const listed = doc({ name: "beta-listed", title: "Beta notes" });
  const certified = doc({ name: "beta-certified", title: "Beta notes", claimedTier: "certified" });
  const hits = searchEntries({ query: "beta notes", limit: 2, today: "2026-11-21" }, indexOf([listed, certified]));
  assert.equal(hits[0]?.name, "beta-certified");
  assert.equal(hits[0].tier, "certified");
  assert.equal(hits[1]?.tier, "listed");
});

test("min_grade filters", () => {
  const weak = doc({ name: "gamma-d", title: "Gamma", grade: "D" });
  const strong = doc({ name: "gamma-a", title: "Gamma", grade: "A" });
  const hits = searchEntries({ query: "gamma", minGrade: "B", today: "2026-11-21" }, indexOf([weak, strong]));
  assert.deepEqual(hits.map((hit) => hit.name), ["gamma-a"]);
});
