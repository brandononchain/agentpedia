import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { TierMark } from "@/components/tier-mark";
import { certificateFor } from "@/lib/certificates";
import { catalog } from "@/lib/catalog";
import { absoluteUrl, SITE_NAME, siteMeta } from "@/lib/site";
import { alphabet, firstSentence, groupByLetter } from "@/lib/wiki";

export const metadata: Metadata = siteMeta("/agents", {
  title: "Agents",
  description: `Agents in ${SITE_NAME}, each a bundle of linted skills for one job.`,
  keywords: ["AI agents", "agent skills", SITE_NAME],
});

export default function AgentsPage() {
  const groups = groupByLetter(catalog.agents, (agent) => agent.name);
  const present = new Set(groups.map(([letter]) => letter));

  return (
    <ArticleFrame
      title="Agents"
      lede="An agent is a bundle: a job, the skills that do it, and the connectors it may use. Every bundled skill has already passed the linter. Each skill is listed under one agent."
      path="/agents"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Agents" },
      ]}
      structuredData={[
        {
          "@context": "https://schema.org",
          "@type": "ItemList",
          name: "Agents",
          numberOfItems: catalog.agents.length,
          itemListElement: catalog.agents.map((agent, index) => ({
            "@type": "ListItem",
            position: index + 1,
            name: agent.name,
            url: absoluteUrl(`/agents/${agent.name}`),
          })),
        },
      ]}
    >
      <nav className="letter-jump" aria-label="Letters">
        {alphabet().map((letter) =>
          present.has(letter) ? (
            <a key={letter} href={`#letter-${letter}`}>
              {letter}
            </a>
          ) : (
            <span key={letter}>{letter}</span>
          ),
        )}
      </nav>
      {groups.map(([letter, agents]) => (
        <section key={letter} className="letter-block" id={`letter-${letter}`}>
          <h2>{letter}</h2>
          <ul className="letter-list">
            {agents.map((agent) => (
              <li key={agent.name}>
                <Link href={`/agents/${agent.name}`}>{agent.name}</Link>
                <span className="quiet"> {agent.callNumber}</span>
                {certificateFor("agent", agent.name) ? (
                  <>
                    <span className="quiet"> · </span>
                    <TierMark
                      id={certificateFor("agent", agent.name)!.payload.id}
                      tier={certificateFor("agent", agent.name)!.payload.displayTier}
                    />
                  </>
                ) : null}
                <span className="quiet">
                  {" "}
                  — {agent.skills.length} skills. {firstSentence(agent.description)}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </ArticleFrame>
  );
}
