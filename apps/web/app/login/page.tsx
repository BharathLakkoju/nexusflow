"use client";
import { AuthView } from "@neondatabase/auth-ui";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-slate-950 to-slate-900">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome back</h1>
          <p className="text-white/50">Sign in to NexusFlow AI</p>
        </div>
        <AuthView pathname="sign-in" />
      </div>
    </div>
  );
}
