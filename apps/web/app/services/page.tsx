"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { MarketingNav } from "@/components/marketing/MarketingNav";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import Link from "next/link";
import { ArrowRight, CheckCircle } from "lucide-react";

function AnimatedSection({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

const PLANS = [
  {
    name: "Free",
    price: "$0",
    period: "/month",
    desc: "For individuals exploring AI workflows.",
    cta: "Start for free",
    href: "/register",
    features: [
      "1,000 agent executions / month",
      "3 active workflows",
      "100 MB knowledge base",
      "Community support",
      "Basic analytics",
    ],
    highlight: false,
  },
  {
    name: "Pro",
    price: "$49",
    period: "/month",
    desc: "For teams shipping production agents.",
    cta: "Start Pro trial",
    href: "/register",
    features: [
      "50,000 executions / month",
      "Unlimited workflows",
      "10 GB knowledge base",
      "Priority email support",
      "Full analytics & cost tracking",
      "Human-in-the-loop approvals",
      "RBAC & team management",
    ],
    highlight: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    desc: "For organizations with compliance needs.",
    cta: "Contact us",
    href: "/about",
    features: [
      "Unlimited executions",
      "Dedicated infrastructure",
      "SSO & SAML",
      "Custom data retention",
      "SLA guarantee",
      "Dedicated support engineer",
      "On-premise deployment option",
    ],
    highlight: false,
  },
];

const USE_CASES = [
  {
    title: "Customer Support Automation",
    desc: "Orchestrate research, drafting, and review agents to handle support tickets — with human approval before sending.",
    industry: "SaaS",
  },
  {
    title: "Legal Document Analysis",
    desc: "Upload contracts to the knowledge base. Agents extract clauses, flag risks, and summarize findings in minutes.",
    industry: "Legal",
  },
  {
    title: "Content Production Pipeline",
    desc: "Research agent gathers sources, planner structures the outline, executor writes, critic reviews — all automated.",
    industry: "Media",
  },
  {
    title: "Data Pipeline Orchestration",
    desc: "Use workflow DAGs to pull, transform, and load data with AI-enriched steps and error-handling agents.",
    industry: "Data",
  },
];

export default function ServicesPage() {
  return (
    <div className="min-h-[100dvh] bg-brown-50 text-brown-900">
      <MarketingNav />

      {/* Hero */}
      <section className="pt-36 pb-24 max-w-[1400px] mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="inline-flex items-center gap-2 bg-brown-100 border border-brown-200 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-600 mb-6">
            Services &amp; Pricing
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-end">
            <div>
              <h1 className="text-5xl md:text-6xl font-800 tracking-tighter leading-none text-brown-900 mb-4">
                Simple pricing.
                <br />
                <span className="text-brown-500">Serious capabilities.</span>
              </h1>
            </div>
            <div>
              <p className="text-lg text-brown-600 leading-relaxed">
                Start free and scale when you need it. Every plan includes the
                full feature set — we charge based on usage, not gated features.
              </p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Pricing */}
      <section className="pb-28 max-w-[1400px] mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {PLANS.map((plan, i) => (
            <AnimatedSection key={plan.name}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.12, duration: 0.5 }}
                className={`rounded-2xl p-7 h-full flex flex-col border ${
                  plan.highlight
                    ? "bg-brown-800 border-brown-700 shadow-[0_24px_64px_-16px_rgba(107,66,38,0.25)]"
                    : "bg-brown-100 border-brown-200"
                }`}
              >
                {plan.highlight && (
                  <div className="inline-flex items-center gap-1.5 bg-brown-600/40 border border-brown-500/30 rounded-full px-3 py-1 text-xs font-medium text-brown-200 mb-5 self-start">
                    Most popular
                  </div>
                )}
                <div
                  className={`text-sm font-semibold mb-1 ${plan.highlight ? "text-brown-300" : "text-brown-600"}`}
                >
                  {plan.name}
                </div>
                <div
                  className={`text-4xl font-800 tracking-tighter mb-1 ${plan.highlight ? "text-brown-50" : "text-brown-900"}`}
                >
                  {plan.price}
                  <span
                    className={`text-sm font-normal ${plan.highlight ? "text-brown-400" : "text-brown-500"}`}
                  >
                    {plan.period}
                  </span>
                </div>
                <p
                  className={`text-sm mb-6 ${plan.highlight ? "text-brown-400" : "text-brown-500"}`}
                >
                  {plan.desc}
                </p>

                <ul className="space-y-2.5 mb-8 flex-1">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2.5 text-sm">
                      <CheckCircle
                        className={`h-4 w-4 mt-0.5 shrink-0 ${plan.highlight ? "text-brown-400" : "text-brown-500"}`}
                      />
                      <span
                        className={
                          plan.highlight ? "text-brown-300" : "text-brown-700"
                        }
                      >
                        {f}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.href}
                  className={`inline-flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm transition-all duration-200 active:scale-[0.98] ${
                    plan.highlight
                      ? "bg-brown-50 hover:bg-brown-100 text-brown-900"
                      : "bg-brown-700 hover:bg-brown-800 text-brown-50"
                  }`}
                >
                  {plan.cta}
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </motion.div>
            </AnimatedSection>
          ))}
        </div>
      </section>

      {/* Use cases */}
      <section className="bg-brown-100 border-y border-brown-200 py-28">
        <div className="max-w-[1400px] mx-auto px-6">
          <AnimatedSection className="mb-16">
            <div className="inline-flex items-center gap-2 bg-brown-200/60 border border-brown-300/50 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-700 mb-5">
              What teams build
            </div>
            <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900">
              Built for real problems.
            </h2>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {USE_CASES.map((uc, i) => (
              <motion.div
                key={uc.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="bg-brown-50 border border-brown-200 rounded-2xl p-7"
              >
                <div className="inline-flex items-center bg-brown-200/60 border border-brown-300/40 rounded-full px-2.5 py-1 text-xs font-medium text-brown-700 mb-4">
                  {uc.industry}
                </div>
                <h3 className="text-xl font-700 text-brown-900 mb-3 tracking-tight">
                  {uc.title}
                </h3>
                <p className="text-sm text-brown-600 leading-relaxed">
                  {uc.desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 max-w-[1400px] mx-auto px-6 text-center">
        <AnimatedSection>
          <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900 mb-5">
            Start building today.
          </h2>
          <p className="text-brown-500 text-lg mb-10 max-w-[38ch] mx-auto">
            No credit card required. Full platform access on the free tier.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 bg-brown-800 hover:bg-brown-900 text-brown-50 font-semibold px-8 py-3.5 rounded-full transition-all duration-200 active:scale-[0.98]"
          >
            Get started free
            <ArrowRight className="h-4 w-4" />
          </Link>
        </AnimatedSection>
      </section>

      <MarketingFooter />
    </div>
  );
}
