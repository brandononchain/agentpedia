import type { BrainGrade, BrainKind, BrainTier } from "@/lib/brain/types";
import { brainError } from "@/lib/brain/http";

const KINDS = new Set(["skill", "agent", "any"]);
const TIERS = new Set(["listed", "verified", "certified"]);
const GRADES = new Set(["A", "B", "C", "D"]);

export type ParsedSearch =
  | {
      ok: true;
      query: string;
      kind: BrainKind | "any";
      shelf?: string;
      minTier?: BrainTier;
      minGrade?: Exclude<BrainGrade, "F">;
      limit: number;
    }
  | { ok: false; response: Response };

export function parseSearchParams(url: URL): ParsedSearch {
  const query = url.searchParams.get("query")?.trim() ?? "";
  if (!query) return { ok: false, response: brainError(400, "invalid_request", "query is required.") };
  const kind = url.searchParams.get("kind") || "any";
  if (!KINDS.has(kind)) return { ok: false, response: brainError(400, "invalid_request", "kind must be skill, agent, or any.") };
  const minTier = url.searchParams.get("min_tier");
  if (minTier && !TIERS.has(minTier)) {
    return { ok: false, response: brainError(400, "invalid_request", "min_tier must be listed, verified, or certified.") };
  }
  const minGrade = url.searchParams.get("min_grade");
  if (minGrade && !GRADES.has(minGrade)) {
    return { ok: false, response: brainError(400, "invalid_request", "min_grade must be A, B, C, or D.") };
  }
  const limitRaw = url.searchParams.get("limit");
  let limit = 10;
  if (limitRaw !== null && limitRaw !== "") {
    if (!/^[0-9]+$/.test(limitRaw)) return { ok: false, response: brainError(400, "invalid_request", "limit must be an integer from 1 to 20.") };
    limit = Number(limitRaw);
    if (limit < 1 || limit > 20) return { ok: false, response: brainError(400, "invalid_request", "limit must be an integer from 1 to 20.") };
  }
  const shelf = url.searchParams.get("shelf")?.trim() || undefined;
  return {
    ok: true,
    query,
    kind: kind as BrainKind | "any",
    shelf,
    minTier: (minTier as BrainTier | null) || undefined,
    minGrade: (minGrade as Exclude<BrainGrade, "F"> | null) || undefined,
    limit,
  };
}

export function wantsFiles(url: URL) {
  const include = url.searchParams.get("include") ?? "";
  return include.split(",").map((part) => part.trim()).includes("files");
}
