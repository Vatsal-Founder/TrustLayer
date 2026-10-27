import type { Metadata } from "next";
import { Suspense } from "react";

import NavLink from "@/components/NavLink";

import "./globals.css";

export const metadata: Metadata = {
  title: "Scorecard Trust Layer",
  description:
    "A demo of scoring, consistency, calibration, and drift checks for AI-scored support conversations.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <span className="nav-title">Scorecard Trust Layer</span>
          <Suspense fallback={null}>
            <NavLink href="/">Score a ticket</NavLink>
            <NavLink href="/golden-set">Golden set</NavLink>
            <NavLink href="/reliability">Scorer reliability</NavLink>
            <NavLink href="/dashboard">Dashboard</NavLink>
          </Suspense>
        </nav>
        <main className="main">{children}</main>
      </body>
    </html>
  );
}
