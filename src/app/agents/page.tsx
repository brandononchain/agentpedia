import type { Metadata } from "next";
import Link from "next/link";
import { catalog } from "@/lib/catalog";
import { formatDropDate } from "@/lib/format";

export const metadata: Metadata = {
  title: "Agents",
  description: "Agents that bundle linted Skilldex skills, with the connectors they need.",
};

export default function AgentsPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-12">
      <h1 className="font-serif text-5xl font-light tracking-tight">Agents</h1>
      <p className="mt-3 max-w-2xl text-muted-foreground">
        An agent is a bundle: a job, the skills that do it, and the connectors it may use.
        Every bundled skill has already passed the linter.
      </p>
      <ul className="mt-10 border-t border-border">
        {catalog.agents.map((agent) => (
          <li key={agent.name} className="border-b border-border py-7">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <Link href={`/agents/${agent.name}`} className="font-serif text-3xl font-light tracking-tight">
                {agent.name}
              </Link>
              <span className="font-mono text-xs text-muted-foreground">{formatDropDate(agent.added)}</span>
            </div>
            <p className="mt-3 max-w-3xl text-sm leading-relaxed text-muted-foreground">{agent.description}</p>
            <p className="mt-3 text-sm">
              {agent.skills.map((name, index) => (
                <span key={name}>
                  {index > 0 ? " · " : ""}
                  <Link href={`/skills/${name}`} className="underline decoration-border underline-offset-4">
                    {name}
                  </Link>
                </span>
              ))}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
