"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/browse", label: "Browse" },
  { href: "/agents", label: "Agents" },
  { href: "/lint", label: "How we lint" },
  { href: "/changelog", label: "Drops" },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-5 py-4">
        <Link href="/" className="flex items-center gap-2.5 text-foreground">
          <Mark className="size-4 text-stamp" />
          <span className="font-serif text-xl tracking-tight">Skilldex</span>
        </Link>
        <nav aria-label="Primary" className="flex gap-4 overflow-x-auto text-sm">
          {LINKS.map((link) => {
            const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "whitespace-nowrap text-muted-foreground hover:text-foreground",
                  active && "text-foreground",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

export function Mark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 16 16" className={className} aria-hidden="true">
      <rect x="1.25" y="1.25" width="13.5" height="13.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
      <rect x="5" y="5" width="6" height="6" fill="currentColor" />
    </svg>
  );
}
