import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { authorGroups } from "@/lib/authors";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/authors", {
  title: "Authors",
  description: `Creators credited on ${SITE_NAME}, with a count of the entries under each name.`,
  keywords: ["authors", "credits", "agent skills", SITE_NAME],
});

export default function AuthorsPage() {
  const groups = authorGroups();
  return (
    <ArticleFrame
      title="Authors"
      lede="Each entry names the person or organization who wrote it. Imported skills also name the curator. Counts include skills and agents."
      path="/authors"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Authors" },
      ]}
    >
      <ul className="stack-list">
        {groups.map((group) => (
          <li key={group.url || group.name}>
            <p>
              {group.url ? <a href={group.url}>{group.name}</a> : group.name}{" "}
              <span className="quiet">
                {group.count} {group.count === 1 ? "entry" : "entries"}
              </span>
            </p>
            <ul>
              {group.entries.map((entry) => (
                <li key={entry.href}>
                  <Link href={entry.href}>{entry.title}</Link>
                  <span className="quiet"> {entry.kind}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </ArticleFrame>
  );
}
