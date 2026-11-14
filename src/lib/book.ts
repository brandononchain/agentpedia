import { catalog, type Agent, type Skill } from "@/lib/catalog";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { formatDropDate } from "@/lib/format";
import { absoluteUrl } from "@/lib/site";
import { slugify, type Crumb } from "@/lib/wiki";

export type BookKind = "skill" | "agent";

export type Chapter = {
  number: number;
  slug: string;
  title: string;
  markdown: string;
};

export type BookEntry = {
  kind: BookKind;
  name: string;
  title: string;
  description: string;
  body: string;
  added: string;
  sourcePath: string;
  files: { path: string; url?: string }[];
  callNumber: string;
  shelfNumber: number;
  category: string;
  categoryLabel: string;
  subshelf: string;
  subshelfLabel: string;
};

export function skillBook(skill: Skill): BookEntry {
  return {
    kind: "skill",
    name: skill.name,
    title: skill.title,
    description: skill.description,
    body: skill.body,
    added: skill.added,
    sourcePath: skill.sourcePath,
    files: skill.files,
    callNumber: skill.callNumber,
    shelfNumber: skill.shelfNumber,
    category: skill.category,
    categoryLabel: skill.categoryLabel,
    subshelf: skill.subshelf,
    subshelfLabel: skill.subshelfLabel,
  };
}

export function agentBook(agent: Agent): BookEntry {
  return {
    kind: "agent",
    name: agent.name,
    title: agent.name,
    description: agent.description,
    body: agent.body,
    added: agent.added,
    sourcePath: agent.sourcePath,
    files: [],
    callNumber: agent.callNumber,
    shelfNumber: agent.shelfNumber,
    category: agent.category,
    categoryLabel: agent.categoryLabel,
    subshelf: agent.subshelf,
    subshelfLabel: agent.subshelfLabel,
  };
}

export function bookBase(entry: BookEntry) {
  return entry.kind === "skill" ? `/skills/${entry.name}` : `/agents/${entry.name}`;
}

export function bookCrumbs(entry: BookEntry, tail?: { label: string }): Crumb[] {
  const crumbs: Crumb[] = [
    { href: "/", label: "Home" },
    { href: "/#shelves", label: "Shelves" },
    { href: `/category/${entry.category}`, label: `${entry.shelfNumber} ${entry.categoryLabel}` },
    {
      href: `/category/${entry.category}/${entry.subshelf}`,
      label: `${entry.callNumber} ${entry.subshelfLabel}`,
    },
    { href: tail ? bookBase(entry) : undefined, label: entry.title },
  ];
  if (tail) crumbs.push({ label: tail.label });
  return crumbs;
}

