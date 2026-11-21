/** Plain strings and schema.org builders shared by pages and the JSON-LD test. */

export const SITE_IDENTITY =
  "Agentpedia (agentpedia.sh) is the open, audited encyclopedia of AI agent skills (SKILL.md) and agents.";

export const SITE_NOT =
  "It is not the Microsoft Agent wiki (agentpedia.tmafe.com) or AgentPedia.so.";

export const TITLE_LIMIT = 60;

export const SUBMIT_HOWTO = {
  name: "Submit a skill or an agent to Agentpedia",
  description: "A skill or an agent starts as a pull request. There is no account and no form.",
  steps: [
    {
      name: "Fork or clone",
      text: "Fork the Agentpedia repository, or clone it and create a branch.",
    },
    {
      name: "Scaffold the entry",
      text: "Scaffold the entry. The new-entry command writes the folder, runs skill-lint, runs the static audit, and prints the pull-request commands. It does not push.",
    },
    {
      name: "Replace the example",
      text: "Replace the placeholder example. Run the command again.",
    },
    {
      name: "Open a pull request",
      text: "Commit the entry and open a pull request with the submission template. Do not force-push.",
    },
  ],
};

export const GLOSSARY_TERMS: { id: string; term: string; description: string }[] = [
  {
    id: "agentpedia",
    term: "Agentpedia",
    description: `${SITE_IDENTITY} ${SITE_NOT}`,
  },
  {
    id: "skill",
    term: "Skill",
    description:
      "A folder with a SKILL.md file an agent can follow. Each skill in this encyclopedia is one article, with steps, an example, and a lint score.",
  },
  {
    id: "agent",
    term: "Agent",
    description:
      "A named bundle: a job, the skills that do it, and any connectors it may use. A skill belongs to one agent.",
  },
  {
    id: "shelf",
    term: "Shelf",
    description:
      "A numbered category of skills. Each shelf holds sub-shelves, and a skill or agent is a book on one of them. The call number is the shelf number, then the sub-shelf, as in 11.2.",
  },
  {
    id: "lint-score",
    term: "Lint score",
    description:
      "The result of skill-lint on an entry. A skill starts at 100. Errors, warnings, and notes subtract from it. This catalog ships only entries with no errors and no warnings.",
  },
  {
    id: "drop",
    term: "Drop",
    description: "The day an entry was added. The date lives on the entry. The site does not backdate a page.",
  },
  {
    id: "certificate",
    term: "Certificate",
    description:
      "A public record that a skill or agent passed a named check at one commit, including the static audit of that tree. Tiers are Listed, Verified, and Certified. On hold means the audit blocked listing.",
  },
  {
    id: "version",
    term: "Version",
    description:
      "Not recorded on these entries. The infobox says so rather than inventing a number. The added date is the edition the catalog knows.",
  },
];

type ListItem = { name: string; url: string };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Chapter and read URLs consolidate to the book. They stay out of the sitemap. */
export function isChapterOrReadPath(value: string): boolean {
  let path = value;
  if (value.startsWith("http://") || value.startsWith("https://")) {
    try {
      path = new URL(value).pathname;
    } catch {
      path = value;
    }
  }
  return /\/read$/.test(path) || /\/ch\/[^/]+$/.test(path);
}

export function bookDocumentTitle(
  name: string,
  file: "SKILL.md" | "AGENT.md",
  lintScore?: number,
  auditGrade?: string,
): string {
  const parts: string[] = [file];
  if (typeof lintScore === "number" && Number.isFinite(lintScore)) parts.push(`lint ${lintScore}`);
  if (auditGrade) parts.push(`audit ${auditGrade}`);
  const tail = ` — ${parts.join(" · ")} | Agentpedia`;
  const full = `${name}${tail}`;
  if (full.length <= TITLE_LIMIT) return full;
  const room = TITLE_LIMIT - tail.length - 1;
  if (room < 8) return full;
  let slice = name.slice(0, room);
  const space = slice.lastIndexOf(" ");
  if (space >= 8) slice = slice.slice(0, space);
  slice = slice.replace(/[\s,;:–—-]+$/u, "");
  if (!slice) slice = name.slice(0, room);
  return `${slice}…${tail}`;
}

export function howToLd(origin: string) {
  const root = origin.replace(/\/$/, "");
  return {
    "@context": "https://schema.org",
    "@type": "HowTo",
    name: SUBMIT_HOWTO.name,
    description: SUBMIT_HOWTO.description,
    url: `${root}/submit`,
    step: SUBMIT_HOWTO.steps.map((step, index) => ({
      "@type": "HowToStep",
      position: index + 1,
      name: step.name,
      text: step.text,
      url: `${root}/submit#step-${index + 1}`,
    })),
  };
}

export function definedTermSetLd(origin: string) {
  const root = origin.replace(/\/$/, "");
  return {
    "@context": "https://schema.org",
    "@type": "DefinedTermSet",
    name: "Agentpedia glossary",
    description: `${SITE_IDENTITY} ${SITE_NOT}`,
    url: `${root}/glossary`,
    hasDefinedTerm: GLOSSARY_TERMS.map((term) => ({
      "@type": "DefinedTerm",
      name: term.term,
      description: term.description,
      url: `${root}/glossary#${term.id}`,
      inDefinedTermSet: `${root}/glossary`,
    })),
  };
}

