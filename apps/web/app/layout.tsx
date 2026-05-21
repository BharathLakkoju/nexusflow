import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { StackProvider, StackTheme } from "@stackframe/stack";
import { stackServerApp } from "@/stack";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "NexusFlow AI — AI Agent Workflow Platform",
  description:
    "Build, deploy, and monitor multi-agent AI workflows with a visual drag-and-drop builder.",
  openGraph: {
    title: "NexusFlow AI",
    description: "AI Agent Workflow Platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <StackProvider app={stackServerApp}>
          <StackTheme>{children}</StackTheme>
        </StackProvider>
      </body>
    </html>
  );
}
