import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AEGIS-9 Trading Dashboard",
  description: "Institutional Microstructure & Order Flow Console",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="mono">{children}</body>
    </html>
  );
}