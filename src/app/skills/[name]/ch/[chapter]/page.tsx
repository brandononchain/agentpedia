import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { ChapterPager, ChapterProgress } from "@/components/book";
import { MarkdownBody } from "@/components/markdown-body";
import { bookChapters, bookCrumbs, chapterBySlug, chapterJsonLd, skillBook } from "@/lib/book";
import { catalog, getSkill } from "@/lib/catalog";
import { metaDescription } from "@/lib/seo";
import { siteMeta } from "@/lib/site";

type Params = { name: string; chapter: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.skills.flatMap((skill) =>
    bookChapters(skillBook(skill)).map((chapter) => ({ name: skill.name, chapter: chapter.slug })),
  );
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name, chapter: slug } = await params;
  const skill = getSkill(name);
  if (!skill) return { title: "Chapter" };
  const entry = skillBook(skill);
  const chapter = chapterBySlug(bookChapters(entry), slug);
  if (!chapter) return { title: "Chapter" };
  return siteMeta(`/skills/${skill.name}/ch/${chapter.slug}`, {
    title: `${chapter.title} · ${skill.title}`,
    description: metaDescription(`${chapter.title}. ${skill.description}`),
    keywords: [skill.title, chapter.title, skill.subshelfLabel, skill.categoryLabel],
    image: `/skills/${skill.name}/opengraph-image`,
    imageAlt: `${skill.title}, chapter ${chapter.number}: ${chapter.title}. Call number ${skill.callNumber}.`,
  });
}

export default async function SkillChapterPage({ params }: { params: Promise<Params> }) {
  const { name, chapter: slug } = await params;
  const skill = getSkill(name);
  if (!skill) notFound();
  const entry = skillBook(skill);
  const chapters = bookChapters(entry);
  const chapter = chapterBySlug(chapters, slug);
  if (!chapter) notFound();

  return (
    <ArticleFrame
      current={`/category/${skill.category}`}
      mark={skill.callNumber}
      title={chapter.title}
      lede={`${skill.title}. Chapter ${chapter.number} of ${chapters.length}.`}
      path={`/skills/${skill.name}/ch/${chapter.slug}`}
      crumbs={bookCrumbs(entry, { label: chapter.title })}
      structuredData={[chapterJsonLd(entry, chapter)]}
    >
      <ChapterProgress chapter={chapter} total={chapters.length} />
      <MarkdownBody source={chapter.markdown} selfHref={`/skills/${skill.name}/ch/${chapter.slug}`} />
      <ChapterPager entry={entry} chapters={chapters} chapter={chapter} />
    </ArticleFrame>
  );
}
