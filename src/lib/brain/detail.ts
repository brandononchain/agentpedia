import { certificateFor, type CertificateDocument } from "@/lib/certificates";
import { entryFiles, publicFile, rawFileUrl, serveInstruction } from "@/lib/brain/content";
import { loadBrainIndex } from "@/lib/brain/index";
import type { BrainEntry, BrainKind } from "@/lib/brain/types";
import { effectiveTier, isServable, todayIso } from "@/lib/brain/trust";
import { absoluteUrl } from "@/lib/site";
import { readFileSync } from "node:fs";
import { join } from "node:path";

export function findEntry(kind: BrainKind, name: string) {
  const index = loadBrainIndex();
  return index.entries.find((entry) => entry.kind === kind && entry.name === name) ?? null;
}

export function digestMatches(entry: BrainEntry, digest: string | null) {
  if (!digest) return true;
  const wanted = digest.startsWith("sha256:") ? digest : `sha256:${digest}`;
  return wanted === entry.digest;
}

function certificateView(entry: BrainEntry, document: CertificateDocument | null) {
  const signature = document?.signature;
  return {
    id: document?.payload.id ?? null,
    claimedTier: entry.claimedTier,
    displayTier: document?.payload.displayTier ?? entry.claimedTier,
    status: document?.payload.status ?? entry.certStatus,
    digest: entry.digest,
    lockHash: entry.lockHash,
    lockHashAlg: entry.lockHashAlg,
    auditedCommit: entry.auditedCommit,
    expiresAt: document?.payload.expiresAt ?? entry.certExpiresAt,
    signed: document?.signed ?? false,
    signature: signature?.value ?? null,
    keyId: signature?.kid ?? null,
  };
}

export function entryDetail(entry: BrainEntry, options: { includeFiles: boolean; today?: string }) {
  if (!isServable(entry)) return null;
  const today = options.today ?? todayIso();
  const tier = effectiveTier(entry, today);
  const primaryName = entry.kind === "skill" ? "SKILL.md" : "AGENT.md";
  const primaryPath = join(process.cwd(), entry.sourcePath, primaryName);
  let raw = "";
  try {
    raw = readFileSync(primaryPath, "utf8");
  } catch {
    raw = "";
  }
  const body = raw ? serveInstruction(raw, entry) : "";
  const document = certificateFor(entry.kind, entry.name);
  const payload: Record<string, unknown> = {
    name: entry.name,
    kind: entry.kind,
    title: entry.title,
    description: entry.description,
    tags: entry.tags,
    shelf: entry.shelf,
    subShelf: entry.subShelf,
    callNumber: entry.callNumber,
    tier,
    audit: { grade: entry.grade, score: entry.auditScore },
    lint: { score: entry.lintScore },
    digest: entry.digest,
    lockHash: entry.lockHash,
    status: entry.status,
    warning: entry.status === "warning",
    url: absoluteUrl(entry.url),
    frontmatter: entry.frontmatter,
    body,
    certificate: certificateView(entry, document),
  };
  if (options.includeFiles) {
    payload.files = entryFiles(entry).map((file) => ({
      ...publicFile(entry, file),
      url: rawFileUrl(entry, file.path),
    }));
  }
  return payload;
}

export function shelfList(today = todayIso()) {
  const index = loadBrainIndex();
  const served = index.entries.filter((entry) => isServable(entry) && effectiveTier(entry, today));
  return index.shelves
    .map((shelf) => {
      const entries = served.filter((entry) => entry.shelf === shelf.id);
      return {
        id: shelf.id,
        label: shelf.label,
        number: shelf.number,
        blurb: shelf.blurb,
        skills: entries.filter((entry) => entry.kind === "skill").length,
        agents: entries.filter((entry) => entry.kind === "agent").length,
        subshelves: shelf.subshelves.map((subshelf) => ({
          ...subshelf,
          skills: entries.filter((entry) => entry.kind === "skill" && entry.subShelf === subshelf.slug).length,
          agents: entries.filter((entry) => entry.kind === "agent" && entry.subShelf === subshelf.slug).length,
        })),
      };
    })
    .filter((shelf) => shelf.skills + shelf.agents > 0);
}
