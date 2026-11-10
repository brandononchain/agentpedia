import type { Metadata } from "next";
import { catalog } from "@/lib/catalog";

export const metadata: Metadata = {
  title: "How we lint",
  description: "The skill-lint rules Skilldex runs before an entry can ship, and how the score is calculated.",
};

export default function LintPage() {
  const { scoring, stats } = catalog;
  return (
    <div className="mx-auto max-w-6xl px-5 py-12">
      <h1 className="max-w-[16ch] font-serif text-5xl font-light tracking-tight">
        How we lint
      </h1>
      <div className="mt-6 max-w-[68ch] space-y-4 text-base leading-relaxed text-muted-foreground">
        <p>
          Agent Skills are folders with a <span className="font-mono text-sm text-foreground">SKILL.md</span> file.
          The format is an open specification, now a project of the Agentic AI Foundation under the Linux Foundation.
          The body of a skill is free Markdown. That freedom is why quality varies so widely.
        </p>
        <p>
          In{" "}
          <a className="text-stamp underline decoration-stamp/40 underline-offset-4" href={catalog.studyUrl}>
            From Anatomy to Smells
          </a>
          , Hong, Imani, and Ahmed at UC Irvine studied 238 real skills sampled from a public marketplace.
          Over 99 percent — 237 of the 238 — contained at least one skill smell. Smells introduced early rarely disappeared
          in later commits. Popularity did not clean them up.
        </p>
        <p>
          Skilldex vendors{" "}
          <span className="font-mono text-sm text-foreground">tools/skill-lint</span>, a dependency-free Python
          checker for the spec, for progressive-disclosure smells, for broken relative links, and for a small set of
          safety patterns. The catalog build runs it on every skill. An error or a warning fails the build.
          Info findings are recorded and lower the score, and the current shelf has {stats.info} of them.
        </p>
      </div>

      <section className="mt-12 max-w-3xl border border-border p-5">
        <h2 className="font-serif text-3xl font-light">The score</h2>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          A skill starts at {scoring.start}. Each error subtracts {scoring.errorPenalty}, each warning subtracts{" "}
          {scoring.warningPenalty}, and each info finding subtracts {scoring.infoPenalty}. The floor is {scoring.floor}.
          The badge reads clean when errors and warnings are both zero, noted when there are warnings but no errors,
          and blocked when any error remains. Blocked and noted entries do not ship in this catalog.
        </p>
      </section>

      <div className="mt-14 space-y-12">
        {catalog.rules.map((group) => (
          <section key={group.group}>
            <h2 className="font-serif text-3xl font-light">{group.group}</h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
                <caption className="sr-only">{group.group} rules</caption>
                <thead>
                  <tr className="border-b border-border text-muted-foreground">
                    <th scope="col" className="py-2 pr-4 font-medium">Rule</th>
                    <th scope="col" className="py-2 pr-4 font-medium">Severity</th>
                    <th scope="col" className="py-2 font-medium">What it checks</th>
                  </tr>
                </thead>
                <tbody>
                  {group.rules.map((rule) => (
                    <tr key={rule.id} className="border-b border-border align-top">
                      <th scope="row" className="py-3 pr-4 font-mono text-xs font-normal text-foreground">
                        {rule.id}
                      </th>
                      <td className="py-3 pr-4 font-mono text-xs text-muted-foreground">{rule.severity}</td>
                      <td className="py-3 text-muted-foreground">{rule.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
