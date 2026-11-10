import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const components: Components = {
  a: ({ href, children }) => {
    const external = Boolean(href && /^https?:\/\//.test(href));
    return (
      <a
        href={href}
        {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
      >
        {children}
      </a>
    );
  },
};

export function MarkdownBody({ source }: { source: string }) {
  return (
    <div className="skill-prose">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {source}
      </ReactMarkdown>
    </div>
  );
}
