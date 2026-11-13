import Link from "next/link";
import { catalog } from "@/lib/catalog";
import { SITE_NAME, SITE_TAGLINE } from "@/lib/site";

export function SiteFooter() {
  return (
    <footer className="site-foot">
      <div className="site-foot-inner">
        <div>
          <p className="foot-name">{SITE_NAME}</p>
          <p className="quiet" style={{ marginTop: "0.4rem", maxWidth: "28rem" }}>
            {SITE_TAGLINE}. Maintained by{" "}
            <a href={catalog.owner.site}>{catalog.owner.name}</a>.
          </p>
        </div>
        <div>
          <p>In this volume</p>
          <ul>
            <li><Link href="/az">Alphabetical index</Link></li>
            <li><Link href="/glossary">Glossary</Link></li>
            <li><Link href="/agents">Agents</Link></li>
            <li><Link href="/changelog">Recent changes</Link></li>
            <li><Link href="/lint">How we lint</Link></li>
            <li><Link href="/certification">Certification</Link></li>
            <li><Link href="/certify">Submit a skill</Link></li>
          </ul>
        </div>
        <div>
          <p>Sources</p>
          <ul>
            <li><a href={catalog.owner.github}>GitHub</a></li>
            <li><a href={catalog.owner.site}>brandononchain.com</a></li>
            <li><a href={catalog.specUrl}>Agent Skills specification</a></li>
            <li><a href={catalog.aaifUrl}>Agentic AI Foundation</a></li>
            <li><a href={catalog.studyUrl}>UC Irvine study</a></li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
