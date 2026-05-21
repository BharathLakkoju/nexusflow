"use client";

import { AuthView } from "@neondatabase/auth-ui";
import Link from "next/link";
import { motion } from "framer-motion";
import { CheckCircle } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-[100dvh] bg-brown-50 grid grid-cols-1 lg:grid-cols-2">
      {/* Left — branding panel */}
      <motion.div
        initial={{ opacity: 0, x: -24 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="hidden lg:flex flex-col justify-between bg-brown-800 p-12 relative overflow-hidden"
      >
        {/* Background texture */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-brown-400 to-transparent" />
          <div
            className="absolute inset-0"
            style={{
              backgroundImage:
                "radial-gradient(circle at 20% 80%, rgba(212,184,150,0.15) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(184,144,106,0.1) 0%, transparent 50%)",
            }}
          />
        </div>

        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 relative z-10">
          <div className="h-8 w-8 rounded-lg bg-brown-600 flex items-center justify-center">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-4 w-4 text-brown-100"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
              />
            </svg>
          </div>
          <span className="text-lg font-700 text-brown-100 tracking-tight">
            NexusFlow
          </span>
        </Link>

        {/* Central message */}
        <div className="relative z-10">
          <h2 className="text-4xl font-800 tracking-tighter text-brown-50 leading-tight mb-6">
            Your AI workflows
            <br />
            <span className="text-brown-400">are waiting.</span>
          </h2>
          <div className="space-y-3">
            {[
              "Visual workflow canvas",
              "Multi-agent orchestration",
              "Real-time observability",
            ].map((f) => (
              <div
                key={f}
                className="flex items-center gap-3 text-sm text-brown-300"
              >
                <CheckCircle className="h-4 w-4 text-brown-500 shrink-0" />
                {f}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom tagline */}
        <p className="text-xs text-brown-600 relative z-10">
          © {new Date().getFullYear()} NexusFlow AI
        </p>
      </motion.div>

      {/* Right — form panel */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col justify-center px-6 py-16 lg:px-20 xl:px-28"
      >
        {/* Mobile logo */}
        <Link href="/" className="flex items-center gap-2.5 mb-10 lg:hidden">
          <div className="h-7 w-7 rounded-lg bg-brown-700 flex items-center justify-center">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-3.5 w-3.5 text-brown-100"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
              />
            </svg>
          </div>
          <span className="text-base font-700 text-brown-900 tracking-tight">
            NexusFlow
          </span>
        </Link>

        <div className="max-w-sm w-full mx-auto lg:mx-0">
          <div className="mb-8">
            <h1 className="text-3xl font-800 tracking-tighter text-brown-900 mb-2">
              Welcome back
            </h1>
            <p className="text-sm text-brown-500">
              Sign in to continue to your dashboard.
            </p>
          </div>

          <AuthView pathname="sign-in" />

          <div className="mt-6 text-center space-y-3">
            <Link
              href="/forgot-password"
              className="block text-sm text-brown-600 hover:text-brown-900 transition-colors"
            >
              Forgot your password?
            </Link>
            <p className="text-sm text-brown-500">
              No account?{" "}
              <Link
                href="/register"
                className="text-brown-700 font-medium hover:text-brown-900 transition-colors"
              >
                Create one free
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
