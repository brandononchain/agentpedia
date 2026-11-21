import Link from "next/link";
import { tierLabel } from "@/lib/certificates";

export function TierMark({ id, tier, grade }: { id: string; tier: string; grade?: string }) {
  const base = tierLabel(tier);
  const label = grade ? `${base} · audit ${grade}` : base;
  return <Link href={`/cert/${id}`}>{label}</Link>;
}
