import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { CopyButton } from "@/components/copy-button";
import { MarkdownBody } from "@/components/markdown-body";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { formatDropDate, stripTitle } from "@/lib/format";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.agents.map((agent) => ({ name: agent.name }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<Params>;
}): Promise<Metadata> {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) return { title: "Agent" };
  return { title: agent.name, description: agent.description };
}

export default async function AgentPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) notFound();

  return (
    <article className="mx-auto max-w-6xl px-5 py-12">
      <p className="text-sm">
        <Link href="/agents" className="text-muted-foreground underline decoration-border underline-offset-4">
          Agents
        </Link>
      </p>
      <h1 className="mt-4 font-serif text-5xl font-light tracking-tight">{agent.name}</h1>
      <p className="mt-4 max-w-3xl text-lg leading-relaxed text-muted-foreground">{agent.description}</p>
      <p className="mt-3 font-mono text-xs text-muted-foreground">
        {agent.sourcePath} · added {formatDropDate(agent.added)}
      </p>

      <div className="mt-10 grid gap-12 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <MarkdownBody source={stripTitle(agent.body)} />
        <aside className="space-y-8">
          <section>
            <h2 className="font-serif text-2xl font-light">Skills</h2>
            <ul className="mt-3 border-t border-border">
              {agent.skills.map((skillName) => {
                const skill = getSkill(skillName);
                return (
                  <li key={skillName} className="border-b border-border py-3">
                    <Link href={`/skills/${skillName}`} className="font-serif text-lg">
                      {skill?.title ?? skillName}
                    </Link>
                    {skill ? (
                      <p className="mt-1 text-sm text-muted-foreground">{skill.categoryLabel}</p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </section>
          <section>
            <h2 className="font-serif text-2xl font-light">Connectors</h2>
            {agent.connectors.length === 0 ? (
              <p className="mt-3 text-sm text-muted-foreground">None. This agent works from files and text the user supplies.</p>
            ) : (
              <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-muted-foreground">
                {agent.connectors.map((connector) => (
                  <li key={connector}>{connector}</li>
                ))}
              </ul>
            )}
          </section>
        </aside>
      </div>

      <section className="mt-14 border-t border-border pt-8">
        <h2 className="font-serif text-3xl font-light">Sample prompts</h2>
        <ul className="mt-6 space-y-4">
          {agent.prompts.map((prompt) => (
            <li key={prompt} className="flex flex-col gap-3 border border-border p-4 sm:flex-row sm:items-start sm:justify-between">
              <p className="max-w-3xl text-sm leading-relaxed">{prompt}</p>
              <CopyButton text={prompt} label="Copy prompt" />
            </li>
          ))}
        </ul>
      </section>
    </article>
  );
}
