import Link from "next/link";
import type { ReactNode } from "react";
import { WikiRail } from "@/components/wiki-rail";
import { catalog } from "@/lib/catalog";
import type { Crumb } from "@/lib/wiki";

export function ArticleFrame({
  crumbs,
  title,
  lede,
  plate,
  current,
  children,
}: {
  crumbs: Crumb[];
  title: string;
  lede?: ReactNode;
  plate?: ReactNode;
  current?: string;
  children: ReactNode;
}) {
  const names = catalog.skills.map((skill) => skill.name);
  return (
    <div className="wiki-frame">
      <WikiRail
        current={current}
        names={names}
        categories={catalog.categories.map((category) => ({
          id: category.id,
          label: category.label,
          count: category.count,
        }))}
      />
      <div>
        <nav className="crumbs" aria-label="Breadcrumb">
          <ol className="flex flex-wrap gap-x-2 gap-y-1">
            {crumbs.map((crumb, index) => {
              const last = index === crumbs.length - 1;
              return (
                <li key={`${crumb.label}-${index}`} className="flex gap-2">
                  {index > 0 ? <span aria-hidden="true">/</span> : null}
                  {crumb.href && !last ? <Link href={crumb.href}>{crumb.label}</Link> : <span aria-current={last ? "page" : undefined}>{crumb.label}</span>}
                </li>
              );
            })}
          </ol>
        </nav>
        <h1 className="entry-title">{title}</h1>
        {lede ? <div className="lede">{lede}</div> : null}
        <div className="wiki-split">
          {plate}
          <div className="wiki-reading">{children}</div>
        </div>
      </div>
    </div>
  );
}
