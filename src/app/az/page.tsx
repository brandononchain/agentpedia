import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { TierMark } from "@/components/tier-mark";
import { certificateFor } from "@/lib/certificates";
import { catalog } from "@/lib/catalog";
import { SITE_NAME, siteMeta } from "@/lib/site";
import { alphabet, groupByLetter } from "@/lib/wiki";

export const metadata: Metadata = siteMeta("/az", {
  title: "Index",
  description: `Alphabetical index of every skill and agent in ${SITE_NAME}, the open encyclopedia of agents and skills.`,
  keywords: ["index", "agent skills", SITE_NAME],
});

type Row = { key: string; title: string; href: string; kind: "Skill" | "Agent"; certId?: string; tier?: string };

export default function IndexPage() {
  const rows: Row[] = [
    ...catalog.skills.map((skill) => {
      const cert = certificateFor("skill", skill.name);
      return {
        key: `skill-${skill.name}`,
        title: skill.title,
        href: `/skills/${skill.name}`,
        kind: "Skill" as const,
        certId: cert?.payload.id,
        tier: cert?.payload.displayTier,
      };
    }),
    ...catalog.agents.map((agent) => {
      const cert = certificateFor("agent", agent.name);
      return {
        key: `agent-${agent.name}`,
        title: agent.name,
        href: `/agents/${agent.name}`,
        kind: "Agent" as const,
        certId: cert?.payload.id,
        tier: cert?.payload.displayTier,
      };
    }),
  ];
  const groups = groupByLetter(rows, (row) => row.title);
  const present = new Set(groups.map(([letter]) => letter));

  return (
    <ArticleFrame
      title="Index"
      lede={`${SITE_NAME} is the open encyclopedia of agents and skills. This index lists every skill and agent by title.`}
      path="/az"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Index" },
      ]}
    >
      <p>
        <Link href="/glossary">Glossary</Link>
        <span className="quiet"> · </span>
        <Link href="/browse">Search</Link>
      </p>
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
      {groups.map(([letter, items]) => (
        <section key={letter} className="letter-block" id={`letter-${letter}`}>
          <h2>{letter}</h2>
          <ul className="letter-list">
            {items.map((item) => (
              <li key={item.key}>
                <Link href={item.href}>{item.title}</Link>
                <span className="quiet"> {item.kind}</span>
                {item.certId && item.tier ? (
                  <>
                    <span className="quiet"> · </span>
                    <TierMark id={item.certId} tier={item.tier} />
                  </>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </ArticleFrame>
  );
}
