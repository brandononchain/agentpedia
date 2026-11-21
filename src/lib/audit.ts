import type { AuditView } from "@/lib/catalog";

export function auditStatusLabel(audit: AuditView) {
  if (audit.status === "on-hold") return "On hold";
  if (audit.status === "warning") {
    const days = audit.graceDaysLeft ?? 0;
    const unit = days === 1 ? "day" : "days";
    return `Warning, ${days} ${unit} left`;
  }
  return "Passed";
}

export function auditMark(audit: AuditView | null | undefined) {
  if (!audit) return "";
  if (audit.status === "on-hold") return `on hold · audit ${audit.grade}`;
  if (audit.status === "warning") return `warning · audit ${audit.grade}`;
  return `audit ${audit.grade}`;
}
