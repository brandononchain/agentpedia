import Link from "next/link";
import { badgeAlt, certificateFor, tierLabel } from "@/lib/certificates";

export function CertFact({ kind, name }: { kind: "skill" | "agent"; name: string }) {
  const document = certificateFor(kind, name);
  if (!document) return null;
  const { payload } = document;
  return (
    <>
      <dt>Certificate</dt>
      <dd>
        <Link href={`/cert/${payload.id}`}>{tierLabel(payload.displayTier)}</Link>
        {/* Static SVG badge. next/image does not serve this shields-style file at its exact pixel size. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          className="cert-badge"
          src={`/badge/${payload.id}.svg`}
          alt={badgeAlt(document)}
          width={payload.badge.width}
          height={payload.badge.height}
        />
      </dd>
    </>
  );
}
