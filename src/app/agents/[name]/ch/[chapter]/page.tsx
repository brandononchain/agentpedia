import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { ChapterPager, ChapterProgress } from "@/components/book";
import { MarkdownBody } from "@/components/markdown-body";
import { agentBook, bookChapters, bookCrumbs, chapterBySlug, chapterJsonLd } from "@/lib/book";
import { catalog, getAgent } from "@/lib/catalog";
import { metaDescription } from "@/lib/seo";
import { siteMeta } from "@/lib/site";

type Params = { name: string; chapter: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.agents.flatMap((agent) =>
    bookChapters(agentBook(agent)).map((chapter) => ({ name: agent.name, chapter: chapter.slug })),
  );
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name, chapter: slug } = await params;
  const agent = getAgent(name);
  if (!agent) return { title: "Chapter" };
  const entry = agentBook(agent);
  const chapter = chapterBySlug(bookChapters(entry), slug);
  if (!chapter) return { title: "Chapter" };
  return siteMeta(`/agents/${agent.name}/ch/${chapter.slug}`, {
    title: `${chapter.title} · ${agent.name}`,
    description: metaDescription(`${chapter.title}. ${agent.description}`),
    keywords: [agent.name, chapter.title, agent.subshelfLabel, agent.categoryLabel],
    image: `/agents/${agent.name}/opengraph-image`,
    imageAlt: `${agent.name}, chapter ${chapter.number}: ${chapter.title}. Call number ${agent.callNumber}.`,
  });
}

export default async function AgentChapterPage({ params }: { params: Promise<Params> }) {
  const { name, chapter: slug } = await params;
  const agent = getAgent(name);
  if (!agent) notFound();
  const entry = agentBook(agent);
  const chapters = bookChapters(entry);
  const chapter = chapterBySlug(chapters, slug);
  if (!chapter) notFound();

  return (
    <ArticleFrame
      current={`/category/${agent.category}`}
      mark={agent.callNumber}
      title={chapter.title}
      lede={`${agent.name}. Chapter ${chapter.number} of ${chapters.length}.`}
      path={`/agents/${agent.name}/ch/${chapter.slug}`}
      crumbs={bookCrumbs(entry, { label: chapter.title })}
      structuredData={[chapterJsonLd(entry, chapter)]}
    >
      <ChapterProgress chapter={chapter} total={chapters.length} />
      <MarkdownBody source={chapter.markdown} selfHref={`/agents/${agent.name}/ch/${chapter.slug}`} />
      <ChapterPager entry={entry} chapters={chapters} chapter={chapter} />
    </ArticleFrame>
  );
}
