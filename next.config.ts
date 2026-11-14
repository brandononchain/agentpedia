import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
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
