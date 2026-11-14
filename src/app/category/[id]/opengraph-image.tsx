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
  return renderOg({
    kicker: "Shelf",
    title: category.label,
    lines: [`${category.count} ${category.count === 1 ? "entry" : "entries"}`],
  });
}

export function generateStaticParams() {
  return catalog.categories.map((category) => ({ id: category.id }));
}
