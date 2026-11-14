import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { BookToc } from "@/components/book";
import { CertFact } from "@/components/cert-fact";
import { CopyButton } from "@/components/copy-button";
import { MarkdownBody } from "@/components/markdown-body";
import { agentBook, bookChapters, bookCrumbs, bookJsonLd, recordedCommit } from "@/lib/book";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { metaDescription } from "@/lib/seo";
import { absoluteUrl, siteMeta } from "@/lib/site";
import { formatDropDate, stripTitle } from "@/lib/format";
import { otherAgents } from "@/lib/wiki";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.agents.map((agent) => ({ name: agent.name }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) return { title: "Agent" };
  const tier = certificateFor("agent", agent.name);
  return siteMeta(`/agents/${agent.name}`, {
    title: agent.name,
    description: metaDescription(agent.description),
    keywords: [agent.name, "AI agent", "agent skills"],
    image: `/agents/${agent.name}/opengraph-image`,
    imageAlt: `${agent.name}, call number ${agent.callNumber} ${agent.subshelfLabel}. ${agent.skills.length} skills. ${tier ? tierLabel(tier.payload.displayTier) : "Unlisted"}.`,
  });
}

export default async function AgentPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) notFound();
  const body = stripTitle(agent.body);
  const others = otherAgents(agent);
  const entry = agentBook(agent);
  const chapters = bookChapters(entry);

  return (
    <ArticleFrame
      current={`/category/${agent.category}`}
      mark={agent.callNumber}
      title={agent.name}
      lede={agent.description}
      path={`/agents/${agent.name}`}
      crumbs={bookCrumbs(entry)}
      structuredData={[
        bookJsonLd(entry, chapters),
        {
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          name: agent.name,
          applicationCategory: "AI agent",
          description: agent.description,
          url: absoluteUrl(`/agents/${agent.name}`),
          datePublished: agent.added,
          isPartOf: {
            "@type": "Collection",
            name: agent.subshelfLabel,
            url: absoluteUrl(`/category/${agent.category}/${agent.subshelf}`),
          },
        },
      ]}
      plate={
        <aside className="plate" aria-label="Agent facts">
          <p className="plate-name">{agent.name}</p>
          <dl>
            <dt>Call number</dt>
            <dd>{agent.callNumber}</dd>
            <dt>Shelf</dt>
            <dd>
              <Link href={`/category/${agent.category}`}>
                {agent.shelfNumber} {agent.categoryLabel}
              </Link>
            </dd>
            <dt>Sub-shelf</dt>
            <dd>
              <Link href={`/category/${agent.category}/${agent.subshelf}`}>{agent.subshelfLabel}</Link>
            </dd>
            <dt>Author</dt>
            <dd>{catalog.owner.name}</dd>
            <dt>Source</dt>
            <dd>{agent.sourcePath}</dd>
            <dt>Kind</dt>
            <dd>Agent</dd>
            <CertFact kind="agent" name={agent.name} />
            <dt>Skills</dt>
            <dd>{agent.skills.length}</dd>
            <dt>Added</dt>
            <dd>
              <time dateTime={agent.added}>{formatDropDate(agent.added)}</time>
            </dd>
            <dt>Version</dt>
            <dd>Not recorded</dd>
            <dt>Commit</dt>
            <dd>{recordedCommit("agent", agent.name)}</dd>
            <dt>Connectors</dt>
            <dd>{agent.connectors.length === 0 ? "None" : agent.connectors.join("; ")}</dd>
          </dl>
        </aside>
      }
    >
      <BookToc entry={entry} chapters={chapters} />
      <p className="quiet">The sections below are this book on one page.</p>
      <MarkdownBody source={body} selfHref={`/agents/${agent.name}`} />

      <section className="see-also" id="member-skills">
        <h2 className="section-title">Member skills</h2>
        <ul>
          {agent.skills.map((skillName) => {
            const skill = getSkill(skillName);
            return (
              <li key={skillName}>
                <Link href={`/skills/${skillName}`}>{skill?.title ?? skillName}</Link>
                {skill ? <span className="quiet"> — {skill.categoryLabel}</span> : null}
              </li>
            );
          })}
        </ul>
      </section>

      <section className="see-also" id="sample-prompts">
        <h2 className="section-title">Sample prompts</h2>
        <ul>
          {agent.prompts.map((prompt) => (
            <li key={prompt} style={{ marginTop: "0.7rem" }}>
              <p>{prompt}</p>
              <CopyButton text={prompt} label="Copy prompt" />
            </li>
          ))}
        </ul>
      </section>

      <section className="see-also" id="see-also">
        <h2 className="section-title">See also</h2>
        <ul>
          {others.map((item) => (
            <li key={item.name}>
              <Link href={`/agents/${item.name}`}>{item.name}</Link>
            </li>
          ))}
          <li>
            <Link href="/agents">All agents</Link>
          </li>
        </ul>
      </section>
    </ArticleFrame>
  );
}
