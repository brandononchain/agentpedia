"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/theme-toggle";
import { SITE_NAME } from "@/lib/site";

const LINKS = [
  { href: "/az", label: "Index" },
  { href: "/#shelves", label: "Shelves" },
  { href: "/agents", label: "Agents" },
  { href: "/changelog", label: "Recent changes" },
  { href: "/lint", label: "How we lint" },
];

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <header className="site-head">
      <div className="site-head-inner">
        <Link href="/" className="wordmark">
          {SITE_NAME}
        </Link>
        <nav id="site-menu" className={open ? "site-nav is-open" : "site-nav"} aria-label="Primary">
          {LINKS.map((link) => {
            const active = link.href !== "/#shelves" && (pathname === link.href || pathname.startsWith(`${link.href}/`));
            return (
              <Link key={link.href} href={link.href} aria-current={active ? "page" : undefined}>
                {link.label}
              </Link>
            );
          })}
        </nav>
        <form className="head-search" action="/browse" role="search">
          <label htmlFor="head-q" className="sr-only">
            Search the encyclopedia
          </label>
          <input id="head-q" name="q" placeholder="Search" />
          <button type="submit">Search</button>
        </form>
        <div className="head-tools">
          <ThemeToggle />
          <button
            type="button"
            className="nav-toggle"
            aria-expanded={open}
            aria-controls="site-menu"
            onClick={() => setOpen((value) => !value)}
          >
            {open ? "Close" : "Menu"}
          </button>
        </div>
      </div>
    </header>
  );
}
