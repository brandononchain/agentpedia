import type { FaqItem } from "@/lib/seo";

export function FaqList({ items }: { items: FaqItem[] }) {
  return (
    <dl className="faq-list">
      {items.map((item) => (
        <div key={item.q}>
          <dt>{item.q}</dt>
          <dd>{item.a}</dd>
        </div>
      ))}
    </dl>
  );
}
