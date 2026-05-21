import { stackServerApp } from "@/stack";
import { StackHandler } from "@stackframe/stack";

export async function GET(req: Request, options: { params: Promise<{ stack: string[] }> }) {
  const params = await options.params;
  return StackHandler({ app: stackServerApp, request: req, params });
}

export async function POST(req: Request, options: { params: Promise<{ stack: string[] }> }) {
  const params = await options.params;
  return StackHandler({ app: stackServerApp, request: req, params });
}
