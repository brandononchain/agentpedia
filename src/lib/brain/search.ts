import type { BrainGrade, BrainIndex, BrainKind, BrainTier, SearchHit } from "@/lib/brain/types";
import { loadBrainIndex } from "@/lib/brain/index";
import { tokenize } from "@/lib/brain/tokenize";
import { gradeAtLeast, tierAtLeast, todayIso, trustFor } from "@/lib/brain/trust";
import { absoluteUrl } from "@/lib/site";

const FIELD_INDEX: Record<string, number> = {
  name: 1,
  title: 2,
  description: 3,
  tags: 4,
  shelf: 5,
  body: 6,
};

export type SearchInput = {
  query: string;
  kind?: BrainKind | "any";
  shelf?: string;
  minTier?: BrainTier;
  minGrade?: Exclude<BrainGrade, "F">;
  limit?: number;
  today?: string;
};

function idf(docCount: number, df: number) {
  return Math.log(1 + (docCount - df + 0.5) / (df + 0.5));
}

function formatFactor(value: number) {
  return Number.isInteger(value) ? String(value) : String(Math.round(value * 100) / 100);
}

export function searchEntries(input: SearchInput, index: BrainIndex = loadBrainIndex()): SearchHit[] {
  const today = input.today ?? todayIso();
  const kind = input.kind ?? "any";
  const limit = input.limit ?? 10;
  const terms = [...new Set(tokenize(input.query))];
  if (terms.length === 0) return [];

  const { k1, b } = index.bm25;
  const weights = index.fieldWeights;
  const fields = index.fields;
  const scores = new Map<number, { relevance: number; fields: Set<string> }>();

  for (const term of terms) {
    const rows = index.postings[term];
    if (!rows?.length) continue;
    const weight = idf(index.docCount, rows.length);
    for (const row of rows) {
      const doc = row[0];
      const entry = index.entries[doc];
      if (!entry) continue;
      let tfWeighted = 0;
      const matched = new Set<string>();
      for (const field of fields) {
        const tf = row[FIELD_INDEX[field] ?? -1] ?? 0;
        if (!tf) continue;
        const dl = entry.fieldLength[field] ?? 0;
        const avg = index.avgFieldLength[field] || 1;
        const normalized = tf / ((1 - b) + b * (dl / avg));
        tfWeighted += (weights[field] ?? 1) * normalized;
        matched.add(field);
      }
      if (tfWeighted <= 0) continue;
      const relevance = weight * ((tfWeighted * (k1 + 1)) / (tfWeighted + k1));
      const current = scores.get(doc) ?? { relevance: 0, fields: new Set<string>() };
      current.relevance += relevance;
      for (const field of matched) current.fields.add(field);
      scores.set(doc, current);
    }
  }

  const hits: SearchHit[] = [];
  for (const [doc, scored] of scores) {
    const entry = index.entries[doc];
    if (!entry || scored.relevance <= 0) continue;
    if (kind !== "any" && entry.kind !== kind) continue;
    if (input.shelf && entry.shelf !== input.shelf) continue;
    const trust = trustFor(entry, today);
    if (!trust) continue;
    if (input.minTier && !tierAtLeast(trust.tier, input.minTier)) continue;
    if (input.minGrade && !gradeAtLeast(entry.grade, input.minGrade)) continue;
    const finalScore = scored.relevance * trust.multiplier;
    const why = [...scored.fields].sort().map((field) => `matched ${field}`);
    why.push(`tier ${trust.tier} x${formatFactor(trust.tierMultiplier)}`);
    why.push(`grade ${entry.grade} x${formatFactor(trust.gradeMultiplier)}`);
    if (trust.warning) why.push("warning x0.8");
    if (trust.lintMultiplier !== 1) why.push(`lint ${entry.lintScore} x0.9`);
    hits.push({
      name: entry.name,
      kind: entry.kind,
      title: entry.title,
      description: entry.description,
      shelf: entry.shelf,
      callNumber: entry.callNumber,
      tier: trust.tier,
      audit: { grade: entry.grade, score: entry.auditScore },
      lint: { score: entry.lintScore },
      digest: entry.digest,
      status: entry.status,
      url: absoluteUrl(entry.url),
      score: Math.round(finalScore * 10000) / 10000,
      warning: trust.warning,
      why,
    });
  }

  hits.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));
  return hits.slice(0, Math.max(0, limit));
}
