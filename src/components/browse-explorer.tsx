"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ScoreMark } from "@/components/score-mark";
import type { SkillSummary } from "@/lib/catalog";
import { formatDropDate } from "@/lib/format";
import { cn } from "@/lib/utils";

type Category = { id: string; label: string; count: number };

export function BrowseExplorer({
  skills,
  categories,
}: {
  skills: Array<SkillSummary & { tier?: string }>;
  categories: Category[];
}) {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const q = params.get("q") ?? "";
  const category = params.get("category") ?? "";
  const tag = params.get("tag") ?? "";
  const sort = params.get("sort") ?? "newest";

  function setParam(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    const query = next.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  const tagCounts = new Map<string, number>();
  for (const skill of skills) {
    for (const item of skill.tags) tagCounts.set(item, (tagCounts.get(item) ?? 0) + 1);
  }
  const tags = [...tagCounts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

  const needle = q.trim().toLowerCase();
  const filtered = skills.filter((skill) => {
    if (category && skill.category !== category) return false;
    if (tag && !skill.tags.includes(tag)) return false;
    if (!needle) return true;
    const haystack = [skill.name, skill.title, skill.description, skill.categoryLabel, skill.subshelfLabel, skill.callNumber, ...skill.tags].join(" ").toLowerCase();
    return haystack.includes(needle);
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sort === "score") return b.score - a.score || a.name.localeCompare(b.name);
    if (sort === "name") return a.name.localeCompare(b.name);
    return b.added.localeCompare(a.added) || a.name.localeCompare(b.name);
  });

  const filtersActive = Boolean(q || category || tag || (sort && sort !== "newest"));
  const activeCategory = categories.find((item) => item.id === category);

  return (
    <div className="page-wrap" style={{ padding: "0 0 2rem" }}>
      {activeCategory ? (
        <p className="lede">
          {activeCategory.label} has {activeCategory.count} entries. Narrow them here, or open the shelf page.{" "}
          <Link href={`/category/${activeCategory.id}`}>Open {activeCategory.label}</Link>.
        </p>
      ) : null}

      <div className="search-layout">
        <aside>
          <h2 className="section-title">Shelves</h2>
          <ul className="filters">
            <li>
              <FilterButton active={!category} onClick={() => setParam("category", "")}>
                All <span className="quiet">{skills.length}</span>
              </FilterButton>
            </li>
            {categories.map((item) => (
              <li key={item.id}>
                <FilterButton active={category === item.id} onClick={() => setParam("category", category === item.id ? "" : item.id)}>
                  {item.label} <span className="quiet">{item.count}</span>
                </FilterButton>
              </li>
            ))}
          </ul>
        </aside>
        <div className="wiki-reading">
          <div className="search-fields">
            <div>
              <label htmlFor="shelf-search">Search</label>
              <input
                id="shelf-search"
                className="field"
                value={q}
                onChange={(event) => setParam("q", event.target.value)}
                placeholder="Name, tag, or a job to be done"
              />
            </div>
            <div>
              <label htmlFor="shelf-sort">Sort</label>
              <select
                id="shelf-sort"
                className="select-field"
                value={sort}
                onChange={(event) => setParam("sort", event.target.value === "newest" ? "" : event.target.value)}
              >
                <option value="newest">Newest</option>
                <option value="score">Lint score</option>
                <option value="name">Name</option>
              </select>
            </div>
          </div>

          <div className="tag-list">
            {tags.map(([name]) => (
              <button
                key={name}
                type="button"
                className="tag-chip"
                onClick={() => setParam("tag", tag === name ? "" : name)}
                aria-pressed={tag === name}
              >
                {name}
              </button>
            ))}
          </div>

          <div className="result-meta">
            <p className="quiet" aria-live="polite">
              {sorted.length} {sorted.length === 1 ? "skill" : "skills"}
            </p>
            {filtersActive ? (
              <button type="button" className="text-button" onClick={() => router.replace(pathname, { scroll: false })}>
                Clear filters
              </button>
            ) : null}
          </div>

          {sorted.length === 0 ? (
            <div className="empty-note">
              <h2>Nothing matches</h2>
              <p className="quiet" style={{ marginTop: "0.45rem" }}>
                Try a broader word, or clear the shelf and tag. Every published skill is still lint-clean.
              </p>
              <p className="page-actions">
                <button type="button" className="solid-button" onClick={() => router.replace(pathname, { scroll: false })}>
                  Show every skill
                </button>
              </p>
            </div>
          ) : (
            <ul className="result-list">
              {sorted.map((skill) => (
                <li key={skill.name}>
                  <Link href={`/skills/${skill.name}`}>
                    <span className="entry-row">
                      <span className="shelf-name">{skill.title}</span>
                      <ScoreMark score={skill.score} badge={skill.badge} />
                    </span>
                    <span className="quiet">{skill.description}</span>
                    <span className="quiet">
                      {skill.callNumber} {skill.subshelfLabel} · {skill.categoryLabel}
                      {skill.tier ? ` · ${skill.tier}` : ""} · {formatDropDate(skill.added)}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function FilterButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button type="button" onClick={onClick} aria-pressed={active} className={cn("filter-button")}>
      {children}
    </button>
  );
}
