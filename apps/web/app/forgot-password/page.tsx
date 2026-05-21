"use client";

import { AuthView } from "@neondatabase/auth-ui";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-[100dvh] bg-brown-50 flex items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-sm"
      >
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 mb-10">
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

        <div className="mb-8">
          <h1 className="text-3xl font-800 tracking-tighter text-brown-900 mb-2">
            Reset your password
          </h1>
          <p className="text-sm text-brown-500 leading-relaxed">
            Enter your email address and we&apos;ll send you a link to reset
            your password.
          </p>
        </div>

        <AuthView pathname="forgot-password" />

        <div className="mt-6">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-sm text-brown-600 hover:text-brown-900 transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back to sign in
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
