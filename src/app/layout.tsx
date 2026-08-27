import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(
    "https://paradigmra.tech",
  ),

  title:
    "Paradigm Ra | Software, Systems & Business Solutions",

  description:
    "Paradigm Ra helps businesses remove operational friction through custom software, systems integration, automation, digital solutions, and financial workflows.",

  alternates: {
    canonical: "/",
  },

  openGraph: {
    title:
      "Paradigm Ra | Software, Systems & Business Solutions",

    description:
      "Software, systems, automation, integrations, digital solutions, and financial workflows designed around how your business actually operates.",

    url: "/",
    siteName: "Paradigm Ra",
    type: "website",

    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Paradigm Ra — Software, Systems & Business Solutions",
      },
    ],
  },

  twitter: {
    card: "summary_large_image",

    title:
      "Paradigm Ra | Software, Systems & Business Solutions",

    description:
      "Software, systems, automation, integrations, digital solutions, and financial workflows designed around how your business actually operates.",

    images: [
      "/og-image.jpg",
    ],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}