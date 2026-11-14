import Link from "next/link";
import type { ReactNode } from "react";
import { JsonLd } from "@/components/json-ld";
import { WikiRail } from "@/components/wiki-rail";
import { catalog } from "@/lib/catalog";
import { absoluteUrl } from "@/lib/site";
import type { Crumb } from "@/lib/wiki";

export function ArticleFrame({
  crumbs,
  title,
  lede,
  plate,
  current,
  path,
  mark,
  structuredData,
  children,
}: {
  crumbs: Crumb[];
  title: string;
  lede?: ReactNode;
  plate?: ReactNode;
  current?: string;
  path?: string;
  mark?: string;
  structuredData?: unknown[];
  children: ReactNode;
}) {
  const names = catalog.skills.map((skill) => skill.name);
  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: crumbs.map((crumb, index) => {
      const last = index === crumbs.length - 1;
      const href = crumb.href ?? (last ? path : undefined);
      return {
        "@type": "ListItem",
        position: index + 1,
        name: crumb.label,
        ...(href ? { item: absoluteUrl(href) } : {}),
      };
    }),
  };
  return (
    <div className="wiki-frame">
      <JsonLd data={[breadcrumb, ...(structuredData ?? [])]} />
      <WikiRail
        current={current}
        names={names}
        categories={catalog.categories.map((category) => ({
          id: category.id,
          label: `${category.number} ${category.label}`,
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
        {mark ? <p className="call-number">{mark}</p> : null}
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
