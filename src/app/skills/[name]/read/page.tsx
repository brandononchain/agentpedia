import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { BookRead } from "@/components/book";
import { bookChapters, bookCrumbs, bookJsonLd, skillBook } from "@/lib/book";
import { catalog, getSkill } from "@/lib/catalog";
import { metaDescription } from "@/lib/seo";
import { siteMeta } from "@/lib/site";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.skills.map((skill) => ({ name: skill.name }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) return { title: "Book" };
  return siteMeta(`/skills/${skill.name}/read`, {
    title: `${skill.title}, read as one page`,
    description: metaDescription(skill.description),
    keywords: [skill.title, skill.subshelfLabel, skill.categoryLabel, "agent skill"],
    image: `/skills/${skill.name}/opengraph-image`,
    imageAlt: `${skill.title}, read as one page. Call number ${skill.callNumber}.`,
  });
}

export default async function SkillReadPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) notFound();
  const entry = skillBook(skill);
  const chapters = bookChapters(entry);

  return (
    <ArticleFrame
      current={`/category/${skill.category}`}
      mark={skill.callNumber}
      title={skill.title}
      lede={`Read as one page. ${chapters.length} chapters.`}
      path={`/skills/${skill.name}/read`}
      crumbs={bookCrumbs(entry, { label: "Read as one page" })}
      structuredData={[bookJsonLd(entry, chapters)]}
    >
      <p>
        <Link href={`/skills/${skill.name}`}>Title page</Link>
      </p>
      <BookRead entry={entry} chapters={chapters} />
    </ArticleFrame>
  );
}
