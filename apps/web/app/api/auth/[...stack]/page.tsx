// Implements: [F-001] — Neon Auth catch-all handler page
import { stackServerApp } from "@/stack";
import { StackHandler } from "@stackframe/stack";

export default function Handler(props: {
  params: Promise<{ stack?: string[] }>;
  searchParams: Promise<Record<string, string>>;
}) {
  return <StackHandler app={stackServerApp} {...props} fullPage />;
}
