import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { BrainIndex } from "@/lib/brain/types";

let cached: BrainIndex | null = null;

export function brainIndexPath() {
  return join(process.cwd(), "data", "brain-index.json");
}

export function loadBrainIndex(): BrainIndex {
  if (cached) return cached;
  const raw = readFileSync(brainIndexPath(), "utf8");
  cached = JSON.parse(raw) as BrainIndex;
  return cached;
}

export function resetBrainIndexCache() {
  cached = null;
}
