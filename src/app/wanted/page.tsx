import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { catalog } from "@/lib/catalog";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/wanted", {
  title: "Wanted",
  description: `Shelves on ${SITE_NAME} that are still thin. Submissions are most useful where a shelf has little on it.`,
  keywords: ["wanted", "submit a skill", "empty shelves", SITE_NAME],
});

export default function WantedPage() {
  const shelves = [...catalog.categories].sort((a, b) => a.count - b.count || a.number - b.number);
  const thin = shelves.filter((shelf) => shelf.count <= 3);
  const shown = thin.length > 0 ? thin : shelves.slice(0, 8);

  return (
    <ArticleFrame
      title="Wanted"
      lede="These shelves are thin. A submission that does one job on a thin shelf is more useful than another git helper."
      path="/wanted"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Wanted" },
      ]}
    >
      <p>
        Open a pull request with <Link href="/submit">the submit steps</Link>. The command tags the entry{" "}
        <code>source: inbound</code> and records you as the author.
      </p>
      <ul className="stack-list">
        {shown.map((shelf) => (
          <li key={shelf.id}>
            <p>
              <Link href={`/category/${shelf.id}`}>
                {shelf.number} {shelf.label}
              </Link>{" "}
              <span className="quiet">
                {shelf.count} {shelf.count === 1 ? "skill" : "skills"}
              </span>
            </p>
            <p>{shelf.blurb}</p>
            <ul>
              {shelf.subshelves.map((subshelf) => (
                <li key={subshelf.slug}>
                  <Link href={`/category/${shelf.id}/${subshelf.slug}`}>{subshelf.label}</Link>
                  <span className="quiet">
                    {" "}
                    {subshelf.skills} {subshelf.skills === 1 ? "skill" : "skills"}
                  </span>
                  <span className="quiet"> — {subshelf.description}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </ArticleFrame>
  );
}
