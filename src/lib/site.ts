/** Display name. The site reads this string. */
export const SITE_NAME = "Agentpedia";

export const SITE_TAGLINE = "The reference encyclopedia of agent skills and agents.";

/** Public origin used in badge embeds. Override with NEXT_PUBLIC_SITE_URL. */
export const SITE_ORIGIN = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://agentpedia-ten.vercel.app").replace(/\/$/, "");

export const REPO_URL = "https://github.com/brandononchain/agentpedia";
