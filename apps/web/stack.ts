import "server-only";
import { StackServerApp } from "@stackframe/stack";

export const stackServerApp = new StackServerApp({
  tokenStore: "nextjs-cookie",
  // Point to your Neon Auth endpoint (Auth URL from the Project Info page)
  baseUrl: process.env.NEXT_PUBLIC_STACK_BASE_URL,
  urls: {
    signIn: "/login",
    signUp: "/register",
    afterSignIn: "/dashboard",
    afterSignUp: "/dashboard",
    afterSignOut: "/",
  },
});
