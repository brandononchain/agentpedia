import type { BrainEntry, BrainGrade, BrainTier } from "@/lib/brain/types";

const TIER_RANK: Record<BrainTier, number> = { listed: 1, verified: 2, certified: 3 };
const GRADE_RANK: Record<BrainGrade, number> = { F: 0, D: 1, C: 2, B: 3, A: 4 };
const TIER_MULT: Record<BrainTier, number> = { certified: 1.25, verified: 1.15, listed: 1 };
const GRADE_MULT: Record<Exclude<BrainGrade, "F">, number> = { A: 1, B: 0.95, C: 0.85, D: 0.6 };

const BLOCKED_AUDIT = new Set(["on-hold", "revoked"]);
const BLOCKED_CERT = new Set(["on-hold", "withheld", "revoked"]);

export function todayIso(now = new Date()) {
  return now.toISOString().slice(0, 10);
}

export function isServable(entry: BrainEntry) {
  if (!entry.digest) return false;
  if (entry.grade === "F" || BLOCKED_AUDIT.has(entry.status)) return false;
  if (BLOCKED_CERT.has(entry.certStatus)) return false;
  return entry.grade === "A" || entry.grade === "B" || entry.grade === "C" || entry.grade === "D";
}

/** Expired audits and expired certificates rank as Listed. */
export function effectiveTier(entry: BrainEntry, today: string): BrainTier {
  const auditExpired = Boolean(entry.expiresAt) && entry.expiresAt < today;
  const certExpired = entry.certStatus === "expired" || (Boolean(entry.certExpiresAt) && entry.certExpiresAt < today);
  if (auditExpired || certExpired || entry.certStatus === "recheck-pending") return "listed";
  return entry.claimedTier;
}

export type Trust = {
  tier: BrainTier;
  multiplier: number;
  warning: boolean;
  tierMultiplier: number;
  gradeMultiplier: number;
  warningMultiplier: number;
  lintMultiplier: number;
};

export function trustFor(entry: BrainEntry, today: string): Trust | null {
  if (!isServable(entry)) return null;
  if (entry.grade === "F") return null;
  const tier = effectiveTier(entry, today);
  const warning = entry.status === "warning";
  const tierMultiplier = TIER_MULT[tier];
  const gradeMultiplier = GRADE_MULT[entry.grade];
  const warningMultiplier = warning ? 0.8 : 1;
  const lintMultiplier = entry.lintScore < 100 ? 0.9 : 1;
  return {
    tier,
    multiplier: tierMultiplier * gradeMultiplier * warningMultiplier * lintMultiplier,
    warning,
    tierMultiplier,
    gradeMultiplier,
    warningMultiplier,
    lintMultiplier,
  };
}

export function tierAtLeast(tier: BrainTier, min: BrainTier) {
  return TIER_RANK[tier] >= TIER_RANK[min];
}

export function gradeAtLeast(grade: BrainGrade, min: Exclude<BrainGrade, "F">) {
  return GRADE_RANK[grade] >= GRADE_RANK[min];
}
