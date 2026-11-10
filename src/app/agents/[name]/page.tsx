import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { CopyButton } from "@/components/copy-button";
import { MarkdownBody } from "@/components/markdown-body";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { formatDropDate, stripTitle } from "@/lib/format";
import { extractToc, otherAgents, type TocItem } from "@/lib/wiki";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.agents.map((agent) => ({ name: agent.name }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) return { title: "Agent" };
  return { title: agent.name, description: agent.description };
}

export default async function AgentPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) notFound();
  const body = stripTitle(agent.body);
  const others = otherAgents(agent);
  const toc: TocItem[] = [
    ...extractToc(body),
    { id: "member-skills", text: "Member skills", depth: 2 },
    { id: "sample-prompts", text: "Sample prompts", depth: 2 },
    { id: "see-also", text: "See also", depth: 2 },
  ];

  return (
    <ArticleFrame
      title={agent.name}
      lede={agent.description}
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/agents", label: "Agents" },
        { label: agent.name },
      ]}
      plate={
        <aside className="plate" aria-label="Agent facts">
          <p className="plate-name">{agent.name}</p>
          <dl>
            <dt>Kind</dt>
            <dd>Agent</dd>
            <dt>Skills</dt>
            <dd>{agent.skills.length}</dd>
            <dt>Added</dt>
            <dd>
              <time dateTime={agent.added}>{formatDropDate(agent.added)}</time>
            </dd>
            <dt>Version</dt>
            <dd>Not recorded</dd>
            <dt>Connectors</dt>
            <dd>{agent.connectors.length === 0 ? "None" : agent.connectors.join("; ")}</dd>
          </dl>
        </aside>
      }
    >
      <Contents items={toc} />
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
