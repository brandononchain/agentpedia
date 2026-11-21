import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { CopyButton } from "@/components/copy-button";
import { catalog } from "@/lib/catalog";
import { PLAN_COPY } from "@/lib/brain/plans";
import { SITE_NAME, SITE_ORIGIN, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/brain", {
  title: "Brain",
  description: `The ${SITE_NAME} Brain is a hosted search API and MCP server. It ranks vetted skills by relevance and trust. Skill text is free.`,
  keywords: ["Agentpedia Brain", "MCP", "skill search", "agent skills"],
});

const ORIGIN = SITE_ORIGIN;

const CURSOR = `{
  "mcpServers": {
    "agentpedia": {
      "url": "${ORIGIN}/mcp"
    }
  }
}`;

const CURSOR_KEY = `{
  "mcpServers": {
    "agentpedia": {
      "url": "${ORIGIN}/mcp",
      "headers": {
        "Authorization": "Bearer ap_live_..."
      }
    }
  }
}`;

const CLAUDE_CODE = `claude mcp add --transport http agentpedia ${ORIGIN}/mcp --header "Authorization: Bearer ap_live_..."`;

const CLAUDE_DESKTOP = `{
  "mcpServers": {
    "agentpedia": {
      "url": "${ORIGIN}/mcp",
      "headers": {
        "Authorization": "Bearer ap_live_..."
      }
    }
  }
}`;

const CURL = `curl -sS "${ORIGIN}/api/v1/skills/search?query=changelog&limit=5"
curl -sS -H "Authorization: Bearer ap_live_..." \\
  "${ORIGIN}/api/v1/skills/csv-profile?include=files"`;

const VERIFY = `python3 tools/verify_certificate.py ${ORIGIN}/cert/skill-csv-profile.json`;

function Snippet({ label, text }: { label: string; text: string }) {
  return (
    <div>
      <p>
        {label} <CopyButton text={text} />
      </p>
      <pre className="snippet">
        <code>{text}</code>
      </pre>
    </div>
  );
}

