import raw from "../../data/certificates.json";

export type DisplayTier =
  | "listed"
  | "verified"
  | "certified"
  | "recheck-pending"
  | "expired"
  | "withheld";

export type CertificatePayload = {
  schema: string;
  id: string;
  subject: {
    kind: "skill" | "agent";
    name: string;
    title: string;
    sourcePath: string;
    entryPath: string;
  };
  claimedTier: "listed" | "verified" | "certified";
  displayTier: DisplayTier;
  status: "active" | "recheck-pending" | "expired" | "withheld";
  statusReason: string;
  sourceCommit: string;
  currentCommit: string;
  contentDigest: string;
  currentDigest: string;
  issuedAt: string;
  expiresAt: string;
  revalidation: {
    sourceRule: string;
    expiryRule: string;
    listedDays: number;
    verifiedDays: number;
    reviewDays: number;
  };
  lint: {
    score: number;
    errors: number;
    warnings: number;
    info: number;
    gate: string;
    summary: string;
  };
  review: { reviewer: string; date: string; notes: string } | null;
  run: {
    present: boolean;
    ok: boolean;
    ranAt: string | null;
    countsAsVerification: boolean;
    harnessDigest: string | null;
    manifestDigest: string | null;
  };
  checks: Array<{
    id: string;
    kind: string;
    ok: boolean;
    exitCode: number | null;
    durationMs: number;
    stdout: string;
    stderr: string;
  }>;
  limits: string[];
  badge: { width: number; height: number; label: string; message: string };
  urls: { page: string; badge: string; record: string; publicKey: string };
};

export type CertificateDocument = {
  payload: CertificatePayload;
  canonical: string;
  signed: boolean;
  signature: { alg: "Ed25519"; kid: string; value: string } | null;
  keyUrl: string;
};

export type CertificateCatalog = {
  schema: string;
  generatedAt: string;
  rules: { listedDays: number; verifiedDays: number; reviewDays: number };
  signing: { alg: string; signed: boolean };
  stats: {
    total: number;
    active: number;
    listed: number;
    verified: number;
    certified: number;
    recheckPending: number;
    expired: number;
    withheld: number;
  };
  certificates: CertificateDocument[];
};

export const certificates = raw as CertificateCatalog;

const bySubject = new Map(
  certificates.certificates.map((document) => [
    `${document.payload.subject.kind}:${document.payload.subject.name}`,
    document,
  ]),
);

const byId = new Map(certificates.certificates.map((document) => [document.payload.id, document]));

export function certificateFor(kind: "skill" | "agent", name: string) {
  return bySubject.get(`${kind}:${name}`) ?? null;
}

export function certificateById(id: string) {
  return byId.get(id) ?? null;
}

export function tierLabel(tier: string) {
  if (tier === "recheck-pending") return "re-check pending";
  if (tier === "withheld") return "not listed";
  return tier;
}

export function badgeAlt(document: CertificateDocument) {
  return `${document.payload.badge.label}: ${document.payload.badge.message}`;
}

export function embedMarkdown(document: CertificateDocument) {
  const alt = badgeAlt(document);
  const { page, badge } = document.payload.urls;
  return `[![${alt}](${badge})](${page})`;
}

export function embedHtml(document: CertificateDocument) {
  const alt = badgeAlt(document);
  const { page, badge } = document.payload.urls;
  return `<a href="${page}"><img alt="${alt}" src="${badge}"></a>`;
}
