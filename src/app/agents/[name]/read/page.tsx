import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { BookRead } from "@/components/book";
import { agentBook, bookChapters, bookCrumbs, bookJsonLd } from "@/lib/book";
import { catalog, getAgent } from "@/lib/catalog";
import { metaDescription } from "@/lib/seo";
import { siteMeta } from "@/lib/site";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.agents.map((agent) => ({ name: agent.name }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) return { title: "Book" };
  return siteMeta(`/agents/${agent.name}/read`, {
    title: `${agent.name}, read as one page`,
    description: metaDescription(agent.description),
    keywords: [agent.name, agent.subshelfLabel, agent.categoryLabel, "AI agent"],
    image: `/agents/${agent.name}/opengraph-image`,
    imageAlt: `${agent.name}, read as one page. Call number ${agent.callNumber}.`,
  });
}

export default async function AgentReadPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) notFound();
  const entry = agentBook(agent);
  const chapters = bookChapters(entry);

  return (
    <ArticleFrame
      current={`/category/${agent.category}`}
      mark={agent.callNumber}
      title={agent.name}
      lede={`Read as one page. ${chapters.length} chapters.`}
      path={`/agents/${agent.name}/read`}
      crumbs={bookCrumbs(entry, { label: "Read as one page" })}
      structuredData={[bookJsonLd(entry, chapters)]}
    >
      <p>
        <Link href={`/agents/${agent.name}`}>Title page</Link>
      </p>
      <BookRead entry={entry} chapters={chapters} />
    </ArticleFrame>
  );
}
