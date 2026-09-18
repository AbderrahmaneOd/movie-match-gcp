import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "image.tmdb.org",
        port: "",
        pathname: "/**",
      },
    ],
  },
  // This option allows you to build a standalone Next.js application that can be deployed without the need for a Node.js server. 
  // It includes all necessary files and dependencies in the output directory, making it easier to deploy to various environments.
  output: "standalone", 
};

export default nextConfig;