import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { TierMark } from "@/components/tier-mark";
import { certificateFor } from "@/lib/certificates";
import { catalog } from "@/lib/catalog";
import { metaDescription } from "@/lib/seo";
import { absoluteUrl, siteMeta } from "@/lib/site";
import { alphabet, firstSentence, groupByLetter } from "@/lib/wiki";

type Params = { id: string; sub: string };

export const dynamicParams = false;

function lookup(id: string, sub: string) {
  const category = catalog.categories.find((item) => item.id === id);
  const subshelf = category?.subshelves.find((item) => item.slug === sub);
  return { category, subshelf };
}

export function generateStaticParams() {
  return catalog.categories.flatMap((category) =>
    category.subshelves.map((subshelf) => ({ id: category.id, sub: subshelf.slug })),
  );
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { id, sub } = await params;
  const { category, subshelf } = lookup(id, sub);
  if (!category || !subshelf) return { title: "Sub-shelf" };
  const count = subshelf.skills + subshelf.agents;
  const callNumber = `${category.number}.${subshelf.number}`;
  return siteMeta(`/category/${category.id}/${subshelf.slug}`, {
    title: `${subshelf.label} · ${category.label}`,
    description: metaDescription(
      count === 0
        ? `${subshelf.description} This sub-shelf is being written.`
        : `${subshelf.description} ${count} ${count === 1 ? "entry" : "entries"}.`,
    ),
    keywords: [subshelf.label, category.label, "agent skills"],
    image: `/category/${category.id}/${subshelf.slug}/opengraph-image`,
    imageAlt: `${callNumber} ${subshelf.label}, a sub-shelf of ${category.label}.`,
    noindex: count === 0,
  });
}

export default async function SubshelfPage({ params }: { params: Promise<Params> }) {
  const { id, sub } = await params;
  const { category, subshelf } = lookup(id, sub);
  if (!category || !subshelf) notFound();

  const callNumber = `${category.number}.${subshelf.number}`;
  const skills = catalog.skills.filter((skill) => skill.category === category.id && skill.subshelf === subshelf.slug);
  const agents = catalog.agents.filter((agent) => agent.category === category.id && agent.subshelf === subshelf.slug);
  const rows = [
    ...skills.map((skill) => ({
      key: `skill-${skill.name}`,
      title: skill.title,
      href: `/skills/${skill.name}`,
      kind: "Skill" as const,
      sentence: firstSentence(skill.description),
      certKind: "skill" as const,
      name: skill.name,
    })),
    ...agents.map((agent) => ({
      key: `agent-${agent.name}`,
      title: agent.name,
      href: `/agents/${agent.name}`,
      kind: "Agent" as const,
      sentence: firstSentence(agent.description),
      certKind: "agent" as const,
      name: agent.name,
    })),
  ];
  const groups = groupByLetter(rows, (row) => row.title);
  const present = new Set(groups.map(([letter]) => letter));
  const empty = rows.length === 0;

  return (
    <ArticleFrame
      current={`/category/${category.id}`}
      mark={callNumber}
      title={subshelf.label}
      lede={subshelf.description}
      path={`/category/${category.id}/${subshelf.slug}`}
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/#shelves", label: "Shelves" },
        { href: `/category/${category.id}`, label: `${category.number} ${category.label}` },
        { label: subshelf.label },
      ]}
      structuredData={
        empty
          ? []
          : [
              {
                "@context": "https://schema.org",
                "@type": "ItemList",
                name: `${callNumber} ${subshelf.label}`,
                description: subshelf.description,
                numberOfItems: rows.length,
                itemListElement: rows.map((row, index) => ({
                  "@type": "ListItem",
                  position: index + 1,
                  name: row.title,
                  url: absoluteUrl(row.href),
                })),
              },
            ]
      }
    >
      <p>
        <Link href={`/category/${category.id}`}>
          Shelf {category.number} · {category.label}
        </Link>
      </p>
      {empty ? (
        <p className="empty-note">This sub-shelf is being written. The call number is held for the first entry.</p>
      ) : (
        <>
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
                {items.map((item) => {
                  const cert = certificateFor(item.certKind, item.name);
                  return (
                    <li key={item.key}>
                      <Link href={item.href}>{item.title}</Link>
                      <span className="quiet"> {item.kind}</span>
                      {cert ? (
                        <>
                          <span className="quiet"> · </span>
                          <TierMark id={cert.payload.id} tier={cert.payload.displayTier} />
                        </>
                      ) : null}
                      <span className="quiet"> — {item.sentence}</span>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))}
        </>
      )}
    </ArticleFrame>
  );
}
