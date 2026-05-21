import { stackServerApp } from "@/stack";
import { StackHandler } from "@stackframe/stack";

export function GET(req: Request, options: { params: { stack: string[] } }) {
  return StackHandler({ app: stackServerApp, request: req, params: options.params });
}

export function POST(req: Request, options: { params: { stack: string[] } }) {
  return StackHandler({ app: stackServerApp, request: req, params: options.params });
}
