import { Suspense } from "react";
import type { Metadata } from "next";
import { BrowseExplorer } from "@/components/browse-explorer";
import { catalog, skillSummaries } from "@/lib/catalog";

export const metadata: Metadata = {
  title: "Browse",
  description: "Search linted Agent Skills by category, tag, recency, and lint score.",
};

export default function BrowsePage() {
  return (
    <Suspense fallback={<p className="mx-auto max-w-6xl px-5 py-16 text-muted-foreground">Opening the shelf…</p>}>
      <div className="mx-auto max-w-6xl px-5 pt-12">
        <h1 className="font-serif text-5xl font-light tracking-tight">Browse</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          {catalog.stats.skills} skills. Filter by shelf or tag, and sort by the day they landed or by lint score.
        </p>
      </div>
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