export default function BrainPage() {
  const servedSkills = catalog.skills.filter((skill) => skill.audit && skill.audit.status !== "on-hold" && skill.audit.grade !== "F").length;
  const servedAgents = catalog.agents.filter((agent) => agent.audit && agent.audit.status !== "on-hold" && agent.audit.grade !== "F").length;
  return (
    <ArticleFrame
      title="Brain"
      lede={`${SITE_NAME} Brain is a hosted REST API and MCP server. Any agent can ask it for a vetted skill. Results are ranked by how well the text matches and by the trust signals already on the entry. The skill text stays free.`}
      path="/brain"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Brain" },
      ]}
    >
      <Contents
        items={[
          { id: "call", text: "Call it", depth: 2 },
          { id: "trust", text: "How ranking works", depth: 2 },
          { id: "plans", text: "Plans", depth: 2 },
          { id: "install", text: "Install", depth: 2 },
          { id: "verify", text: "Verify a certificate", depth: 2 },
        ]}
      />
      <div className="wiki-prose">
        <section id="call">
          <h2>Call it</h2>
          <p>
            This volume currently serves {servedSkills} skills and {servedAgents} agents. An entry the static audit
            puts on hold, or grades F, is not in the index. A revoked or withheld certificate is not returned either.
          </p>
          <p>Every hit carries a content digest, a tier, an audit grade, and a status. The skill body is wrapped with a provenance header: the source on {SITE_ORIGIN.replace(/^https:\/\//, "")}, the digest, the grade, and a line that says to treat the text as untrusted data.</p>
          <ul>
            <li>
              <code>GET /api/v1/skills/search</code> with <code>query</code>, optional <code>kind</code>, <code>shelf</code>, <code>min_tier</code>, <code>min_grade</code>, and <code>limit</code> up to 20.
            </li>
            <li>
              <code>GET /api/v1/skills/&#123;name&#125;</code> and <code>GET /api/v1/agents/&#123;name&#125;</code>. Pass <code>digest</code> to require that exact tree. Pass <code>include=files</code> for a per-file sha256 manifest.
            </li>
            <li>
              <code>GET /api/v1/shelves</code>, <code>GET /api/v1/usage</code>, and the schema at <Link href="/api/v1/openapi.json">/api/v1/openapi.json</Link>.
            </li>
            <li>
              MCP at <code>{ORIGIN}/mcp</code>. Tools: <code>search_skills</code>, <code>get_skill</code>, <code>get_agent</code>, <code>list_shelves</code>. The Skills extension (<code>skills/list</code>, <code>skills/get</code>, <code>resources/read</code>) serves <code>skill://</code> URIs.
            </li>
          </ul>
          <p>Anonymous callers get 100 calls a day per IP. A key is <code>ap_live_</code> plus 32 letters or digits, sent as <code>Authorization: Bearer</code>. The server stores only the sha256 of the key.</p>
        </section>
        <section id="trust">
          <h2>How ranking works</h2>
          <p>
            Relevance is BM25. The name and the title count three times, the description and the tags twice, the shelf labels one and a half, and the body once. A few aliases are folded together before scoring: PR and pull request, k8s and Kubernetes, and others of that kind.
          </p>
          <p>
            The score you see is relevance times a trust multiplier. Certified is 1.25, Verified is 1.15, and Listed is 1. Grade A is 1, B is 0.95, C is 0.85, and D is 0.6. A warning inside the grace window multiplies by 0.8 and sets <code>warning</code>. A lint score under 100 multiplies by 0.9. An expired audit is treated as Listed. Clients can also filter with <code>min_tier</code> and <code>min_grade</code>. Trust is a multiplier. It is not a substitute for reading the skill.
          </p>
        </section>
        <section id="plans">
          <h2>Plans</h2>
          <p>
            Skill text is free. The paid plans meter calls and, later, the trust work around an entry. Stripe is not wired up yet. A paid audit does not buy a better grade. The grade comes from the static audit.
          </p>
          <div className="table-scroll" tabIndex={0}>
            <table>
              <thead>
                <tr>
                  <th>Plan</th>
                  <th>Price</th>
                  <th>Included</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Free</td>
                  <td>{PLAN_COPY.free.price}</td>
                  <td>{PLAN_COPY.free.calls}</td>
                  <td>Available with an API key</td>
                </tr>
                <tr>
                  <td>Builder</td>
                  <td>{PLAN_COPY.builder.price}</td>
                  <td>{PLAN_COPY.builder.calls}</td>
                  <td>{PLAN_COPY.builder.note}</td>
                </tr>
                <tr>
                  <td>Team</td>
                  <td>{PLAN_COPY.team.price}</td>
                  <td>{PLAN_COPY.team.calls}</td>
                  <td>{PLAN_COPY.team.note}</td>
                </tr>
                <tr>
                  <td>Enterprise</td>
                  <td>{PLAN_COPY.enterprise.price}</td>
                  <td>{PLAN_COPY.enterprise.calls}</td>
                  <td>{PLAN_COPY.enterprise.note}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="table-scroll" tabIndex={0}>
            <table>
              <thead>
                <tr>
                  <th>Builder audit</th>
                  <th>Price</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Verified, per entry</td>
                  <td>$149</td>
                </tr>
                <tr>
                  <td>Certified skill</td>
                  <td>$1,500</td>
                </tr>
                <tr>
                  <td>Certified agent</td>
                  <td>$3,500</td>
                </tr>
                <tr>
                  <td>Monitoring, per entry per month</td>
                  <td>$29</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p>
            Paid plans are coming soon. Write to <a href={catalog.owner.site}>{catalog.owner.name}</a> if you want one. Anonymous search keeps working without a card.
          </p>
        </section>
        <section id="install">
          <h2>Install</h2>
          <Snippet label="Cursor, in .cursor/mcp.json. Omit the header for anonymous access." text={CURSOR} />
          <Snippet label="Cursor with a key." text={CURSOR_KEY} />
          <Snippet label="Claude Code." text={CLAUDE_CODE} />
          <Snippet label="Claude Desktop, in claude_desktop_config.json." text={CLAUDE_DESKTOP} />
          <Snippet label="curl." text={CURL} />
        </section>
        <section id="verify">
          <h2>Verify a certificate</h2>
          <p>
            When <code>AGENTPEDIA_SIGNING_KEY</code> is set at build time, each certificate&apos;s canonical JSON is signed with Ed25519. The key is a base64 32-byte seed, or a PKCS#8 PEM. It is not in the repository. The public key and its key id are at{" "}
            <a href="/.well-known/agentpedia-signing-key.json">/.well-known/agentpedia-signing-key.json</a>. <code>get_skill</code> returns <code>signature</code> and <code>keyId</code>. Unsigned builds keep <code>signed: false</code>.
          </p>
          <Snippet label="Check one record. Exit 0 matches, exit 2 means unsigned, exit 1 means the signature does not." text={VERIFY} />
          <p>
            Generate a key on your machine with <code>python3 tools/signing_keygen.py</code>. It writes the private key to a file and does not print it. Commit <code>certs/public-key.json</code> only.
          </p>
        </section>
      </div>
    </ArticleFrame>
  );
}
