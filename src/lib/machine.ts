import { readFileSync } from "node:fs";
import { join } from "node:path";
import { catalog, type Agent, type Skill } from "@/lib/catalog";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { absoluteUrl, SITE_NAME, SITE_ORIGIN } from "@/lib/site";
import { homeDescription, metaDescription } from "@/lib/seo";

function oneLine(text: string) {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= 180) return clean;
  const slice = clean.slice(0, 177);
  const cut = slice.lastIndexOf(" ");
  return `${slice.slice(0, cut > 80 ? cut : 177).replace(/[.,;: ]+$/, "")}.`;
}

function skillFile(skill: Skill) {
  return join(process.cwd(), skill.sourcePath, "SKILL.md");
}

function agentFile(agent: Agent) {
  return join(process.cwd(), agent.sourcePath, "AGENT.md");
}

export function readSkillMarkdown(skill: Skill) {
  return readFileSync(skillFile(skill), "utf8");
}

export function readAgentMarkdown(agent: Agent) {
  return readFileSync(agentFile(agent), "utf8");
}

export function llmsTxt() {
  const origin = SITE_ORIGIN;
  const { stats } = catalog;
  const lines = [
    `# ${SITE_NAME}`,
    "",
    `> ${homeDescription(stats.categories)}`,
    "",
    HOME_NOTE,
    "",
    "## Shelves",
    ...catalog.categories.flatMap((category) => {
      const block = [
        "",
        `### ${category.number} ${category.label}`,
        "",
        `${oneLine(category.blurb)} ${category.count} skills.`,
      ];
      for (const subshelf of category.subshelves) {
        const callNumber = `${category.number}.${subshelf.number}`;
        const href = absoluteUrl(`/category/${category.id}/${subshelf.slug}`);
        block.push("", `#### ${callNumber} ${subshelf.label}`, "");
        const skills = catalog.skills.filter(
          (skill) => skill.category === category.id && skill.subshelf === subshelf.slug,
        );
        const agents = catalog.agents.filter(
          (agent) => agent.category === category.id && agent.subshelf === subshelf.slug,
        );
        if (skills.length + agents.length === 0) {
          block.push(`Being written. ${oneLine(subshelf.description)}`);
          continue;
        }
        block.push(`[${subshelf.label}](${href}): ${oneLine(subshelf.description)}`);
        for (const skill of skills) {
          const tier = certificateFor("skill", skill.name);
          const mark = tier ? tierLabel(tier.payload.displayTier) : "unlisted";
          block.push(
            `- [${skill.title}](${absoluteUrl(`/skills/${skill.name}`)}): ${oneLine(skill.description)} Call number ${skill.callNumber}. Lint ${skill.lint.score}. ${mark}. Markdown: ${absoluteUrl(`/skills/${skill.name}.md`)}.`,
          );
        }
        for (const agent of agents) {
          const tier = certificateFor("agent", agent.name);
          const mark = tier ? tierLabel(tier.payload.displayTier) : "unlisted";
          block.push(
            `- [${agent.name}](${absoluteUrl(`/agents/${agent.name}`)}): ${oneLine(agent.description)} Call number ${agent.callNumber}. ${agent.skills.length} skills. ${mark}. Markdown: ${absoluteUrl(`/agents/${agent.name}.md`)}.`,
          );
        }
      }
      return block;
    }),
    "",
    "## Key pages",
    `- [Home](${origin}/): ${oneLine(homeDescription(stats.categories))}`,
    `- [Search](${origin}/browse): Search skills by name, shelf, tag, and lint score.`,
    `- [Index](${origin}/az): Every skill and agent, listed A–Z. Numbered view: ${origin}/az/numbered.`,
    `- [Agents](${origin}/agents): Each agent bundles skills for one job.`,
    `- [Recent changes](${origin}/changelog): Entries by the day they were added.`,
    `- [How we lint](${origin}/lint): The skill-lint score and the rules behind it.`,
    `- [Glossary](${origin}/glossary): Skill, agent, shelf, score, and drop.`,
    `- [Certification](${origin}/certification): Listed, Verified, and Certified, and what they do not guarantee.`,
    `- [Catalog JSON](${origin}/catalog.json): Machine-readable catalog of every entry.`,
    `- [RSS](${origin}/feed.xml): Recent changes as a feed.`,
    "",
  ];
  return lines.join("\n");
}

const HOME_NOTE =
  "Raw SKILL.md and AGENT.md files are the same path as the article with a .md suffix. The full text of every entry is /llms-full.txt.";

export function llmsFullTxt() {
  const parts = [
    `# ${SITE_NAME}`,
    "",
    `> ${homeDescription(catalog.stats.categories)}`,
    "",
    "The blocks below are the files in the repository, concatenated.",
    "",
  ];
  for (const skill of catalog.skills) {
    parts.push(`## ${skill.sourcePath}/SKILL.md`, "", readSkillMarkdown(skill).trimEnd(), "");
  }
  for (const agent of catalog.agents) {
    parts.push(`## ${agent.sourcePath}/AGENT.md`, "", readAgentMarkdown(agent).trimEnd(), "");
  }
  return parts.join("\n");
}

export function escapeXml(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

type FeedEntry = { title: string; href: string; date: string; summary: string };

function feedEntries(): FeedEntry[] {
  const skills = catalog.skills.map((skill) => ({
    title: skill.title,
    href: absoluteUrl(`/skills/${skill.name}`),
    date: skill.added,
    summary: metaDescription(skill.description),
  }));
  const agents = catalog.agents.map((agent) => ({
    title: agent.name,
    href: absoluteUrl(`/agents/${agent.name}`),
    date: agent.added,
    summary: metaDescription(agent.description),
  }));
  return [...skills, ...agents].sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : a.title.localeCompare(b.title)));
}

export function rssXml() {
  const items = feedEntries()
    .map((entry) => {
      const pub = new Date(`${entry.date}T00:00:00Z`).toUTCString();
      return `  <item>
    <title>${escapeXml(entry.title)}</title>
    <link>${escapeXml(entry.href)}</link>
    <guid>${escapeXml(entry.href)}</guid>
    <pubDate>${pub}</pubDate>
    <description>${escapeXml(entry.summary)}</description>
  </item>`;
    })
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>${escapeXml(SITE_NAME)} recent changes</title>
  <link>${escapeXml(absoluteUrl("/changelog"))}</link>
  <description>${escapeXml(homeDescription())}</description>
  <language>en</language>
${items}
</channel>
</rss>
`;
}

export function atomXml() {
  const updated = catalog.drops[0]?.date ? `${catalog.drops[0].date}T00:00:00Z` : new Date().toISOString();
  const items = feedEntries()
    .map(
      (entry) => `  <entry>
    <title>${escapeXml(entry.title)}</title>
    <link href="${escapeXml(entry.href)}"/>
    <id>${escapeXml(entry.href)}</id>
    <updated>${entry.date}T00:00:00Z</updated>
    <summary>${escapeXml(entry.summary)}</summary>
  </entry>`,
    )
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>${escapeXml(SITE_NAME)} recent changes</title>
  <link href="${escapeXml(absoluteUrl("/atom.xml"))}" rel="self"/>
  <link href="${escapeXml(absoluteUrl("/changelog"))}"/>
  <id>${escapeXml(absoluteUrl("/changelog"))}</id>
  <updated>${updated}</updated>
${items}
</feed>
`;
}
