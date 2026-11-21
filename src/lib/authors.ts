import { catalog } from "@/lib/catalog";

export type AuthorEntry = {
  href: string;
  title: string;
  kind: "skill" | "agent";
};

export type AuthorGroup = {
  name: string;
  url: string;
  kind: "person" | "organization";
  count: number;
  entries: AuthorEntry[];
};

export function authorGroups(): AuthorGroup[] {
  const groups = new Map<string, AuthorGroup>();

  function add(
    kind: "skill" | "agent",
    id: string,
    title: string,
    author: string,
    url: string,
    authorKind: "person" | "organization",
  ) {
    const key = url || author;
    const group = groups.get(key) ?? {
      name: author,
      url,
      kind: authorKind,
      count: 0,
      entries: [],
    };
    group.count += 1;
    group.entries.push({
      href: kind === "skill" ? `/skills/${id}` : `/agents/${id}`,
      title,
      kind,
    });
    groups.set(key, group);
  }

  for (const skill of catalog.skills) {
    add("skill", skill.name, skill.title, skill.author, skill.authorUrl, skill.authorKind);
  }
  for (const agent of catalog.agents) {
    add("agent", agent.name, agent.name, agent.author, agent.authorUrl, agent.authorKind);
  }

  return [...groups.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}
