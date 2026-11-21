import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    "/api/v1/skills/[name]": ["./skills/**/*", "./data/brain-index.json", "./data/certificates.json"],
    "/api/v1/agents/[name]": ["./agents/**/*", "./data/brain-index.json", "./data/certificates.json"],
    "/mcp": ["./skills/**/*", "./agents/**/*", "./data/brain-index.json", "./data/certificates.json"],
  },
  async rewrites() {
    return [
      { source: "/.well-known/llms.txt", destination: "/llms.txt" },
      { source: "/skills/:name.md", destination: "/raw/skills/:name" },
      { source: "/agents/:name.md", destination: "/raw/agents/:name" },
    ];
  },
  async redirects() {
    return [
      { source: "/index", destination: "/az", permanent: false },
      { source: "/recent-changes", destination: "/changelog", permanent: false },
      { source: "/drops", destination: "/changelog", permanent: false },
      { source: "/shelves/:id", destination: "/category/:id", permanent: false },
    ];
  },
};

export default nextConfig;
