import type { TocItem } from "@/lib/wiki";

export function Contents({ items }: { items: TocItem[] }) {
  if (items.length === 0) return null;
  return (
    <nav className="contents" aria-label="Contents">
      <h2>Contents</h2>
      <ol>
        {items.map((item) => (
          <li key={item.id} className={item.depth === 3 ? "depth-3" : undefined}>
            <a href={`#${item.id}`}>{item.text}</a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
