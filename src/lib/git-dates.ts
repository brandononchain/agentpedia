import { execFileSync } from "node:child_process";

let dates: Map<string, string> | null = null;

function load(): Map<string, string> {
  if (dates) return dates;
  dates = new Map();
  try {
    const output = execFileSync("git", ["log", "--pretty=format:%cI", "--name-only"], {
      cwd: process.cwd(),
      encoding: "utf8",
      maxBuffer: 32 * 1024 * 1024,
    });
    let current = "";
    for (const line of output.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      if (/^\d{4}-\d{2}-\d{2}T/.test(trimmed)) {
        current = trimmed;
        continue;
      }
      if (current && !dates.has(trimmed)) dates.set(trimmed, current);
    }
  } catch {
    dates = new Map();
  }
  return dates;
}

/** Newest commit time touching `path` or a file inside it. */
export function commitDate(path: string): Date | undefined {
  const map = load();
  const prefix = path.endsWith("/") ? path : `${path}/`;
  let best = map.get(path) ?? "";
  if (!path.includes(".")) {
    for (const [file, iso] of map) {
      if (file.startsWith(prefix) && iso > best) best = iso;
    }
  }
  return best ? new Date(best) : undefined;
}

export function latestDate(paths: string[], fallback: string): Date {
  let best = 0;
  for (const path of paths) {
    const found = commitDate(path);
    if (found && found.getTime() > best) best = found.getTime();
  }
  if (best) return new Date(best);
  const parsed = new Date(fallback);
  return Number.isNaN(parsed.getTime()) ? new Date() : parsed;
}
