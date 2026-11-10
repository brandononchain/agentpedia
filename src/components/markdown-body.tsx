import type { Components } from "react-markdown";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { headingId, linkCatalogTerms } from "@/lib/wiki";

function plainText(node: ReactNode): string {
  if (node == null || typeof node === "boolean") return "";
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(plainText).join("");
  if (typeof node === "object" && "props" in node) {
    return plainText((node as { props?: { children?: ReactNode } }).props?.children);
  }
  return "";
}

export function MarkdownBody({ source, selfHref }: { source: string; selfHref?: string }) {
  const seen = new Map<string, number>();
  const linked = linkCatalogTerms(source, selfHref);

  const components: Components = {
    a: ({ href, children }) => {
      const external = Boolean(href && /^https?:\/\//.test(href));
      return (
        <a href={href} {...(external ? { target: "_blank", rel: "noreferrer" } : {})}>
          {children}
        </a>
      );
    },
    h2: ({ children }) => <h2 id={headingId(plainText(children), seen)}>{children}</h2>,
    h3: ({ children }) => <h3 id={headingId(plainText(children), seen)}>{children}</h3>,
    table: ({ children }) => (
      <div className="table-scroll">
        <table>{children}</table>
      </div>
    ),
  };

  return (
    <div className="wiki-prose">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {linked}
      </ReactMarkdown>
    </div>
  );
}
