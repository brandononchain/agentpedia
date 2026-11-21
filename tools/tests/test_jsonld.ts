import assert from "node:assert/strict";
import { test } from "node:test";
import {
  SITE_IDENTITY,
  SITE_NOT,
  bookDocumentTitle,
  collectionPageLd,
  datasetLd,
  definedTermSetLd,
  howToLd,
  isChapterOrReadPath,
  itemListLd,
  jsonLdErrors,
} from "../../src/lib/structured.ts";

const ORIGIN = "https://agentpedia.sh";

test("identity names this site and the two others", () => {
  assert.match(SITE_IDENTITY, /agentpedia\.sh/);
  assert.match(SITE_IDENTITY, /SKILL\.md/);
  assert.match(SITE_IDENTITY, /open, audited encyclopedia/);
  assert.match(SITE_NOT, /agentpedia\.tmafe\.com/);
  assert.match(SITE_NOT, /AgentPedia\.so/);
});

test("book titles take the lint score and audit grade from the caller", () => {
  const short = bookDocumentTitle("CSV profile", "SKILL.md", 100, "A");
  assert.equal(short, "CSV profile — SKILL.md · lint 100 · audit A | Agentpedia");
  assert.ok(short.length <= 60);

  const graded = bookDocumentTitle("CSV profile", "SKILL.md", 92, "B");
  assert.match(graded, /lint 92/);
  assert.match(graded, /audit B/);
  assert.doesNotMatch(graded, /audit A/);

  const long = bookDocumentTitle("SQL explain, in plain language", "SKILL.md", 100, "A");
  assert.ok(long.length <= 60, long);
  assert.match(long, /SKILL\.md/);
  assert.match(long, /lint 100/);
  assert.match(long, /audit A/);
  assert.match(long, /Agentpedia/);

  const agent = bookDocumentTitle("day-operator", "AGENT.md", undefined, "A");
  assert.equal(agent, "day-operator — AGENT.md · audit A | Agentpedia");
  assert.ok(agent.length <= 60);
});

test("chapter and read URLs are the ones the sitemap drops", () => {
  assert.equal(isChapterOrReadPath("/skills/csv-profile/read"), true);
  assert.equal(isChapterOrReadPath("/agents/day-operator/ch/1-overview"), true);
  assert.equal(isChapterOrReadPath("https://agentpedia.sh/skills/csv-profile/ch/2-steps"), true);
  assert.equal(isChapterOrReadPath("/skills/csv-profile"), false);
  assert.equal(isChapterOrReadPath("/skills/csv-profile.md"), false);
  assert.equal(isChapterOrReadPath("/compare/skills-sh"), false);
});

test("HowTo, DefinedTermSet, Dataset, ItemList, and CollectionPage shapes", () => {
  const howTo = howToLd(ORIGIN);
  const glossary = definedTermSetLd(ORIGIN);
  const dataset = datasetLd({
    origin: ORIGIN,
    name: "Agentpedia security audit",
    description: "Static audit grade, score, and status for every published skill and agent.",
    pagePath: "/security",
    contentPath: "/catalog.json",
  });
  const list = itemListLd({
    name: "Agentpedia security audit",
    description: "Every published entry.",
    items: [{ name: "CSV profile", url: `${ORIGIN}/skills/csv-profile` }],
  });
  const collection = collectionPageLd({
    name: "Dev Tools",
    description: "Shelf of developer skills.",
    url: `${ORIGIN}/category/dev-tools`,
    items: [{ name: "Changelog from commits", url: `${ORIGIN}/skills/changelog-from-commits` }],
  });

  for (const node of [howTo, glossary, dataset, list, collection]) {
    assert.deepEqual(jsonLdErrors(node), [], JSON.stringify(node, null, 2));
  }

  assert.equal(howTo["@type"], "HowTo");
  assert.equal(howTo.step.length, 4);
  assert.equal(glossary["@type"], "DefinedTermSet");
  assert.match(String(glossary.hasDefinedTerm[0].description), /agentpedia\.tmafe\.com/);
  assert.equal(dataset["@type"], "Dataset");
  assert.equal(dataset.distribution["@type"], "DataDownload");
  assert.equal(list["@type"], "ItemList");
  assert.equal(collection["@type"], "CollectionPage");
  assert.equal(collection.mainEntity["@type"], "ItemList");
});
