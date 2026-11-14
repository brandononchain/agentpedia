import type { Metadata } from "next";
import Link from "next/link";
import { siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/404", {
  title: "No entry by that name",
  description: "That name is not a skill, an agent, or a shelf in this build of Agentpedia.",
  noindex: true,
});

export default function NotFound() {
  return (
    <div className="page-wrap" style={{ padding: "3rem 0" }}>
      <h1 className="entry-title">No entry by that name</h1>
      <p className="lede">The name does not match a skill, an agent, or a shelf in this build.</p>
      <p style={{ marginTop: "1rem", display: "flex", gap: "1rem" }}>
        <Link href="/az">Index</Link>
        <Link href="/browse">Search</Link>
        <Link href="/agents">Agents</Link>
      </p>
    </div>
  );
}
