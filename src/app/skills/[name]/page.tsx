import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { InstallPanel } from "@/components/install-panel";
import { MarkdownBody } from "@/components/markdown-body";
import { ScoreMark } from "@/components/score-mark";
import { catalog, getSkill } from "@/lib/catalog";
import { formatBytes, formatDropDate, stripTitle } from "@/lib/format";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.skills.map((skill) => ({ name: skill.name }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<Params>;
}): Promise<Metadata> {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) return { title: "Skill" };
  return { title: skill.title, description: skill.description };
}

export default async function SkillPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) notFound();

  return (
    <article className="mx-auto max-w-6xl px-5 py-12">
      <p className="text-sm text-muted-foreground">
        <Link href="/browse" className="underline decoration-border underline-offset-4">
          Browse
        </Link>
        <span aria-hidden="true"> / </span>
        <Link
          href={`/browse?category=${skill.category}`}
          className="underline decoration-border underline-offset-4"
        >
          {skill.categoryLabel}
        </Link>
      </p>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
        <h1 className="font-serif text-5xl font-light tracking-tight">{skill.title}</h1>
        <ScoreMark score={skill.lint.score} badge={skill.lint.badge} />
      </div>
      <p className="mt-4 max-w-3xl text-lg leading-relaxed text-muted-foreground">{skill.description}</p>
      <p className="mt-4 font-mono text-xs text-muted-foreground">
        {skill.sourcePath} · added {formatDropDate(skill.added)} · {skill.license}
      </p>
      <ul className="mt-3 flex flex-wrap gap-2">
        {skill.tags.map((tag) => (
          <li key={tag}>
            <Link
              href={`/browse?tag=${encodeURIComponent(tag)}`}
              className="inline-block border border-border px-2 py-1 font-mono text-xs text-muted-foreground hover:text-foreground"
            >
              {tag}
            </Link>
          </li>
        ))}
      </ul>

      <div className="mt-10 grid gap-12 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
        <div className="order-2 lg:order-1">
          <MarkdownBody source={stripTitle(skill.body)} />
        </div>
        <aside className="order-1 space-y-10 lg:order-2">
          <section>
            <h2 className="font-serif text-2xl font-light">Install</h2>
            <div className="mt-4">
              <InstallPanel install={skill.install} />
            </div>
          </section>
          <section>
            <h2 className="font-serif text-2xl font-light">Lint report</h2>
            <p className="mt-3 text-sm text-muted-foreground">
              Score {skill.lint.score}. {skill.lint.errors} errors, {skill.lint.warnings} warnings, {skill.lint.info} notes.
            </p>
            {skill.lint.findings.length === 0 ? (
              <p className="mt-3 text-sm">
                Nothing to fix. skill-lint reported no errors, warnings, or notes.
              </p>
            ) : (
              <ul className="mt-4 space-y-4">
                {skill.lint.findings.map((finding) => (
                  <li key={`${finding.ruleId}-${finding.line}`} className="border-t border-border pt-3">
                    <p className="font-mono text-xs text-stamp">
                      {finding.severity} · {finding.ruleId}
                      {finding.line ? `:${finding.line}` : ""}
                    </p>
                    <p className="mt-1 text-sm">{finding.message}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{finding.hint}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section>
            <h2 className="font-serif text-2xl font-light">Files</h2>
            <ul className="mt-3">
              {skill.files.map((file) => (
                <li key={file.path} className="flex items-baseline justify-between gap-3 border-t border-border py-2 font-mono text-xs">
                  <a href={file.url} className="truncate underline decoration-border underline-offset-4">
                    {file.path}
                  </a>
                  <span className="shrink-0 text-muted-foreground tabular-nums">{formatBytes(file.bytes)}</span>
                </li>
              ))}
            </ul>
            <p className="mt-4 flex flex-wrap gap-4 text-sm">
              <a href={skill.rawUrl} className="text-stamp underline decoration-stamp/40 underline-offset-4">
                Raw SKILL.md
              </a>
              <a href={skill.zipUrl} className="text-stamp underline decoration-stamp/40 underline-offset-4">
                Download zip
              </a>
            </p>
          </section>
          {skill.compatibility ? (
            <section>
              <h2 className="font-serif text-2xl font-light">Compatibility</h2>
              <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{skill.compatibility}</p>
            </section>
          ) : null}
        </aside>
      </div>
    </article>
  );
}
