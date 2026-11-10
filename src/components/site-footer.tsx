import Link from "next/link";
import { catalog } from "@/lib/catalog";
import { Mark } from "@/components/site-header";

export function SiteFooter() {
  return (
    <footer className="mt-24 bg-vellum text-vellum-ink">
      <div className="mx-auto grid max-w-6xl gap-10 px-5 py-14 sm:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <p className="flex items-center gap-2 font-serif text-2xl">
            <Mark className="size-4 text-stamp-ink" />
            Skilldex
          </p>
          <p className="mt-3 max-w-sm text-sm leading-relaxed text-vellum-dim">
            A curated directory of Agent Skills and the agents that bundle them.
            Maintained by{" "}
            <a className="underline decoration-vellum-ink/40 underline-offset-4" href={catalog.owner.site}>
              {catalog.owner.name}
            </a>
            .
          </p>
        </div>
        <div className="text-sm leading-7">
          <p className="font-medium">Catalog</p>
          <ul>
            <li><Link className="underline decoration-vellum-ink/30 underline-offset-4" href="/browse">Browse skills</Link></li>
            <li><Link className="underline decoration-vellum-ink/30 underline-offset-4" href="/agents">Agents</Link></li>
            <li><Link className="underline decoration-vellum-ink/30 underline-offset-4" href="/lint">How we lint</Link></li>
            <li><Link className="underline decoration-vellum-ink/30 underline-offset-4" href="/changelog">Daily drops</Link></li>
          </ul>
        </div>
        <div className="text-sm leading-7">
          <p className="font-medium">Outside</p>
          <ul>
            <li><a className="underline decoration-vellum-ink/30 underline-offset-4" href={catalog.owner.github}>GitHub</a></li>
            <li><a className="underline decoration-vellum-ink/30 underline-offset-4" href={catalog.owner.site}>brandononchain.com</a></li>
            <li><a className="underline decoration-vellum-ink/30 underline-offset-4" href={catalog.specUrl}>Agent Skills spec</a></li>
            <li><a className="underline decoration-vellum-ink/30 underline-offset-4" href={catalog.aaifUrl}>Linux Foundation AAIF</a></li>
            <li><a className="underline decoration-vellum-ink/30 underline-offset-4" href={catalog.studyUrl}>UC Irvine study</a></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-vellum-ink/15">
        <p className="mx-auto max-w-6xl px-5 py-4 text-xs text-vellum-dim">
          Apache-2.0. Skills follow the Agent Skills format, now a project of the Agentic AI Foundation.
        </p>
      </div>
    </footer>
  );
}
