import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { catalog } from "@/lib/catalog";
import { auditStatusLabel } from "@/lib/audit";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/security", {
  title: "Security",
  description: `Static security audit grades for every skill and agent in ${SITE_NAME}.`,
  keywords: ["security audit", "agent skills", SITE_NAME],
});

type Row = {
  key: string;
  title: string;
  href: string;
  shelf: string;
  shelfId: string;
  grade: string;
  status: string;
  label: string;
  score: number;
};

export default async function SecurityPage({
  searchParams,
}: {
  searchParams: Promise<{ shelf?: string; grade?: string; status?: string }>;
}) {
  const params = await searchParams;
  const shelf = params.shelf ?? "";
  const grade = params.grade ?? "";
  const status = params.status ?? "";
  const rows: Row[] = [
    ...catalog.skills.flatMap((skill) =>
      skill.audit
        ? [
            {
              key: `skill-${skill.name}`,
              title: skill.title,
              href: `/skills/${skill.name}#security-report`,
              shelf: skill.categoryLabel,
              shelfId: skill.category,
              grade: skill.audit.grade,
              status: skill.audit.status,
              label: auditStatusLabel(skill.audit),
              score: skill.audit.score,
            },
          ]
        : [],
    ),
    ...catalog.agents.flatMap((agent) =>
      agent.audit
        ? [
            {
              key: `agent-${agent.name}`,
              title: agent.name,
              href: `/agents/${agent.name}#security-report`,
              shelf: agent.categoryLabel,
              shelfId: agent.category,
              grade: agent.audit.grade,
              status: agent.audit.status,
              label: auditStatusLabel(agent.audit),
              score: agent.audit.score,
            },
          ]
        : [],
    ),
  ];
  const filtered = rows.filter((row) => {
    if (shelf && row.shelfId !== shelf) return false;
    if (grade && row.grade !== grade) return false;
    if (status && row.status !== status) return false;
    return true;
  });
  const stats = catalog.audit?.stats;

  return (
    <ArticleFrame
      title="Security"
      lede="Every published skill and agent has a static audit. The grade and the status come from that run. This page does not invent a score."
      path="/security"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Security" },
      ]}
    >
      <div className="wiki-prose">
        <p>
          {stats
            ? `${stats.entries} entries. ${stats.passed} passed, ${stats.warning} warning, ${stats.onHold} on hold. Grades A ${stats.grades.A ?? 0}, B ${stats.grades.B ?? 0}, C ${stats.grades.C ?? 0}, D ${stats.grades.D ?? 0}, F ${stats.grades.F ?? 0}.`
            : "This catalog build has no audit summary yet."}{" "}
          <Link href="/security/methodology">How the audit works</Link>.
        </p>
        <form className="audit-filters" method="get" action="/security">
          <label>
            Shelf
            <select name="shelf" defaultValue={shelf}>
              <option value="">All</option>
              {catalog.categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Grade
            <select name="grade" defaultValue={grade}>
              <option value="">All</option>
              {["A", "B", "C", "D", "F"].map((letter) => (
                <option key={letter} value={letter}>
                  {letter}
                </option>
              ))}
            </select>
          </label>
          <label>
            Status
            <select name="status" defaultValue={status}>
              <option value="">All</option>
              <option value="passed">Passed</option>
              <option value="warning">Warning</option>
              <option value="on-hold">On hold</option>
            </select>
          </label>
          <button type="submit">Filter</button>
        </form>
        {filtered.length === 0 ? (
          <p>No entries match these filters.</p>
        ) : (
          <div className="table-scroll" tabIndex={0}>
            <table>
              <thead>
                <tr>
                  <th>Entry</th>
                  <th>Shelf</th>
                  <th>Grade</th>
                  <th>Score</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((row) => (
                  <tr key={row.key}>
                    <td>
                      <Link href={row.href}>{row.title}</Link>
                    </td>
                    <td>{row.shelf}</td>
                    <td>{row.grade}</td>
                    <td>{row.score}</td>
                    <td>{row.label}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </ArticleFrame>
  );
}
