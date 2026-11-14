import raw from "../../data/catalog.json";

export type Severity = "error" | "warn" | "info";
export type BadgeName = "clean" | "noted" | "blocked";

export type Finding = {
  ruleId: string;
  severity: Severity;
  message: string;
  hint: string;
  line: number | null;
  path: string;
};

export type InstallTarget = {
  label: string;
  hint: string;
  snippet: string;
};

export type SkillFile = {
  path: string;
  bytes: number;
  url: string;
};

export type Skill = {
  name: string;
  title: string;
  description: string;
  category: string;
  categoryLabel: string;
  categoryBlurb: string;
  shelfNumber: number;
  subshelf: string;
  subshelfLabel: string;
  callNumber: string;
  tags: string[];
  added: string;
  featured: boolean;
  license: string;
  compatibility: string;
  lint: {
    score: number;
    errors: number;
    warnings: number;
    info: number;
    badge: BadgeName;
    findings: Finding[];
  };
  files: SkillFile[];
  body: string;
  install: Record<"claude" | "codex" | "cursor" | "grok", InstallTarget>;
  rawUrl: string;
  zipUrl: string;
  sourcePath: string;
};

export type Agent = {
  name: string;
  description: string;
  added: string;
  category: string;
  categoryLabel: string;
  shelfNumber: number;
  subshelf: string;
  subshelfLabel: string;
  callNumber: string;
  skills: string[];
  connectors: string[];
  prompts: string[];
  body: string;
  sourcePath: string;
};

export type Subshelf = {
  slug: string;
  label: string;
  description: string;
  number: number;
  skills: number;
  agents: number;
};

export type Catalog = {
  generatedAt: string;
  repoUrl: string;
  owner: { name: string; github: string; site: string };
  specUrl: string;
  aaifUrl: string;
  studyUrl: string;
  stats: {
    skills: number;
    agents: number;
    categories: number;
    errors: number;
    warnings: number;
    info: number;
    clean: number;
  };
  scoring: {
    start: number;
    errorPenalty: number;
    warningPenalty: number;
    infoPenalty: number;
    floor: number;
  };
  rules: {
    group: string;
    rules: { id: string; severity: string; summary: string }[];
  }[];
  categories: {
    id: string;
    label: string;
    blurb: string;
    number: number;
    count: number;
    agentCount: number;
    subshelves: Subshelf[];
  }[];
  skills: Skill[];
  agents: Agent[];
  drops: { date: string; skills: string[]; agents: string[] }[];
};

export const catalog = raw as Catalog;

export function getSkill(name: string) {
  return catalog.skills.find((skill) => skill.name === name);
}

export function getAgent(name: string) {
  return catalog.agents.find((agent) => agent.name === name);
}

export function skillSummaries() {
  return catalog.skills.map((skill) => ({
    name: skill.name,
    title: skill.title,
    description: skill.description,
    category: skill.category,
    categoryLabel: skill.categoryLabel,
    subshelf: skill.subshelf,
    subshelfLabel: skill.subshelfLabel,
    callNumber: skill.callNumber,
    tags: skill.tags,
    added: skill.added,
    featured: skill.featured,
    score: skill.lint.score,
    badge: skill.lint.badge,
    errors: skill.lint.errors,
    warnings: skill.lint.warnings,
  }));
}

export type SkillSummary = ReturnType<typeof skillSummaries>[number];