function splitSections(markdown: string) {
  const intro: string[] = [];
  const sections: { title: string; body: string[] }[] = [];
  let current: { title: string; body: string[] } | null = null;
  let fence = false;
  let skippedTitle = false;
  for (const line of markdown.replace(/\r\n/g, "\n").split("\n")) {
    if (line.startsWith("```")) fence = !fence;
    const heading = !fence ? /^##\s+(.+?)\s*#*\s*$/.exec(line) : null;
    if (heading) {
      if (current) sections.push(current);
      current = { title: heading[1].replace(/[*_`]/g, "").trim(), body: [] };
      continue;
    }
    if (!current && !skippedTitle && /^#\s+/.test(line)) {
      skippedTitle = true;
      continue;
    }
    if (current) current.body.push(line);
    else intro.push(line);
  }
  if (current) sections.push(current);
  return {
    intro: intro.join("\n").trim(),
    sections: sections.map((section) => ({ title: section.title, body: section.body.join("\n").trim() })),
  };
}

function sectionTitle(title: string) {
  if (/^steps$/i.test(title)) return "Steps";
  if (/input/i.test(title) && /output/i.test(title)) return "Inputs/Outputs";
  return title;
}

export function bookChapters(entry: BookEntry): Chapter[] {
  const { intro, sections } = splitSections(entry.body);
  const used = new Set<number>();
  const chapters: { title: string; markdown: string }[] = [];

  if (intro) chapters.push({ title: "Overview", markdown: intro });

  const whenIndex = sections.findIndex((section) => /when to use/i.test(section.title));
  if (whenIndex >= 0) {
    used.add(whenIndex);
    chapters.push({ title: "When to use", markdown: sections[whenIndex].body || entry.description });
  } else if (/use when/i.test(entry.description)) {
    chapters.push({ title: "When to use", markdown: entry.description.trim() });
  }

  sections.forEach((section, index) => {
    if (used.has(index)) return;
    chapters.push({ title: sectionTitle(section.title), markdown: section.body || section.title });
  });

  const scripts = entry.files.filter((file) => file.path.startsWith("scripts/"));
  if (scripts.length > 0 && !chapters.some((chapter) => /^scripts$/i.test(chapter.title))) {
    chapters.push({
      title: "Scripts",
      markdown: scripts.map((file) => `- \`${file.path}\``).join("\n"),
    });
  }

  if (!chapters.some((chapter) => /reference|asset/i.test(chapter.title))) {
    const assets = entry.files.filter(
      (file) => file.path.startsWith("references/") || file.path.startsWith("assets/"),
    );
    const lines = [`Source: \`${entry.sourcePath}\``];
    for (const file of assets) lines.push(`- [${file.path}](${file.url ?? file.path})`);
    chapters.push({ title: "References/assets", markdown: lines.join("\n") });
  }

  const cert = certificateFor(entry.kind, entry.name);
  if (cert) {
    const commit = cert.payload.sourceCommit.trim();
    chapters.push({
      title: "Certificate",
      markdown: [
        `This entry is ${tierLabel(cert.payload.displayTier)}.`,
        cert.payload.statusReason,
        `Record: [${cert.payload.id}](/cert/${cert.payload.id}).`,
        commit ? `Source commit: \`${commit}\`.` : "Source commit: not recorded.",
        "Version: not recorded.",
      ].join("\n\n"),
    });
  }

  chapters.push({
    title: "Changelog",
    markdown: `Added ${formatDropDate(entry.added)}.`,
  });

  return chapters.map((chapter, index) => ({
    number: index + 1,
    slug: `${index + 1}-${slugify(chapter.title)}`,
    title: chapter.title,
    markdown: `${chapter.markdown.trim()}\n`,
  }));
}

export function chapterBySlug(chapters: Chapter[], slug: string) {
  return chapters.find((chapter) => chapter.slug === slug);
}

export function bookJsonLd(entry: BookEntry, chapters: Chapter[]) {
  const url = absoluteUrl(bookBase(entry));
  return {
    "@context": "https://schema.org",
    "@type": "Book",
    name: entry.title,
    description: entry.description,
    url,
    inLanguage: "en",
    datePublished: entry.added,
    identifier: entry.callNumber,
    author: { "@type": "Person", name: catalog.owner.name, url: catalog.owner.site },
    isPartOf: {
      "@type": "Collection",
      name: `${entry.callNumber} ${entry.subshelfLabel}`,
      url: absoluteUrl(`/category/${entry.category}/${entry.subshelf}`),
    },
    hasPart: chapters.map((chapter) => ({
      "@type": "Chapter",
      position: chapter.number,
      name: chapter.title,
      url: absoluteUrl(`${bookBase(entry)}/ch/${chapter.slug}`),
    })),
  };
}

export function chapterJsonLd(entry: BookEntry, chapter: Chapter) {
  return {
    "@context": "https://schema.org",
    "@type": "Chapter",
    name: chapter.title,
    position: chapter.number,
    url: absoluteUrl(`${bookBase(entry)}/ch/${chapter.slug}`),
    isPartOf: {
      "@type": "Book",
      name: entry.title,
      url: absoluteUrl(bookBase(entry)),
      identifier: entry.callNumber,
    },
  };
}

export function recordedCommit(kind: BookKind, name: string) {
  const commit = certificateFor(kind, name)?.payload.sourceCommit.trim();
  return commit || "Not recorded";
}
