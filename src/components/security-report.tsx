import type { AuditView } from "@/lib/catalog";
import { auditStatusLabel } from "@/lib/audit";

function Gauge({ score, grade }: { score: number; grade: string }) {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - Math.max(0, Math.min(100, score)) / 100);
  return (
    <svg className="audit-gauge" viewBox="0 0 96 96" width="96" height="96" role="img" aria-label={`Audit score ${score}, grade ${grade}`}>
      <circle cx="48" cy="48" r={radius} fill="none" stroke="var(--rule)" strokeWidth="8" />
      <circle
        cx="48"
        cy="48"
        r={radius}
        fill="none"
        stroke="var(--accent-ink)"
        strokeWidth="8"
        strokeDasharray={`${circumference} ${circumference}`}
        strokeDashoffset={offset}
        transform="rotate(-90 48 48)"
      />
      <text x="48" y="46" textAnchor="middle" fontSize="18" fill="var(--ink)">
        {grade}
      </text>
      <text x="48" y="64" textAnchor="middle" fontSize="11" fill="var(--ink)">
        {score}
      </text>
    </svg>
  );
}

export function SecurityReport({ audit }: { audit: AuditView | null | undefined }) {
  if (!audit) {
    return <p>This catalog build has no static audit for the entry.</p>;
  }
  const counts = audit.counts;
  return (
    <div className="audit-report">
      <div className="audit-head">
        <Gauge score={audit.score} grade={audit.grade} />
        <div>
          <p>
            {auditStatusLabel(audit)}. Grade {audit.grade}. Score {audit.score} of 100.
          </p>
          <p className="quiet">{audit.summary}</p>
        </div>
      </div>
      <p>
        {counts.critical} critical, {counts.high} high, {counts.medium} medium, {counts.low} low, {counts.info} info.
      </p>
      {audit.findings.length === 0 ? (
        <p>No findings.</p>
      ) : (
        <div className="table-scroll" tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th>Rule</th>
                <th>Severity</th>
                <th>Where</th>
                <th>Evidence</th>
                <th>What to change</th>
              </tr>
            </thead>
            <tbody>
              {audit.findings.map((finding) => (
                <tr key={`${finding.ruleId}-${finding.path}-${finding.line}`}>
                  <td>{finding.ruleId}</td>
                  <td>{finding.severity}</td>
                  <td>
                    {finding.path}:{finding.line}
                  </td>
                  <td className="audit-evidence">{finding.evidence}</td>
                  <td className="audit-evidence">{finding.remediation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <dl className="audit-meta">
        <dt>Audited commit</dt>
        <dd>{audit.auditedCommit ? <code>{audit.auditedCommit.slice(0, 12)}</code> : "Not recorded"}</dd>
        <dt>Content digest</dt>
        <dd>
          <code>{audit.contentDigest}</code>
        </dd>
        <dt>Lock hash</dt>
        <dd>
          <code>
            {audit.lockHashAlg} {audit.lockHash.slice(0, 16)}
          </code>
        </dd>
        <dt>Audited</dt>
        <dd>
          <time dateTime={audit.auditedAt}>{audit.auditedAt}</time>
        </dd>
        <dt>Expires</dt>
        <dd>
          <time dateTime={audit.expiresAt}>{audit.expiresAt}</time>
        </dd>
        <dt>Ruleset</dt>
        <dd>
          {audit.rulesetVersion}, {audit.auditor}
        </dd>
        <dt>CVE lookup</dt>
        <dd>{audit.cveLookup}</dd>
      </dl>
      <h3>Stages</h3>
      <ul className="entry-list">
        {audit.stages.map((stage) => (
          <li key={stage.id}>
            <span>
              Phase {stage.phase}. {stage.title}. {stage.status}.
            </span>
            <span className="quiet"> {stage.detail}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
