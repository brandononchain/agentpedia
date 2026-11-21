export const PLAN_IDS = ["free", "builder", "team", "enterprise"] as const;
export type PlanId = (typeof PLAN_IDS)[number];

export const ANON_DAILY_LIMIT = 100;

/** Calendar-month hard stops. Enterprise uses the key's monthlyLimit, else this default. */
export const PLAN_MONTHLY: Record<PlanId, number> = {
  free: 1_000,
  builder: 25_000,
  team: 150_000,
  enterprise: 1_000_000,
};

export const PLAN_COPY = {
  free: { price: "$0", calls: "1,000 calls/mo", note: "Hard stop. Skill text stays free." },
  builder: { price: "$19/mo", calls: "25,000 calls, then $4 per 1,000", note: "Coming soon / contact" },
  team: {
    price: "$99/mo",
    calls: "150,000 calls, 5 seats, org-wide trust rules, 50 private skills",
    note: "Coming soon / contact",
  },
  enterprise: { price: "from $1,500/mo", calls: "Custom volume, SSO, and an SLA", note: "Coming soon / contact" },
} as const;

export function isPlan(value: string): value is PlanId {
  return (PLAN_IDS as readonly string[]).includes(value);
}

export function monthlyLimit(plan: PlanId, override?: number | null) {
  if (plan === "enterprise" && override && override > 0) return override;
  return PLAN_MONTHLY[plan];
}

export function yyyymm(now = new Date()) {
  const year = now.getUTCFullYear();
  const month = String(now.getUTCMonth() + 1).padStart(2, "0");
  return `${year}${month}`;
}
