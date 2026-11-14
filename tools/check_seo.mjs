import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

const base = process.env.SEO_BASE ?? "http://127.0.0.1:43123";
const origin = "https://agentpedia.sh";
const errors = [];

function fail(message) {
  errors.push(message);
}

function skillNames() {
  const names = [];
  for (const category of readdirSync("skills")) {
    const dir = join("skills", category);
    let children = [];
    try {
      children = readdirSync(dir);
    } catch {
      continue;
    }
    for (const name of children) {
      if (existsSync(join(dir, name, "SKILL.md"))) names.push(name);
    }
  }
  return names.sort();
}

function agentNames() {
  return readdirSync("agents")
    .filter((name) => existsSync(join("agents", name, "AGENT.md")))
    .sort();
}

function decode(value) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#x27;|&#39;/g, "'");
}

function tags(html) {
  const metas = [];
  for (const tag of html.matchAll(/<meta\b[^>]*>/gi)) {
    const attrs = {};
    for (const attr of tag[0].matchAll(/([\w:-]+)="([^"]*)"/g)) attrs[attr[1].toLowerCase()] = decode(attr[2]);
    metas.push(attrs);
  }
  const links = [];
  for (const tag of html.matchAll(/<link\b[^>]*>/gi)) {
    const attrs = {};
    for (const attr of tag[0].matchAll(/([\w:-]+)="([^"]*)"/g)) attrs[attr[1].toLowerCase()] = decode(attr[2]);
    links.push(attrs);
  }
  const title = decode((html.match(/<title>([^<]*)<\/title>/i) ?? ["", ""])[1]);
  const h1 = [...html.matchAll(/<h1\b/gi)].length;
  const jsonLd = [];
  for (const block of html.matchAll(/<script type="application\/ld\+json">([^<]*)<\/script>/gi)) {
    jsonLd.push(block[1]);
  }
  return { metas, links, title, h1, jsonLd };
}

function metaContent(metas, key, attr) {
  const found = metas.find((item) => item[attr] === key);
  return found?.content ?? "";
}

async function text(path) {
  const response = await fetch(base + path);
  const body = await response.text();
  return { response, body };
}

async function waitForServer() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(base + "/");
      if (response.ok) return;
    } catch {
      // The server is still binding the port.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`no server at ${base}`);
}

await waitForServer();

const skills = skillNames();
const agents = agentNames();
if (!skills.length || !agents.length) fail("no skills or agents on disk");

