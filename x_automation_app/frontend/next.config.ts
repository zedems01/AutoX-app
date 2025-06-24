import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "x-automation-agent.s3.amazonaws.com",
      }
    ]
  },
  output: "standalone",
};

export default nextConfig;
