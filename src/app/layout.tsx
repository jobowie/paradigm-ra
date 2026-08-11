import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Paradigm Ra | Software & Accounting Solutions",
  description:
    "Paradigm Ra builds modern software, accounting systems, automation, and connected business solutions.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
