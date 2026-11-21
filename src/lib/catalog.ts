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

export type AuditSeverity = "critical" | "high" | "medium" | "low" | "info";

export type AuditFinding = {
  ruleId: string;
  severity: AuditSeverity;
  path: string;
  line: number;
  evidence: string;
  message: string;
  remediation: string;
  cwe: string;
  owasp: string[];
};

export type AuditStage = {
  id: string;
  phase: number;
  title: string;
  status: string;
  detail: string;
};

export type AuditView = {
  score: number;
  grade: "A" | "B" | "C" | "D" | "F";
  status: "passed" | "warning" | "on-hold";
  summary: string;
  graceDays: number;
  graceDaysLeft: number | null;
  counts: Record<AuditSeverity, number>;
  findings: AuditFinding[];
  auditedCommit: string;
  contentDigest: string;
  lockHash: string;
  lockHashAlg: string;
  rulesetVersion: string;
  auditor: string;
  auditedAt: string;
  expiresAt: string;
  cveLookup: string;
  stages: AuditStage[];
};

export type AuditRule = {
  id: string;
  family: string;
  severity: string;
  summary: string;
  remediation: string;
  cwe: string;
  owasp: string[];
};

export type AuditCatalog = {
  rulesetVersion: string;
  auditor: string;
  weights: Record<string, number>;
  graceDays: number;
  auditDays: number;
  rules: AuditRule[];
  stats: {
    entries: number;
    grades: Record<string, number>;
    passed: number;
    warning: number;
    onHold: number;
  };
};

export type Upstream = {
  repo: string;
  commit: string;
  path: string;
  license: string;
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
  author: string;
  authorUrl: string;
  authorKind: "person" | "organization";
  curator: string;
  source: string;
  upstream: Upstream | null;
  lint: {
    score: number;
    errors: number;
    warnings: number;
    info: number;
    badge: BadgeName;
    findings: Finding[];
  };
  audit?: AuditView;
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
  author: string;
  authorUrl: string;
  authorKind: "person" | "organization";
  curator: string;
  source: string;
  upstream: Upstream | null;
  audit?: AuditView;
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
  audit?: AuditCatalog;
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
