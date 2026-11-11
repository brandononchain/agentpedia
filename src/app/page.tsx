import type { Metadata } from "next";
import Link from "next/link";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { SITE_NAME, SITE_TAGLINE, siteMeta } from "@/lib/site";
import { didYouKnow, featuredSkill, firstSentence } from "@/lib/wiki";
import { formatDropDate } from "@/lib/format";

export const metadata: Metadata = siteMeta("/");

export default function HomePage() {
  const featured = featuredSkill();
  const featuredAgent = featured ? getAgentFor(featured.name) : undefined;
  const latest = catalog.drops[0];
  const facts = didYouKnow();
  const { stats } = catalog;

  return (
    <div className="portal">
      <h1 className="portal-name">{SITE_NAME}</h1>
      <p className="portal-tagline">{SITE_TAGLINE}</p>
      <div className="portal-rule" aria-hidden="true" />
      <form className="portal-search" action="/browse" role="search">
        <label htmlFor="q" className="sr-only">
          Search entries
        </label>
        <input id="q" name="q" placeholder="Search skills, agents, and shelves" />
        <button type="submit">Search</button>
      </form>
      <p className="portal-counts">
        {stats.skills} skills, {stats.agents} agents, and {stats.categories} shelves. This build has {stats.errors} lint
        errors and {stats.warnings} warnings.
        {stats.clean === stats.skills ? " Every entry scores 100." : ""}
      </p>

      <ul className="shelf-grid" id="shelves">
        {catalog.categories.map((category) => (
          <li key={category.id}>
            <Link href={`/category/${category.id}`}>
              <span className="shelf-name">{category.label}</span>
              <span className="shelf-count">{category.count}</span>
            </Link>
          </li>
        ))}
      </ul>

      <div className="modules">
        <section>
          <h2>Featured entry</h2>
          {featured ? (
            <div className="module-copy">
              <p>
                <Link href={`/skills/${featured.name}`}>{featured.title}</Link>
                {featuredAgent ? (
                  <>
                    {" "}
                    is bundled by <Link href={`/agents/${featuredAgent.name}`}>{featuredAgent.name}</Link>
                  </>
                ) : null}
                .
              </p>
              <p className="quiet" style={{ marginTop: "0.55rem" }}>
                {firstSentence(featured.description)}
              </p>
              <p style={{ marginTop: "0.55rem" }}>
                <Link href={`/skills/${featured.name}`}>Read the entry</Link>
              </p>
            </div>
          ) : null}
        </section>

        <section>
          <h2>
            Newly added{latest ? <> <time dateTime={latest.date}>{formatDropDate(latest.date)}</time></> : null}
          </h2>
          {latest ? (
            <ul className="module-list">
              {latest.skills.map((name) => {
                const skill = getSkill(name);
                if (!skill) return null;
                return (
                  <li key={name}>
                    <Link href={`/skills/${skill.name}`}>{skill.title}</Link>
                    <span className="quiet"> {skill.categoryLabel}</span>
                  </li>
                );
              })}
              {latest.agents.map((name) => {
                const agent = getAgent(name);
                if (!agent) return null;
                return (
                  <li key={name}>
                    <Link href={`/agents/${agent.name}`}>{agent.name}</Link>
                    <span className="quiet"> Agent</span>
                  </li>
                );
              })}
              <li>
                <Link href="/changelog">Recent changes</Link>
              </li>
            </ul>
          ) : (
            <p className="module-copy quiet">No dated entries yet.</p>
          )}
        </section>

        <section>
          <h2>Did you know</h2>
          <ul className="module-list">
            {facts.map((fact) => (
              <li key={fact}>…that {fact}?</li>
            ))}
            <li>
              <Link href="/lint">How an entry is checked</Link>
            </li>
          </ul>
        </section>
      </div>
    </div>
  );
}

function getAgentFor(name: string) {
  return catalog.agents.find((agent) => agent.skills.includes(name));
}
