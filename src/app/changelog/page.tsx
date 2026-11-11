import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { SITE_NAME, siteMeta } from "@/lib/site";
import { formatDropDate } from "@/lib/format";
import { SHELF_EXPANSION_DATE } from "@/lib/wiki";

export const metadata: Metadata = {
  title: "Recent changes",
  description: `Skills and agents by the day they were added to ${SITE_NAME}.`,
  ...siteMeta("/changelog"),
};

export default function ChangelogPage() {
  return (
    <ArticleFrame
      title="Recent changes"
      lede="A log of entries by the day they were added. A new skill or agent is a drop. The date lives on the entry. This page does not backdate anything."
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Recent changes" },
      ]}
    >
      {catalog.drops.map((drop) => (
        <section key={drop.date} className="letter-block">
          <h2>
            <time dateTime={drop.date}>{formatDropDate(drop.date)}</time>
          </h2>
          {drop.date === SHELF_EXPANSION_DATE ? (
            <p>
              Shelf expansion. Eleven new shelves, with three skills and an anchor agent on each. Entries already
              dated this day stay in the list below.
            </p>
          ) : null}
          <ul className="change-list">
            {drop.skills.map((name) => {
              const skill = getSkill(name);
              if (!skill) return null;
              return (
                <li key={name}>
                  <span className="change-op">added</span>
                  <Link href={`/skills/${skill.name}`}>{skill.title}</Link>
                  <span className="quiet"> skill · {skill.categoryLabel}</span>
                </li>
              );
            })}
            {drop.agents.map((name) => {
              const agent = getAgent(name);
              if (!agent) return null;
              return (
                <li key={name}>
                  <span className="change-op">added</span>
                  <Link href={`/agents/${agent.name}`}>{agent.name}</Link>
                  <span className="quiet"> agent · {agent.skills.length} skills</span>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </ArticleFrame>
  );
}
