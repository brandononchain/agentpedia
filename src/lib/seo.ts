import { catalog } from "@/lib/catalog";
import { REPO_URL, SITE_NAME, SITE_ORIGIN, SITE_TAGLINE } from "@/lib/site";

export const HOME_TITLE = `${SITE_NAME} — ${SITE_TAGLINE}`;

export const HOME_DEFINITION =
  "Agentpedia is the open encyclopedia of agents and skills. A skill is a SKILL.md file that has passed skill-lint. An agent bundles those skills for one job. Shelves group the skills by the work they do.";

export function homeDescription(shelves = catalog.stats.categories) {
  return `Agentpedia is the open, curated encyclopedia of AI agent skills and agents. Every entry is linted to 100, listed, and added daily. Browse all ${shelves} shelves.`;
}

/** Collapse a frontmatter description into a meta description. */
export function metaDescription(text: string) {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= 160) return clean;
  const slice = clean.slice(0, 157);
  const cut = slice.lastIndexOf(" ");
  return `${slice.slice(0, cut > 90 ? cut : 157).replace(/[.,;: ]+$/, "")}…`;
}

export type FaqItem = { q: string; a: string };

export const HOME_FAQ: FaqItem[] = [
  {
    q: "What is Agentpedia?",
    a: "Agentpedia is the open encyclopedia of agents and skills. A skill is a SKILL.md file that has passed skill-lint. An agent bundles those skills for one job.",
  },
  {
    q: "What does a lint score of 100 mean?",
    a: "The score starts at 100. An error subtracts 25, a warning subtracts 8, and an info finding subtracts 2, so 100 means zero of each. The build does not publish a skill that has an error or a warning.",
  },
  {
    q: "What does a certificate mean?",
    a: "A certificate is a public record of a tier: Listed when the lint gate passes, Verified when a recorded check run also passes, and Certified only after a person writes a review. It is not a security audit.",
  },
  {
    q: "How are new entries added?",
    a: "Each skill and agent carries an added date in its file. Recent changes lists those dates. The date is not backdated.",
  },
];

export const CERT_FAQ: FaqItem[] = [
  {
    q: "What does Listed mean?",
    a: "A skill is Listed when skill-lint scores 100, which means zero errors, zero warnings, and zero info findings. An agent is Listed when its manifest is accepted and every bundled skill scores 100. Listed does not run the entry.",
  },
  {
    q: "What does Verified mean?",
    a: "Verified is Listed plus a recorded run of tools/verify_checks.py. The run shows that the declared checks printed what the manifest required. It does not scan the entry for malware.",
  },
  {
    q: "What does Certified mean?",
    a: "Certified is a current Verified run plus a human review stored in the certificate: a GitHub login, a date, and notes. The publisher does not invent that review.",
  },
  {
    q: "What does re-check pending mean?",
    a: "The entry, the harness, or the declared checks changed after the certificate was written, so the old claim is no longer current. Re-check pending takes priority over an expiry date.",
  },
];

export function faqNode(items: FaqItem[]) {
  return {
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: { "@type": "Answer", text: item.a },
    })),
  };
}

export function homeGraph() {
  const origin = SITE_ORIGIN;
  const description = homeDescription();
  const org = `${origin}/#organization`;
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": org,
        name: SITE_NAME,
        url: origin,
        logo: `${origin}/icon-512.png`,
        sameAs: [REPO_URL],
      },
      {
        "@type": "WebSite",
        "@id": `${origin}/#website`,
        name: SITE_NAME,
        url: origin,
        description,
        inLanguage: "en",
        publisher: { "@id": org },
        potentialAction: {
          "@type": "SearchAction",
          target: `${origin}/browse?q={search_term_string}`,
          "query-input": "required name=search_term_string",
        },
      },
      {
        "@type": "Dataset",
        name: `${SITE_NAME} catalog`,
        description: `Machine-readable catalog of ${catalog.stats.skills} skills and ${catalog.stats.agents} agents on ${catalog.stats.categories} shelves.`,
        url: `${origin}/catalog.json`,
        creator: { "@id": org },
        isAccessibleForFree: true,
        distribution: {
          "@type": "DataDownload",
          encodingFormat: "application/json",
          contentUrl: `${origin}/catalog.json`,
        },
      },
      faqNode(HOME_FAQ),
    ],
  };
}
