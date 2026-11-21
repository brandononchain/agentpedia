/**
 * Query tokenizer. Must match tools/brain_text.py tokenize().
 * Cases are locked in tools/tests/brain_tokens.json.
 */

const SYNONYMS: ReadonlyArray<readonly [string, string]> = [
  ["pull requests", "pull request"],
  ["large language models", "large language model"],
  ["model context protocol", "model context protocol"],
  ["continuous integration", "continuous integration"],
  ["continuous delivery", "continuous delivery"],
  ["semantic versioning", "semantic version"],
  ["non disclosure agreement", "non disclosure agreement"],
  ["user experience", "user experience"],
  ["user interface", "user interface"],
  ["pull request", "pull request"],
  ["semantic version", "semantic version"],
  ["large language model", "large language model"],
  ["non disclosure", "non disclosure"],
  ["prs", "pull request"],
  ["llms", "large language model"],
  ["configs", "configuration"],
  ["repos", "repository"],
  ["k8s", "kubernetes"],
  ["kube", "kubernetes"],
  ["semver", "semantic version"],
  ["soc2", "soc 2"],
  ["a11y", "accessibility"],
  ["i18n", "internationalization"],
  ["nda", "non disclosure agreement"],
  ["mcp", "model context protocol"],
  ["llm", "large language model"],
  ["yml", "yaml"],
  ["auth", "authentication"],
  ["config", "configuration"],
  ["repo", "repository"],
  ["docs", "documentation"],
  ["doc", "documentation"],
  ["pr", "pull request"],
  ["js", "javascript"],
  ["ts", "typescript"],
  ["py", "python"],
  ["gh", "github"],
  ["ci", "continuous integration"],
  ["cd", "continuous delivery"],
  ["ux", "user experience"],
  ["ui", "user interface"],
];

const STOP = new Set([
  "a",
  "an",
  "the",
  "of",
  "to",
  "for",
  "and",
  "or",
  "in",
  "on",
  "with",
  "from",
  "by",
  "at",
  "as",
  "is",
  "are",
  "be",
  "this",
  "that",
  "it",
  "when",
  "how",
  "what",
  "use",
  "using",
  "used",
  "into",
  "over",
  "than",
  "then",
  "not",
  "do",
  "does",
  "their",
  "they",
  "them",
  "its",
  "if",
  "but",
  "about",
  "each",
  "per",
  "via",
  "your",
  "you",
  "we",
  "our",
  "can",
  "may",
  "should",
  "would",
  "will",
  "just",
  "also",
  "only",
  "one",
  "out",
  "up",
  "who",
  "which",
  "where",
  "why",
]);

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const SYNONYM_RES = SYNONYMS.map(
  ([alias, canonical]) => [new RegExp(`(?<![a-z0-9])${escapeRegExp(alias)}(?![a-z0-9])`, "g"), canonical] as const,
);

export function stem(word: string) {
  if (word === "kubernetes" || word === "javascript" || word === "typescript") return word;
  if (word.length < 4) return word;
  if (word.endsWith("ies") && word.length > 4) return `${word.slice(0, -3)}y`;
  if (word.endsWith("ing") && word.length > 6) {
    const trimmed = word.slice(0, -3);
    if (trimmed.length >= 4) return trimmed;
  }
  if (word.endsWith("ed") && word.length > 4) {
    const trimmed = word.slice(0, -2);
    if (trimmed.length >= 3) return trimmed;
  }
  if (/(sses|shes|ches|xes|zes)$/.test(word) && word.length > 4) return word.slice(0, -2);
  if (word.endsWith("s") && word.length > 4 && !/(ss|us|is|ous)$/.test(word)) return word.slice(0, -1);
  return word;
}

export function tokenize(text: string) {
  let spaced = text.toLowerCase().replace(/[^a-z0-9]+/g, " ").split(/\s+/).filter(Boolean).join(" ");
  for (const [pattern, canonical] of SYNONYM_RES) {
    spaced = spaced.replace(pattern, canonical);
  }
  const tokens: string[] = [];
  for (const word of spaced.split(/\s+/)) {
    if (!word || STOP.has(word)) continue;
    tokens.push(stem(word));
  }
  return tokens;
}
