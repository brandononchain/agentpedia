export type BrainKind = "skill" | "agent";
export type BrainTier = "listed" | "verified" | "certified";
export type BrainGrade = "A" | "B" | "C" | "D" | "F";
export type BrainStatus = "passed" | "warning" | "on-hold" | "revoked";

export type BrainFile = {
  path: string;
  bytes: number;
};

export type BrainEntry = {
  name: string;
  kind: BrainKind;
  title: string;
  description: string;
  tags: string[];
  shelf: string;
  shelfLabel: string;
  subShelf: string;
  subShelfLabel: string;
  callNumber: string;
  claimedTier: BrainTier;
  grade: BrainGrade;
  auditScore: number;
  lintScore: number;
  digest: string;
  lockHash: string;
  lockHashAlg: string;
  status: BrainStatus;
  certStatus: string;
  expiresAt: string;
  certExpiresAt: string;
  auditedCommit: string;
  sourcePath: string;
  url: string;
  frontmatter: Record<string, unknown>;
  files: BrainFile[];
  fieldLength: Record<string, number>;
};

export type BrainShelf = {
  id: string;
  label: string;
  number: number;
  blurb: string;
  subshelves: { slug: string; label: string; description: string; number: number }[];
};

/** term -> [docIndex, name, title, description, tags, shelf, body] */
export type BrainPosting = number[];

export type BrainIndex = {
  schema: string;
  version: string;
  generatedAt: string;
  tokenizer: string;
  bm25: { k1: number; b: number };
  fieldWeights: Record<string, number>;
  fields: string[];
  avgFieldLength: Record<string, number>;
  docCount: number;
  entries: BrainEntry[];
  postings: Record<string, BrainPosting[]>;
  shelves: BrainShelf[];
};

export type SearchHit = {
  name: string;
  kind: BrainKind;
  title: string;
  description: string;
  shelf: string;
  callNumber: string;
  tier: BrainTier;
  audit: { grade: BrainGrade; score: number };
  lint: { score: number };
  digest: string;
  status: BrainStatus;
  url: string;
  score: number;
  warning: boolean;
  why: string[];
};
