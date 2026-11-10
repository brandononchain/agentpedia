import Link from "next/link";
import { tierLabel } from "@/lib/certificates";

export function TierMark({ id, tier }: { id: string; tier: string }) {
  return <Link href={`/cert/${id}`}>{tierLabel(tier)}</Link>;
}
