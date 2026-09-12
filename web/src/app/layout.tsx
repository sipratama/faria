import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "FARIA Control Center",
  description: "Local household agent monitoring for FARIA.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
