import { catalog } from "@/lib/catalog";
import { ogSize, renderOg } from "@/lib/og";

export const runtime = "nodejs";
export const size = ogSize;
export const contentType = "image/png";
export const alt = "Shelf";

export default async function Image({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const category = catalog.categories.find((item) => item.id === id);
  if (!category) return renderOg({ title: "Agentpedia", lines: ["Missing shelf"] });
  const occupied = category.count + category.agentCount > 0;
  return renderOg({
    kicker: `Shelf ${category.number}`,
    title: category.label,
    lines: [occupied ? `${category.count} ${category.count === 1 ? "skill" : "skills"}` : "Being written"],
  });
}

export function generateStaticParams() {
  return catalog.categories.map((category) => ({ id: category.id }));
}
