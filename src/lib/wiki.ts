import { catalog, getSkill, type Agent, type Skill } from "@/lib/catalog";

export type Crumb = { href?: string; label: string };

export type TocItem = { id: string; text: string; depth: 2 | 3 };

export function slugify(text: string) {
  const slug = text
    .replace(/[`*_[\]()]/g, "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return slug || "section";
}

export function headingId(text: string, seen: Map<string, number>) {
  const base = slugify(text);
  const count = seen.get(base) ?? 0;
  seen.set(base, count + 1);
  return count === 0 ? base : `${base}-${count + 1}`;
}

export function extractToc(markdown: string): TocItem[] {
  const items: TocItem[] = [];
  const seen = new Map<string, number>();
  let inFence = false;
  for (const line of markdown.split("\n")) {
    if (line.startsWith("```")) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const match = /^(#{2,3})\s+(.+?)\s*#*\s*$/.exec(line);
    if (!match) continue;
    const text = match[2].replace(/[*_`]/g, "").trim();
    items.push({
      id: headingId(text, seen),
      text,
      depth: match[1].length as 2 | 3,
    });
  }
  return items;
}

export function firstSentence(text: string) {
  const match = text.match(/^[\s\S]*?[.!?](?:\s|$)/);
  return (match?.[0] ?? text).trim();
}

export function agentForSkill(name: string) {
  return catalog.agents.find((agent) => agent.skills.includes(name));
}

export function skillsInOneAgent() {
  const owners = new Map<string, number>();
  for (const agent of catalog.agents) {
    for (const name of agent.skills) owners.set(name, (owners.get(name) ?? 0) + 1);
  }
  return catalog.skills.every((skill) => owners.get(skill.name) === 1);
}

export function relatedSkills(skill: Skill) {
  const agent = agentForSkill(skill.name);
  const sameAgent = new Set((agent?.skills ?? []).filter((name) => name !== skill.name));
  const ordered = [
    ...sameAgent,
    ...catalog.skills
      .filter((item) => item.category === skill.category && item.name !== skill.name && !sameAgent.has(item.name))
      .map((item) => item.name),
  ];
  return ordered.map((name) => getSkill(name)).filter((item): item is Skill => Boolean(item)).slice(0, 8);
}

export function shelfNeighbors(skill: Skill) {
  const shelf = catalog.skills
    .filter((item) => item.category === skill.category)
    .sort((a, b) => a.title.localeCompare(b.title));
  const index = shelf.findIndex((item) => item.name === skill.name);
  return { prev: shelf[index - 1], next: shelf[index + 1] };
}

export function otherAgents(agent: Agent) {
  return catalog.agents.filter((item) => item.name !== agent.name);
}

export function featuredSkill() {
  const featured = catalog.skills.filter((skill) => skill.featured);
  featured.sort((a, b) => {
    if (a.name === "skill-author") return -1;
    if (b.name === "skill-author") return 1;
    return b.added.localeCompare(a.added) || a.name.localeCompare(b.name);
  });
  return featured[0] ?? catalog.skills[0];
}

export function didYouKnow() {
  const { stats, categories, drops } = catalog;
  const biggest = [...categories].sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))[0];
  const newest = drops[0];
  const facts: string[] = [];
  if (skillsInOneAgent()) {
    facts.push(
      `the encyclopedia holds ${stats.skills} skills and ${stats.agents} agents, and each skill belongs to exactly one agent`,
    );
  } else {
    facts.push(`the encyclopedia holds ${stats.skills} skills and ${stats.agents} agents across ${stats.categories} shelves`);
  }
  if (biggest) {
    facts.push(`${biggest.label} is the largest shelf, with ${biggest.count} entries`);
  }
  if (newest) {
    const agentBit = newest.agents.length === 1 ? "1 agent" : `${newest.agents.length} agents`;
    const skillBit = newest.skills.length === 1 ? "1 skill" : `${newest.skills.length} skills`;
    facts.push(
      newest.agents.length
        ? `the newest drop added ${skillBit} and ${agentBit}`
        : `the newest drop added ${skillBit}`,
    );
  }
  if (stats.clean === stats.skills && stats.errors === 0 && stats.warnings === 0 && stats.info === 0) {
    facts.push("every entry in this build scores 100, with no lint errors, warnings, or notes");
  }
  return facts;
}

export function groupByLetter<T>(items: T[], label: (item: T) => string) {
  const map = new Map<string, T[]>();
  for (const item of items) {
    const raw = label(item).trim();
    const letter = (raw.match(/[A-Za-z]/)?.[0] ?? "#").toUpperCase();
    const bucket = map.get(letter) ?? [];
    bucket.push(item);
    map.set(letter, bucket);
  }
  for (const bucket of map.values()) {
    bucket.sort((a, b) => label(a).localeCompare(label(b), "en"));
  }
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

export function alphabet() {
  return ALPHABET;
}

type Term = { label: string; href: string };

let termCache: Term[] | null = null;

function dictionary() {
  if (termCache) return termCache;
  const list: Term[] = [];
  for (const skill of catalog.skills) {
    list.push({ label: skill.name, href: `/skills/${skill.name}` });
    if (skill.title.length >= 8 && skill.title.toLowerCase() !== skill.name) {
      list.push({ label: skill.title, href: `/skills/${skill.name}` });
    }
  }
  for (const agent of catalog.agents) {
    list.push({ label: agent.name, href: `/agents/${agent.name}` });
  }
  for (const category of catalog.categories) {
    if (category.label.length >= 4) list.push({ label: category.label, href: `/category/${category.id}` });
  }
  list.sort((a, b) => b.label.length - a.label.length);
  termCache = list;
  return list;
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function linkCatalogTerms(source: string, selfHref?: string) {
  const terms = dictionary().filter((term) => term.href !== selfHref);
  if (terms.length === 0) return source;
  const lookup = new Map(terms.map((term) => [term.label.toLowerCase(), term.href]));
  const pattern = new RegExp(`(?<![\\w/.-])(${terms.map((term) => escapeRegExp(term.label)).join("|")})(?![\\w/.-])`, "gi");

  const linkPlain = (text: string) =>
    text.replace(pattern, (match) => {
      const href = lookup.get(match.toLowerCase());
      if (!href || href === selfHref) return match;
      return `[${match}](${href})`;
    });

  return source
    .split(/(```[\s\S]*?```)/g)
    .map((part, index) => {
      if (index % 2 === 1) return part;
      return part
        .split(/(\[[^\]]*\]\([^)]*\)|`[^`\n]+`)/g)
        .map((bit, bitIndex) => (bitIndex % 2 === 1 ? bit : linkPlain(bit)))
        .join("");
    })
    .join("");
}
