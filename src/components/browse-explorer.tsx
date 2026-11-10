"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScoreMark } from "@/components/score-mark";
import type { SkillSummary } from "@/lib/catalog";
import { formatDropDate } from "@/lib/format";
import { cn } from "@/lib/utils";

type Category = { id: string; label: string; count: number };

export function BrowseExplorer({
  skills,
  categories,
}: {
  skills: SkillSummary[];
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
    for (const item of skill.tags) {
      tagCounts.set(item, (tagCounts.get(item) ?? 0) + 1);
    }
  }
  const tags = [...tagCounts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

  const needle = q.trim().toLowerCase();
  const filtered = skills.filter((skill) => {
    if (category && skill.category !== category) return false;
    if (tag && !skill.tags.includes(tag)) return false;
    if (!needle) return true;
    const haystack = [skill.name, skill.title, skill.description, skill.categoryLabel, ...skill.tags]
      .join(" ")
      .toLowerCase();
    return haystack.includes(needle);
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sort === "score") return b.score - a.score || a.name.localeCompare(b.name);
    if (sort === "name") return a.name.localeCompare(b.name);
    return b.added.localeCompare(a.added) || a.name.localeCompare(b.name);
  });

  const filtersActive = Boolean(q || category || tag || (sort && sort !== "newest"));

  return (
    <div className="mx-auto grid max-w-6xl gap-10 px-5 py-12 lg:grid-cols-[220px_minmax(0,1fr)]">
      <aside className="lg:sticky lg:top-24 lg:self-start">
        <p className="font-mono text-xs tracking-wide text-muted-foreground uppercase">Category</p>
        <ul className="mt-3 flex gap-2 overflow-x-auto pb-1 lg:block lg:overflow-visible">
          <li>
            <FilterButton active={!category} onClick={() => setParam("category", "")}>
              All
              <span className="font-mono text-xs tabular-nums">{skills.length}</span>
            </FilterButton>
          </li>
          {categories.map((item) => (
            <li key={item.id}>
              <FilterButton
                active={category === item.id}
                onClick={() => setParam("category", category === item.id ? "" : item.id)}
              >
                {item.label}
                <span className="font-mono text-xs tabular-nums">{item.count}</span>
              </FilterButton>
            </li>
          ))}
        </ul>
      </aside>

      <div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="flex-1">
            <label htmlFor="shelf-search" className="font-mono text-xs tracking-wide text-muted-foreground uppercase">
              Search
            </label>
            <Input
              id="shelf-search"
              value={q}
              onChange={(event) => setParam("q", event.target.value)}
              placeholder="Name, tag, or a job to be done"
              className="mt-2 h-11 rounded-sm text-base md:text-sm"
            />
          </div>
          <div>
            <label htmlFor="shelf-sort" className="font-mono text-xs tracking-wide text-muted-foreground uppercase">
              Sort
            </label>
            <select
              id="shelf-sort"
              value={sort}
              onChange={(event) => setParam("sort", event.target.value === "newest" ? "" : event.target.value)}
              className="mt-2 block h-11 rounded-sm border border-input bg-background px-3 text-sm"
            >
              <option value="newest">Newest</option>
              <option value="score">Lint score</option>
              <option value="name">Name</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
          {tags.map(([name]) => (
            <button
              key={name}
              type="button"
              onClick={() => setParam("tag", tag === name ? "" : name)}
              className={cn(
                "shrink-0 rounded-sm border px-2 py-1 font-mono text-xs",
                tag === name
                  ? "border-stamp bg-stamp text-primary-foreground"
                  : "border-border text-muted-foreground hover:text-foreground",
              )}
              aria-pressed={tag === name}
            >
              {name}
            </button>
          ))}
        </div>

        <div className="mt-6 flex items-baseline justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            {sorted.length} {sorted.length === 1 ? "skill" : "skills"}
          </p>
          {filtersActive ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => router.replace(pathname, { scroll: false })}
            >
              Clear filters
            </Button>
          ) : null}
        </div>

        {sorted.length === 0 ? (
          <div className="mt-8 border border-dashed border-border px-5 py-12">
            <p className="font-serif text-3xl">Nothing on the shelf matches.</p>
            <p className="mt-3 max-w-md text-sm text-muted-foreground">
              Try a broader word, or clear the category and tag. Every published skill is still lint-clean.
            </p>
            <Button
              type="button"
              className="mt-6 rounded-sm"
              onClick={() => router.replace(pathname, { scroll: false })}
            >
              Show the full shelf
            </Button>
          </div>
        ) : (
          <ul className="mt-4 border-t border-border">
            {sorted.map((skill) => (
              <li key={skill.name} className="border-b border-border">
                <Link
                  href={`/skills/${skill.name}`}
                  className="grid gap-3 py-5 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-start sm:gap-8"
                >
                  <span>
                    <span className="font-serif text-2xl tracking-tight">{skill.title}</span>
                    <span className="mt-1 block max-w-2xl text-sm leading-relaxed text-muted-foreground">
                      {skill.description}
                    </span>
                    <span className="mt-2 block font-mono text-xs text-muted-foreground">
                      {skill.categoryLabel} · {formatDropDate(skill.added)}
                    </span>
                  </span>
                  <ScoreMark score={skill.score} badge={skill.badge} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function FilterButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "flex items-baseline justify-between gap-3 px-2 py-2 text-left text-sm whitespace-nowrap lg:w-full lg:whitespace-normal",
        active ? "bg-foreground text-background" : "text-muted-foreground hover:text-foreground",
      )}
    >
      {children}
    </button>
  );
}