const robots = await text("/robots.txt");
if (robots.response.status !== 200) fail(`robots.txt ${robots.response.status}`);
for (const agent of ["GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "Applebot-Extended", "Bingbot"]) {
  if (!robots.body.includes(agent)) fail(`robots.txt missing ${agent}`);
}
if (!robots.body.includes(`${origin}/sitemap.xml`)) fail("robots.txt missing sitemap link");

const sitemap = await text("/sitemap.xml");
if (sitemap.response.status !== 200) fail(`sitemap.xml ${sitemap.response.status}`);
const locs = [...sitemap.body.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);
const lastmods = [...sitemap.body.matchAll(/<lastmod>/g)].length;
if (lastmods < locs.length) fail(`sitemap lastmod ${lastmods} of ${locs.length}`);
for (const name of skills) {
  for (const path of [`/skills/${name}`, `/skills/${name}.md`]) {
    if (!locs.includes(origin + path)) fail(`sitemap missing ${path}`);
  }
}
for (const name of agents) {
  for (const path of [`/agents/${name}`, `/agents/${name}.md`]) {
    if (!locs.includes(origin + path)) fail(`sitemap missing ${path}`);
  }
}

const llms = await text("/llms.txt");
if (llms.response.status !== 200) fail(`llms.txt ${llms.response.status}`);
if (!llms.body.startsWith("# Agentpedia")) fail("llms.txt missing H1");
if (!llms.body.includes("\n> ")) fail("llms.txt missing summary blockquote");
for (const name of skills) {
  if (!llms.body.includes(`/skills/${name}`)) fail(`llms.txt missing skill ${name}`);
}
for (const name of agents) {
  if (!llms.body.includes(`/agents/${name}`)) fail(`llms.txt missing agent ${name}`);
}

const full = await text("/llms-full.txt");
if (full.response.status !== 200) fail(`llms-full.txt ${full.response.status}`);
for (const name of skills) {
  if (!full.body.includes(`/${name}/SKILL.md`)) fail(`llms-full.txt missing ${name}`);
}
for (const name of agents) {
  if (!full.body.includes(`/${name}/AGENT.md`)) fail(`llms-full.txt missing ${name}`);
}

const catalog = await text("/catalog.json");
if (catalog.response.status !== 200) fail(`catalog.json ${catalog.response.status}`);
const catalogJson = JSON.parse(catalog.body);
if (catalogJson.skills.length !== skills.length) fail(`catalog skills ${catalogJson.skills.length} != ${skills.length}`);
if (catalogJson.agents.length !== agents.length) fail(`catalog agents ${catalogJson.agents.length} != ${agents.length}`);

const og = await fetch(base + "/og.png");
if (og.status !== 200 || !og.headers.get("content-type")?.includes("image/png")) {
  fail(`og.png ${og.status} ${og.headers.get("content-type")}`);
}
const entryOg = await fetch(`${base}/skills/${skills[0]}/opengraph-image`);
if (entryOg.status !== 200 || !entryOg.headers.get("content-type")?.includes("image")) {
  fail(`entry og ${entryOg.status} ${entryOg.headers.get("content-type")}`);
}

const sampleMd = await text(`/skills/${skills[0]}.md`);
if (sampleMd.response.status !== 200 || !sampleMd.body.includes("name:")) fail(`raw markdown ${sampleMd.response.status}`);
const feed = await text("/feed.xml");
if (feed.response.status !== 200 || !feed.body.includes("<rss")) fail("feed.xml");
const atom = await text("/atom.xml");
if (atom.response.status !== 200 || !atom.body.includes("<feed")) fail("atom.xml");

const pages = locs
  .map((url) => url.slice(origin.length) || "/")
  .filter((path) => !/\.(xml|txt|json|md|png)$/.test(path));

async function checkPage(path) {
  const { response, body } = await text(path);
  if (!response.ok) {
    fail(`${path} ${response.status}`);
    return;
  }
  const parsed = tags(body);
  if (!parsed.title) fail(`${path} missing title`);
  const description = metaContent(parsed.metas, "description", "name");
  const canonical = parsed.links.find((link) => link.rel === "canonical")?.href ?? "";
  const ogTitle = metaContent(parsed.metas, "og:title", "property");
  const ogDescription = metaContent(parsed.metas, "og:description", "property");
  const ogImage = metaContent(parsed.metas, "og:image", "property");
  const card = metaContent(parsed.metas, "twitter:card", "name");
  const robotsMeta = metaContent(parsed.metas, "robots", "name");
  const theme = parsed.metas.some((item) => item.name === "theme-color");
  const lang = parsed.links.some((link) => link.rel === "alternate" && link.hreflang === "en");
  if (!description) fail(`${path} missing description`);
  if (!canonical.startsWith(`${origin}/`) && canonical !== origin && canonical !== `${origin}/`) {
    fail(`${path} canonical ${canonical}`);
  }
  if (!ogTitle || !ogDescription || !ogImage) fail(`${path} missing og`);
  if (card !== "summary_large_image") fail(`${path} twitter ${card}`);
  if (!robotsMeta) fail(`${path} missing robots`);
  if (!theme) fail(`${path} missing theme-color`);
  if (!lang) fail(`${path} missing hreflang`);
  if (parsed.h1 !== 1) fail(`${path} h1 count ${parsed.h1}`);
  if (!parsed.jsonLd.length) fail(`${path} missing json-ld`);
  for (const block of parsed.jsonLd) {
    try {
      JSON.parse(block);
    } catch {
      fail(`${path} invalid json-ld`);
    }
  }
  if (path === "/") {
    if (parsed.title !== "Agentpedia — The open encyclopedia of agents and skills") fail(`home title ${parsed.title}`);
    if (description.length < 150 || description.length > 165) fail(`home description length ${description.length}: ${description}`);
    const graph = parsed.jsonLd.map((block) => JSON.parse(block)).flat();
    const blob = JSON.stringify(graph);
    for (const type of ["WebSite", "SearchAction", "Organization", "Dataset", "FAQPage"]) {
      if (!blob.includes(type)) fail(`home json-ld missing ${type}`);
    }
  }
}

const queue = pages.slice();
const workers = Array.from({ length: 8 }, async () => {
  while (queue.length) {
    const path = queue.shift();
    if (path) await checkPage(path);
  }
});
await Promise.all(workers);

if (errors.length) {
  console.error(errors.slice(0, 40).join("\n"));
  console.error(`${errors.length} SEO check(s) failed across ${pages.length} pages`);
  process.exit(1);
}
console.log(`SEO ok: ${pages.length} pages, ${skills.length} skills, ${agents.length} agents`);
