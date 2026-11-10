import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
