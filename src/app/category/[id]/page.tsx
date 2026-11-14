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

type Params = { id: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.categories.map((category) => ({ id: category.id }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { id } = await params;
  const category = catalog.categories.find((item) => item.id === id);
  if (!category) return { title: "Shelf" };
  const occupied = category.count + category.agentCount > 0;
  return siteMeta(`/category/${category.id}`, {
    title: category.label,
    description: metaDescription(
      occupied
        ? `Shelf ${category.number}. ${category.blurb} ${category.count} ${category.count === 1 ? "skill" : "skills"}.`
        : `Shelf ${category.number}. ${category.blurb} This shelf is being written.`,
    ),
    keywords: [category.label, "agent skills", "shelf"],
    image: `/category/${category.id}/opengraph-image`,
    imageAlt: `Shelf ${category.number}, ${category.label}. ${occupied ? `${category.count} skills.` : "Being written."}`,
    noindex: !occupied,
  });
}

export default async function CategoryPage({ params }: { params: Promise<Params> }) {
  const { id } = await params;
  const category = catalog.categories.find((item) => item.id === id);
  if (!category) notFound();

  const skills = catalog.skills.filter((skill) => skill.category === category.id);
  const groups = groupByLetter(skills, (skill) => skill.title);
  const present = new Set(groups.map(([letter]) => letter));

  return (
    <ArticleFrame
      current={`/category/${category.id}`}
      mark={`Shelf ${category.number}`}
      title={category.label}
      lede={
        <>
          {category.blurb}{" "}
          {category.count + category.agentCount === 0
            ? "This shelf is being written."
            : `${category.count} ${category.count === 1 ? "skill" : "skills"}, listed by title.`}
        </>
      }
      path={`/category/${category.id}`}
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/#shelves", label: "Shelves" },
        { label: category.label },
      ]}
      structuredData={[
        {
          "@context": "https://schema.org",
          "@type": "ItemList",
          name: category.label,
          description: category.blurb,
          numberOfItems: skills.length,
          itemListElement: skills.map((skill, index) => ({
            "@type": "ListItem",
            position: index + 1,
            name: skill.title,
            url: absoluteUrl(`/skills/${skill.name}`),
          })),
        },
      ]}
    >
      <ul className="subshelf-list">
        {category.subshelves.map((subshelf) => {
          const count = subshelf.skills + subshelf.agents;
          const callNumber = `${category.number}.${subshelf.number}`;
          return (
            <li key={subshelf.slug}>
              <Link href={`/category/${category.id}/${subshelf.slug}`}>
                <span className="quiet">{callNumber}</span>
                <span>
                  {subshelf.label}
                  <span className="quiet"> — {count === 0 ? "Being written" : subshelf.description}</span>
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
      {skills.length === 0 ? (
        <p className="empty-note">This shelf is being written. Its sub-shelves are reserved.</p>
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
                {items.map((skill) => (
                  <li key={skill.name}>
                    <Link href={`/skills/${skill.name}`}>{skill.title}</Link>
                    {certificateFor("skill", skill.name) ? (
                      <>
                        <span className="quiet"> · </span>
                        <TierMark
                          id={certificateFor("skill", skill.name)!.payload.id}
                          tier={certificateFor("skill", skill.name)!.payload.displayTier}
                        />
                      </>
                    ) : null}
                    <span className="quiet"> — {firstSentence(skill.description)}</span>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </>
      )}
    </ArticleFrame>
  );
}