export function datasetLd(input: {
  origin: string;
  name: string;
  description: string;
  pagePath: string;
  contentPath: string;
}) {
  const root = input.origin.replace(/\/$/, "");
  return {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: input.name,
    description: input.description,
    url: `${root}${input.pagePath}`,
    creator: { "@id": `${root}/#organization` },
    isAccessibleForFree: true,
    distribution: {
      "@type": "DataDownload",
      encodingFormat: "application/json",
      contentUrl: `${root}${input.contentPath}`,
    },
  };
}

export function itemListLd(input: { name: string; description?: string; items: ListItem[] }) {
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: input.name,
    ...(input.description ? { description: input.description } : {}),
    numberOfItems: input.items.length,
    itemListElement: input.items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      url: item.url,
    })),
  };
}

export function collectionPageLd(input: {
  name: string;
  description: string;
  url: string;
  items: ListItem[];
}) {
  const list = itemListLd({ name: input.name, description: input.description, items: input.items });
  return {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: input.name,
    description: input.description,
    url: input.url,
    mainEntity: {
      "@type": "ItemList",
      name: list.name,
      description: input.description,
      numberOfItems: list.numberOfItems,
      itemListElement: list.itemListElement,
    },
  };
}

function itemListErrors(data: Record<string, unknown>, label: string): string[] {
  const errors: string[] = [];
  if (data["@type"] !== "ItemList") errors.push(`${label} @type`);
  if (typeof data.name !== "string" || !data.name) errors.push(`${label} name`);
  if (typeof data.numberOfItems !== "number") errors.push(`${label} numberOfItems`);
  if (!Array.isArray(data.itemListElement)) errors.push(`${label} itemListElement`);
  else if (data.itemListElement.length !== data.numberOfItems) errors.push(`${label} length`);
  else {
    data.itemListElement.forEach((item, index) => {
      if (!isRecord(item) || item["@type"] !== "ListItem") errors.push(`${label} item ${index} type`);
      else if (item.position !== index + 1) errors.push(`${label} item ${index} position`);
      else if (typeof item.name !== "string" || !item.name || typeof item.url !== "string" || !item.url) {
        errors.push(`${label} item ${index} fields`);
      }
    });
  }
  return errors;
}

/** Returns shape errors. An empty list means the node matches the type we publish. */
export function jsonLdErrors(data: unknown): string[] {
  if (!isRecord(data)) return ["root must be an object"];
  const errors: string[] = [];
  if (data["@context"] !== "https://schema.org") errors.push("@context");
  const type = data["@type"];
  if (type === "HowTo") {
    if (typeof data.name !== "string" || !data.name) errors.push("HowTo.name");
    if (typeof data.description !== "string" || !data.description) errors.push("HowTo.description");
    if (typeof data.url !== "string" || !data.url.endsWith("/submit")) errors.push("HowTo.url");
    if (!Array.isArray(data.step) || data.step.length === 0) errors.push("HowTo.step");
    else {
      data.step.forEach((step, index) => {
        if (!isRecord(step) || step["@type"] !== "HowToStep") errors.push(`step ${index} type`);
        else if (typeof step.name !== "string" || !step.name || typeof step.text !== "string" || !step.text) {
          errors.push(`step ${index} fields`);
        } else if (step.position !== index + 1) errors.push(`step ${index} position`);
      });
    }
  } else if (type === "DefinedTermSet") {
    if (typeof data.name !== "string" || !data.name) errors.push("DefinedTermSet.name");
    if (typeof data.url !== "string" || !data.url.endsWith("/glossary")) errors.push("DefinedTermSet.url");
    if (!Array.isArray(data.hasDefinedTerm) || data.hasDefinedTerm.length === 0) errors.push("hasDefinedTerm");
    else {
      data.hasDefinedTerm.forEach((term, index) => {
        if (!isRecord(term) || term["@type"] !== "DefinedTerm") errors.push(`term ${index} type`);
        else if (typeof term.name !== "string" || !term.name || typeof term.description !== "string" || !term.description) {
          errors.push(`term ${index} fields`);
        }
      });
    }
  } else if (type === "Dataset") {
    if (typeof data.name !== "string" || !data.name) errors.push("Dataset.name");
    if (typeof data.description !== "string" || !data.description) errors.push("Dataset.description");
    if (typeof data.url !== "string" || !data.url) errors.push("Dataset.url");
    if (data.isAccessibleForFree !== true) errors.push("Dataset.isAccessibleForFree");
    if (!isRecord(data.distribution) || data.distribution["@type"] !== "DataDownload") errors.push("Dataset.distribution");
    else if (typeof data.distribution.contentUrl !== "string" || !data.distribution.contentUrl) {
      errors.push("Dataset.contentUrl");
    }
  } else if (type === "ItemList") {
    errors.push(...itemListErrors(data, "ItemList"));
  } else if (type === "CollectionPage") {
    if (typeof data.name !== "string" || !data.name) errors.push("CollectionPage.name");
    if (typeof data.url !== "string" || !data.url) errors.push("CollectionPage.url");
    if (!isRecord(data.mainEntity)) errors.push("CollectionPage.mainEntity");
    else errors.push(...itemListErrors(data.mainEntity, "mainEntity"));
  } else {
    errors.push(`unsupported @type ${String(type)}`);
  }
  return errors;
}
