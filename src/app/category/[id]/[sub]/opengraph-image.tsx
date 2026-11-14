import { catalog } from "@/lib/catalog";
import { ogSize, renderOg } from "@/lib/og";

export const runtime = "nodejs";
export const size = ogSize;
export const contentType = "image/png";
export const alt = "Sub-shelf";

export default async function Image({ params }: { params: Promise<{ id: string; sub: string }> }) {
  const { id, sub } = await params;
  const category = catalog.categories.find((item) => item.id === id);
  const subshelf = category?.subshelves.find((item) => item.slug === sub);
  if (!category || !subshelf) return renderOg({ title: "Agentpedia", lines: ["Missing sub-shelf"] });
  const count = subshelf.skills + subshelf.agents;
  return renderOg({
    kicker: `Shelf ${category.number}.${subshelf.number}`,
    title: subshelf.label,
    lines: [category.label, count === 0 ? "Being written" : `${count} ${count === 1 ? "entry" : "entries"}`],
  });
}

export function generateStaticParams() {
  return catalog.categories.flatMap((category) =>
    category.subshelves.map((subshelf) => ({ id: category.id, sub: subshelf.slug })),
  );
}
