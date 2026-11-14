import Link from "next/link";
import { MarkdownBody } from "@/components/markdown-body";
import { bookBase, type BookEntry, type Chapter } from "@/lib/book";

export function BookToc({ entry, chapters }: { entry: BookEntry; chapters: Chapter[] }) {
  const base = bookBase(entry);
  return (
    <nav className="book-toc" aria-label="Table of contents">
      <h2 className="section-title">Contents</h2>
      <ol>
        {chapters.map((chapter) => (
          <li key={chapter.slug}>
            <Link href={`${base}/ch/${chapter.slug}`}>
              <span className="quiet">{chapter.number}.</span> {chapter.title}
            </Link>
          </li>
        ))}
      </ol>
      <p>
        <Link href={`${base}/read`}>Read as one page</Link>
      </p>
    </nav>
  );
}

export function ChapterProgress({ chapter, total }: { chapter: Chapter; total: number }) {
  const width = `${Math.round((chapter.number / total) * 100)}%`;
  return (
    <p className="chapter-progress">
      Chapter {chapter.number} of {total}
      <span className="chapter-meter" aria-hidden="true">
        <span style={{ width }} />
      </span>
    </p>
  );
}

export function ChapterPager({
  entry,
  chapters,
  chapter,
}: {
  entry: BookEntry;
  chapters: Chapter[];
  chapter: Chapter;
}) {
  const base = bookBase(entry);
  const prev = chapters[chapter.number - 2];
  const next = chapters[chapter.number];
  return (
    <nav className="pager" aria-label="Chapters">
      <div>
        {prev ? (
          <Link href={`${base}/ch/${prev.slug}`} rel="prev">
            <span className="quiet">Previous</span>
            <span style={{ display: "block" }}>
              {prev.number}. {prev.title}
            </span>
          </Link>
        ) : (
          <Link href={base}>
            <span className="quiet">Title page</span>
            <span style={{ display: "block" }}>{entry.title}</span>
          </Link>
        )}
      </div>
      <div className="pager-next">
        {next ? (
          <Link href={`${base}/ch/${next.slug}`} rel="next">
            <span className="quiet">Next</span>
            <span style={{ display: "block" }}>
              {next.number}. {next.title}
            </span>
          </Link>
        ) : (
          <Link href={`${base}/read`}>
            <span className="quiet">One page</span>
            <span style={{ display: "block" }}>Read the whole book</span>
          </Link>
        )}
      </div>
    </nav>
  );
}

export function BookRead({ entry, chapters }: { entry: BookEntry; chapters: Chapter[] }) {
  const base = bookBase(entry);
  return (
    <div className="book-read">
      {chapters.map((chapter) => (
        <section key={chapter.slug} id={chapter.slug} className="book-chapter">
          <h2 className="section-title">
            <Link href={`${base}/ch/${chapter.slug}`}>
              {chapter.number}. {chapter.title}
            </Link>
          </h2>
          <MarkdownBody source={chapter.markdown} selfHref={`${base}/ch/${chapter.slug}`} />
        </section>
      ))}
    </div>
  );
}
