import { Suspense } from "react";
import Link from "next/link";
import type { Metadata } from "next";
import { BrowseExplorer } from "@/components/browse-explorer";
import { JsonLd } from "@/components/json-ld";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { catalog, skillSummaries } from "@/lib/catalog";
import { absoluteUrl, SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/browse", {
  title: "Search",
  description: `Search ${SITE_NAME} by name, shelf, tag, recency, and lint score.`,
  keywords: ["search", "agent skills", SITE_NAME],
});

export default function BrowsePage() {
  return (
    <>
    <JsonLd
      data={{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: absoluteUrl("/") },
          { "@type": "ListItem", position: 2, name: "Search", item: absoluteUrl("/browse") },
        ],
      }}
    />
    <div className="page-wrap" style={{ padding: "1.4rem 0 0" }}>
      <nav className="crumbs" aria-label="Breadcrumb">
        <Link href="/">Home</Link>
        <span aria-hidden="true"> / </span>
        <span aria-current="page">Search</span>
      </nav>
      <h1 className="entry-title">Search</h1>
      <p className="lede">Search the encyclopedia by name, tag, or the job a skill does.</p>
    </div>
    <Suspense fallback={<p className="page-wrap quiet" style={{ padding: "2rem 0" }}>Opening the index…</p>}>
      <BrowseExplorer
        skills={skillSummaries().map((skill) => ({
          ...skill,
          tier: tierLabel(certificateFor("skill", skill.name)?.payload.displayTier ?? ""),
        }))}
        categories={catalog.categories.map((category) => ({
          id: category.id,
          label: category.label,
          count: category.count,
        }))}
      />
    </Suspense>
    </>
  );
}
