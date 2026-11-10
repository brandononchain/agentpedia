"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

type Shelf = { id: string; label: string; count: number };

export function WikiRail({
  current,
  names,
  categories,
}: {
  current?: string;
  names: string[];
  categories: Shelf[];
}) {
  const router = useRouter();

  return (
    <nav className="wiki-rail" aria-label="Encyclopedia">
      <div className="rail-group">
        <p className="rail-label">Find</p>
        <Link href="/az">Index</Link>
        <Link href="/glossary">Glossary</Link>
        <Link href="/changelog">Recent changes</Link>
        <Link href="/lint">How we lint</Link>
        <button
          type="button"
          className="rail-button"
          onClick={() => {
            const name = names[Math.floor(Math.random() * names.length)];
            if (name) router.push(`/skills/${name}`);
          }}
        >
          Random entry
        </button>
      </div>
      <div className="rail-group">
        <p className="rail-label">Shelves</p>
        {categories.map((category) => {
          const href = `/category/${category.id}`;
          return (
            <Link key={category.id} href={href} aria-current={current === href ? "page" : undefined}>
              {category.label}
              <span className="quiet"> {category.count}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
