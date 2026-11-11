import { Suspense } from "react";
import type { Metadata } from "next";
import { BrowseExplorer } from "@/components/browse-explorer";
import { catalog, skillSummaries } from "@/lib/catalog";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = {
  title: "Search",
  description: `Search ${SITE_NAME} by name, shelf, tag, recency, and lint score.`,
  ...siteMeta("/browse"),
};

export default function BrowsePage() {
  return (
    <Suspense fallback={<p className="page-wrap quiet" style={{ padding: "2rem 0" }}>Opening the index…</p>}>
      <BrowseExplorer
        skills={skillSummaries()}
        categories={catalog.categories.map((category) => ({
          id: category.id,
          label: category.label,
          count: category.count,
        }))}
      />
    </Suspense>
  );
}
