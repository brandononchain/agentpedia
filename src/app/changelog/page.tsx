import type { Metadata } from "next";
import Link from "next/link";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { formatDropDate } from "@/lib/format";

export const metadata: Metadata = {
  title: "Drops",
  description: "Skills and agents by the day they were added to Skilldex.",
};

export default function ChangelogPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-12">
      <h1 className="font-serif text-5xl font-light tracking-tight">Drops</h1>
      <p className="mt-3 max-w-2xl text-muted-foreground">
        Each entry carries the day it was added. A new skill or agent is a drop. Nothing here is backdated by the site;
        the date lives in the entry itself.
      </p>
      <div className="mt-12 space-y-12">
        {catalog.drops.map((drop) => (
          <section key={drop.date}>
            <h2 className="font-serif text-3xl font-light">{formatDropDate(drop.date)}</h2>
            <ul className="mt-4 border-t border-border">
              {drop.skills.map((name) => {
                const skill = getSkill(name);
                if (!skill) return null;
                return (
                  <li key={name} className="grid gap-2 border-b border-border py-4 sm:grid-cols-[8rem_minmax(0,1fr)]">
                    <span className="font-mono text-xs text-muted-foreground uppercase">Skill</span>
                    <span>
                      <Link href={`/skills/${skill.name}`} className="font-serif text-xl">
                        {skill.title}
                      </Link>
                      <span className="mt-1 block text-sm text-muted-foreground">{skill.description}</span>
                    </span>
                  </li>
                );
              })}
              {drop.agents.map((name) => {
                const agent = getAgent(name);
                if (!agent) return null;
                return (
                  <li key={name} className="grid gap-2 border-b border-border py-4 sm:grid-cols-[8rem_minmax(0,1fr)]">
                    <span className="font-mono text-xs text-muted-foreground uppercase">Agent</span>
                    <span>
                      <Link href={`/agents/${agent.name}`} className="font-serif text-xl">
                        {agent.name}
                      </Link>
                      <span className="mt-1 block text-sm text-muted-foreground">{agent.description}</span>
                    </span>
                  </li>
                );
              })}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
