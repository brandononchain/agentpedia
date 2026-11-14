import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { catalog } from "@/lib/catalog";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/az/numbered", {
  title: "Index by call number",
  description: `Every skill and agent in ${SITE_NAME}, listed by shelf and sub-shelf call number.`,
  keywords: ["index", "call number", "shelves", SITE_NAME],
});

export default function NumberedIndexPage() {
  const skills = catalog.skills;
  const agents = catalog.agents;

  return (
    <ArticleFrame
      title="Index"
      lede={`${SITE_NAME} is the open encyclopedia of agents and skills. This view lists every shelf by call number.`}
      path="/az/numbered"
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/az", label: "Index" },
        { label: "Numbered" },
      ]}
    >
      <p className="view-switch">
        <Link href="/az">A–Z</Link>
        <Link href="/az/numbered" aria-current="page">
          Numbered
        </Link>
      </p>
      {catalog.categories.map((shelf) => (
        <section key={shelf.id} className="letter-block" id={`shelf-${shelf.number}`}>
          <h2>
            <Link href={`/category/${shelf.id}`}>
              {shelf.number} {shelf.label}
            </Link>
          </h2>
          <ul className="letter-list">
            {shelf.subshelves.map((subshelf) => {
              const callNumber = `${shelf.number}.${subshelf.number}`;
              const shelfSkills = skills.filter(
                (skill) => skill.category === shelf.id && skill.subshelf === subshelf.slug,
              );
              const shelfAgents = agents.filter(
                (agent) => agent.category === shelf.id && agent.subshelf === subshelf.slug,
              );
              const empty = shelfSkills.length + shelfAgents.length === 0;
              return (
                <li key={subshelf.slug}>
                  {empty ? (
                    <span>
                      <span className="quiet">{callNumber}</span> {subshelf.label}
                      <span className="quiet"> — Being written</span>
                    </span>
                  ) : (
                    <>
                      <Link href={`/category/${shelf.id}/${subshelf.slug}`}>
                        <span className="quiet">{callNumber}</span> {subshelf.label}
                      </Link>
                      <ul>
                        {shelfSkills.map((skill) => (
                          <li key={skill.name}>
                            <Link href={`/skills/${skill.name}`}>{skill.title}</Link>
                            <span className="quiet"> Skill</span>
                          </li>
                        ))}
                        {shelfAgents.map((agent) => (
                          <li key={agent.name}>
                            <Link href={`/agents/${agent.name}`}>{agent.name}</Link>
                            <span className="quiet"> Agent</span>
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </ArticleFrame>
  );
}
