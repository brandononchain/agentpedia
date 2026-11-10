import Link from "next/link";
import { ScoreMark } from "@/components/score-mark";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { catalog, getSkill } from "@/lib/catalog";
import { formatBytes, formatDropDate } from "@/lib/format";

export default function HomePage() {
  const { stats } = catalog;
  const latest = catalog.drops[0];
  const generatedDay = catalog.generatedAt.slice(0, 10);
  const dropHeading = latest && latest.date === generatedDay ? "New today" : "Latest drop";
  const specimen = getSkill("skill-author") ?? catalog.skills.find((skill) => skill.featured) ?? catalog.skills[0];
  const featured = catalog.skills
    .filter((skill) => skill.featured)
    .sort((a, b) => {
      if (a.name === "skill-author") return -1;
      if (b.name === "skill-author") return 1;
      return b.added.localeCompare(a.added) || a.name.localeCompare(b.name);
    });

  return (
    <div>
      <section className="mx-auto grid max-w-6xl items-end gap-12 px-5 pt-16 pb-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(18rem,0.85fr)] lg:pt-24">
        <div>
          <h1 className="max-w-[14ch] font-serif text-[clamp(2.7rem,6.4vw,5.2rem)] leading-[0.96] font-light tracking-[-0.03em] text-balance">
            Every skill here was linted before it was allowed to ship.
          </h1>
          <p className="mt-6 max-w-[62ch] text-lg leading-relaxed text-muted-foreground">
            Hong, Imani, and Ahmed at UC Irvine read 238 real <span className="font-mono text-base text-foreground">SKILL.md</span> files.
            237 of them had at least one skill smell, and the smells did not fade as the files aged.
            Skilldex keeps the opposite rule: an error or a warning, and the entry does not ship.
          </p>
          <p className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm">
            <a className="text-stamp underline decoration-stamp/40 underline-offset-4" href={catalog.studyUrl}>
              Read the study
            </a>
            <Link className="text-stamp underline decoration-stamp/40 underline-offset-4" href="/lint">
              See the rules
            </Link>
            <Link className="text-stamp underline decoration-stamp/40 underline-offset-4" href="/browse">
              Browse the shelf
            </Link>
          </p>
        </div>
        {specimen ? <AssayCard name={specimen.name} /> : null}
      </section>

      <section className="mx-auto max-w-6xl px-5 pb-16">
        <form action="/browse" className="flex flex-col gap-3 sm:flex-row">
          <label htmlFor="q" className="sr-only">
            Search skills
          </label>
          <Input
            id="q"
            name="q"
            placeholder="Search skills by name, tag, or job"
            className="h-12 flex-1 rounded-sm px-4 text-base md:text-base"
          />
          <Button type="submit" className="h-12 rounded-sm px-6">
            Search
          </Button>
        </form>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-muted-foreground">
          The shelf holds {stats.skills} skills and {stats.agents} agents across {stats.categories} categories.
          This build has {stats.errors} lint errors and {stats.warnings} warnings.
          {stats.clean === stats.skills ? " Every entry is clean." : ""}
        </p>
      </section>

      {latest ? (
        <section className="border-t border-border">
          <div className="mx-auto max-w-6xl px-5 py-14">
            <h2 className="font-serif text-4xl font-light tracking-tight">
              {dropHeading}{" "}
              <span className="text-muted-foreground">{formatDropDate(latest.date)}</span>
            </h2>
            <ul className="mt-8 border-t border-border">
              {latest.skills.map((name) => {
                const skill = catalog.skills.find((item) => item.name === name);
                if (!skill) return null;
                return (
                  <li key={name} className="border-b border-border">
                    <Link href={`/skills/${skill.name}`} className="grid gap-2 py-4 sm:grid-cols-[14rem_minmax(0,1fr)_auto] sm:items-baseline sm:gap-6">
                      <span className="font-serif text-xl">{skill.title}</span>
                      <span className="text-sm text-muted-foreground">{skill.categoryLabel}</span>
                      <ScoreMark score={skill.lint.score} badge={skill.lint.badge} />
                    </Link>
                  </li>
                );
              })}
              {latest.agents.map((name) => {
                const agent = catalog.agents.find((item) => item.name === name);
                if (!agent) return null;
                return (
                  <li key={name} className="border-b border-border">
                    <Link href={`/agents/${agent.name}`} className="grid gap-2 py-4 sm:grid-cols-[14rem_minmax(0,1fr)_auto] sm:items-baseline sm:gap-6">
                      <span className="font-serif text-xl">{agent.name}</span>
                      <span className="text-sm text-muted-foreground">Agent · {agent.skills.length} skills</span>
                      <span className="font-mono text-xs tracking-wide text-muted-foreground uppercase">Bundle</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        </section>
      ) : null}

      <section className="border-t border-border">
        <div className="mx-auto max-w-6xl px-5 py-14">
          <h2 className="font-serif text-4xl font-light tracking-tight">Shelves</h2>
          <ul className="mt-8 grid gap-x-16 sm:grid-cols-2">
            {catalog.categories.map((category) => (
              <li key={category.id} className="border-t border-border">
                <Link href={`/browse?category=${category.id}`} className="flex items-baseline justify-between gap-6 py-4">
                  <span>
                    <span className="block font-serif text-2xl">{category.label}</span>
                    <span className="mt-1 block text-sm text-muted-foreground">{category.blurb}</span>
                  </span>
                  <span className="font-mono text-sm tabular-nums">{category.count}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="border-t border-border">
        <div className="mx-auto max-w-6xl px-5 py-14">
          <h2 className="font-serif text-4xl font-light tracking-tight">Worth opening first</h2>
          <ul className="mt-8">
            {featured.map((skill, index) => (
              <li key={skill.name} className="border-t border-border">
                <Link href={`/skills/${skill.name}`} className="block py-7">
                  <span className="flex flex-wrap items-baseline justify-between gap-4">
                    <span className={index === 0 ? "font-serif text-4xl font-light tracking-tight" : "font-serif text-2xl"}>
                      {skill.title}
                    </span>
                    <ScoreMark score={skill.lint.score} badge={skill.lint.badge} />
                  </span>
                  <span className="mt-3 block max-w-3xl text-sm leading-relaxed text-muted-foreground">
                    {skill.description}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="border-t border-border">
        <div className="mx-auto max-w-6xl px-5 py-14">
          <div className="flex items-end justify-between gap-4">
            <h2 className="font-serif text-4xl font-light tracking-tight">Agents</h2>
            <Link href="/agents" className="text-sm text-stamp underline decoration-stamp/40 underline-offset-4">
              All agents
            </Link>
          </div>
          <ul className="mt-8 border-t border-border">
            {catalog.agents.map((agent) => (
              <li key={agent.name} className="border-b border-border py-5">
                <Link href={`/agents/${agent.name}`} className="font-serif text-2xl">
                  {agent.name}
                </Link>
                <p className="mt-2 max-w-3xl text-sm leading-relaxed text-muted-foreground">{agent.description}</p>
                <p className="mt-2 text-sm">
                  {agent.skills.map((name, index) => (
                    <span key={name}>
                      {index > 0 ? ", " : ""}
                      <Link href={`/skills/${name}`} className="underline decoration-border underline-offset-4">
                        {name}
                      </Link>
                    </span>
                  ))}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}

function AssayCard({ name }: { name: string }) {
  const skill = getSkill(name);
  if (!skill) return null;
  return (
    <Link
      href={`/skills/${skill.name}`}
      className="relative block bg-vellum px-6 pt-6 pb-28 text-vellum-ink shadow-[0_28px_50px_-28px_rgba(0,0,0,0.75)]"
    >
      <p className="font-mono text-[0.68rem] tracking-[0.16em] text-vellum-dim uppercase">
        Assay · {formatDropDate(skill.added)}
      </p>
      <p className="mt-4 font-serif text-3xl leading-none tracking-tight">{skill.name}</p>
      <p className="mt-2 text-sm text-vellum-dim">{skill.categoryLabel}</p>
      <p className="mt-8 font-serif text-7xl leading-none font-light tabular-nums">{skill.lint.score}</p>
      <dl className="mt-6 grid grid-cols-3 gap-3 border-t border-vellum-ink/15 pt-4 text-sm">
        <div>
          <dt className="text-vellum-dim">Errors</dt>
          <dd className="font-mono tabular-nums">{skill.lint.errors}</dd>
        </div>
        <div>
          <dt className="text-vellum-dim">Warnings</dt>
          <dd className="font-mono tabular-nums">{skill.lint.warnings}</dd>
        </div>
        <div>
          <dt className="text-vellum-dim">Notes</dt>
          <dd className="font-mono tabular-nums">{skill.lint.info}</dd>
        </div>
      </dl>
      <ul className="mt-5 space-y-1 font-mono text-xs text-vellum-dim">
        {skill.files.slice(0, 4).map((file) => (
          <li key={file.path} className="flex justify-between gap-3">
            <span className="truncate">{file.path}</span>
            <span className="shrink-0 tabular-nums">{formatBytes(file.bytes)}</span>
          </li>
        ))}
      </ul>
      <p className="mt-6 text-sm">
        Lint status: {skill.lint.badge}. Open the full report.
      </p>
      <span className="seal" aria-hidden="true">
        Passed
      </span>
    </Link>
  );
}
