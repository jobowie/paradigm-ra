import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },

    sitemap:
      "https://paradigmra.tech/sitemap.xml",

    host:
      "https://paradigmra.tech",
  };
}