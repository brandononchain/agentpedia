import type { Metadata } from "next";
import Link from "next/link";
import { certificates } from "@/lib/certificates";
import { catalog, getAgent, getSkill } from "@/lib/catalog";
import { FaqList } from "@/components/faq-list";
import { JsonLd } from "@/components/json-ld";
import { HOME_DEFINITION, HOME_FAQ, HOME_TITLE, homeDescription, homeGraph } from "@/lib/seo";
import { SITE_NAME, SITE_TAGLINE, siteMeta } from "@/lib/site";
import { alphabet, didYouKnow, featuredSkill, firstSentence, SHELF_EXPANSION_DATE, SHELF_EXPANSION_IDS } from "@/lib/wiki";
import { formatDropDate } from "@/lib/format";

export const metadata: Metadata = siteMeta("/", {
  absoluteTitle: HOME_TITLE,
  description: homeDescription(),
  keywords: ["Agentpedia", "agent skills", "AI agents", "SKILL.md", "encyclopedia", "shelves"],
});

export default function HomePage() {
  const featured = featuredSkill();
  const featuredAgent = featured ? getAgentFor(featured.name) : undefined;
  const latest = catalog.drops[0];
  const facts = didYouKnow();
  const { stats } = catalog;

  return (
    <div className="portal">
      <JsonLd data={homeGraph()} />
      <h1 className="portal-name">{SITE_NAME}</h1>
      <p className="portal-tagline">{SITE_TAGLINE}</p>
      <div className="portal-rule" aria-hidden="true" />
      <p className="portal-definition">{HOME_DEFINITION}</p>
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
        {stats.clean === stats.skills ? " Every entry scores 100." : ""}{" "}
        <Link href="/certification">
          {certificates.stats.listed} listed
          {certificates.stats.verified ? `, ${certificates.stats.verified} verified` : ""}
        </Link>
        .
      </p>

      <section id="shelves" aria-label="Shelves">
        <nav className="letter-jump" aria-label="Shelves by letter">
          {alphabet().map((letter) => {
            const shelf = catalog.categories.find((category) => category.label.toUpperCase().startsWith(letter));
            return shelf ? (
              <a key={letter} href={`#shelf-${shelf.id}`}>
                {letter}
              </a>
            ) : (
              <span key={letter}>{letter}</span>
            );
          })}
        </nav>
        <ul className="shelf-grid">
          {catalog.categories.map((category) => (
            <li key={category.id} id={`shelf-${category.id}`}>
              <Link href={`/category/${category.id}`}>
                <span className="shelf-id">
                  <span className="shelf-number">{category.number}</span>
                  <span className="shelf-name">{category.label}</span>
                </span>
                <span className="shelf-count">
                  {category.count + category.agentCount === 0 ? "Being written" : category.count}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

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
          {latest?.date === SHELF_EXPANSION_DATE ? (
            <div className="module-copy">
              <p>
                Shelf expansion. Eleven shelves joined the catalog. Each one has three skills and an anchor agent.
              </p>
              <ul className="module-list">
                {catalog.categories
                  .filter((category) => (SHELF_EXPANSION_IDS as readonly string[]).includes(category.id))
                  .sort(
                    (a, b) =>
                      SHELF_EXPANSION_IDS.indexOf(a.id as (typeof SHELF_EXPANSION_IDS)[number]) -
                      SHELF_EXPANSION_IDS.indexOf(b.id as (typeof SHELF_EXPANSION_IDS)[number]),
                  )
                  .map((category) => (
                    <li key={category.id}>
                      <Link href={`/category/${category.id}`}>{category.label}</Link>
                    </li>
                  ))}
                <li>
                  <Link href="/changelog">Recent changes</Link>
                </li>
              </ul>
            </div>
          ) : latest ? (
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
      <section className="portal-faq" id="faq">
        <h2 className="section-title">Questions</h2>
        <FaqList items={HOME_FAQ} />
      </section>
    </div>
  );
}

function getAgentFor(name: string) {
  return catalog.agents.find((agent) => agent.skills.includes(name));
}
