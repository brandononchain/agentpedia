import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { SITE_NAME } from "@/lib/site";

export const metadata: Metadata = {
  title: "Glossary",
  description: `Definitions for the words ${SITE_NAME} uses: skill, agent, shelf, lint score, and drop.`,
};

const TERMS = [
  {
    id: "skill",
    term: "Skill",
    body: (
      <>
        A folder with a <code>SKILL.md</code> file an agent can follow. Each skill in this encyclopedia is one article,
        with steps, an example, and a lint score. See <Link href="/skills/skill-author">Skill author</Link>.
      </>
    ),
  },
  {
    id: "agent",
    term: "Agent",
    body: (
      <>
        A named bundle: a job, the skills that do it, and any connectors it may use. A skill belongs to one agent. The
        list is the <Link href="/agents">agent index</Link>.
      </>
    ),
  },
  {
    id: "shelf",
    term: "Shelf",
    body: (
      <>
        A category of skills, such as <Link href="/category/trading">Trading</Link> or{" "}
        <Link href="/category/skill-authoring">Skill authoring</Link>. Shelves are listed from the{" "}
        <Link href="/#shelves">portal</Link>.
      </>
    ),
  },
  {
    id: "lint-score",
    term: "Lint score",
    body: (
      <>
        The result of skill-lint on an entry. A skill starts at 100. Errors, warnings, and notes subtract from it. This
        catalog ships only entries with no errors and no warnings. The rule list is{" "}
        <Link href="/lint">How we lint</Link>.
      </>
    ),
  },
  {
    id: "drop",
    term: "Drop",
    body: (
      <>
        The day an entry was added. The date lives on the entry. <Link href="/changelog">Recent changes</Link> lists
        them. The site does not backdate a page.
      </>
    ),
  },
  {
    id: "certificate",
    term: "Certificate",
    body: (
      <>
        A public record that a skill or agent passed a named check at one commit. Tiers are Listed, Verified, and
        Certified. The definitions, and what they do not guarantee, are on <Link href="/certification">Certification</Link>.
      </>
    ),
  },
  {
    id: "version",
    term: "Version",
    body: (
      <>
        Not recorded on these entries. The infobox says so rather than inventing a number. The added date is the
        edition the catalog knows.
      </>
    ),
  },
];

export default function GlossaryPage() {
  return (
    <ArticleFrame
      title="Glossary"
      lede={`The words ${SITE_NAME} uses for its own contents. Entry names elsewhere in the encyclopedia link to their articles.`}
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Glossary" },
      ]}
    >
      <Contents items={TERMS.map((term) => ({ id: term.id, text: term.term, depth: 2 as const }))} />
      <dl className="glossary">
        {TERMS.map((term) => (
          <div key={term.id}>
            <dt id={term.id}>{term.term}</dt>
            <dd>{term.body}</dd>
          </div>
        ))}
      </dl>
    </ArticleFrame>
  );
}
