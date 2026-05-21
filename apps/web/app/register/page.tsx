"use client";

import { AuthView } from "@neondatabase/auth-ui";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export default function RegisterPage() {
  return (
    <div className="min-h-[100dvh] bg-brown-50 grid grid-cols-1 lg:grid-cols-2">
      {/* Left — branding panel */}
      <motion.div
        initial={{ opacity: 0, x: -24 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="hidden lg:flex flex-col justify-between bg-brown-800 p-12 relative overflow-hidden"
      >
        <div className="absolute inset-0 opacity-10">
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

        {/* Central value props */}
        <div className="relative z-10 space-y-6">
          <h2 className="text-4xl font-800 tracking-tighter text-brown-50 leading-tight">
            Build your first
            <br />
            <span className="text-brown-400">agent workflow</span>
            <br />
            in minutes.
          </h2>
          <div className="space-y-4">
            {[
              {
                label: "Free tier",
                desc: "1,000 executions / month at no cost",
              },
              {
                label: "No infrastructure",
                desc: "We handle hosting, scaling, and uptime",
              },
              {
                label: "No code required",
                desc: "Visual builder for any workflow",
              },
            ].map((item) => (
              <div key={item.label} className="flex items-start gap-3">
                <div className="h-5 w-5 rounded-full bg-brown-600/40 border border-brown-500/30 flex items-center justify-center shrink-0 mt-0.5">
                  <div className="h-1.5 w-1.5 rounded-full bg-brown-400" />
                </div>
                <div>
                  <div className="text-sm font-medium text-brown-200">
                    {item.label}
                  </div>
                  <div className="text-xs text-brown-500 mt-0.5">
                    {item.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

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
              Create an account
            </h1>
            <p className="text-sm text-brown-500">
              Free tier — no credit card required.
            </p>
          </div>

          <AuthView pathname="sign-up" />

          <p className="mt-6 text-sm text-brown-500 text-center">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-brown-700 font-medium hover:text-brown-900 transition-colors inline-flex items-center gap-1"
            >
              Sign in
              <ArrowRight className="h-3 w-3" />
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
