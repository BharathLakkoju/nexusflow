"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { MarketingNav } from "@/components/marketing/MarketingNav";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import Link from "next/link";
import {
  ArrowRight,
  GitBranch,
  Brain,
  Zap,
  BarChart3,
  Shield,
  FileText,
  Wrench,
  CheckSquare,
  Layers,
  Users,
  Terminal,
} from "lucide-react";

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

const FEATURE_GROUPS = [
  {
    label: "Workflow Engine",
    features: [
      {
        icon: GitBranch,
        title: "Visual DAG Builder",
        desc: "Drag-and-drop canvas with 11 node types. Build complex directed acyclic graphs visually — no code required.",
      },
      {
        icon: Layers,
        title: "11 Node Types",
        desc: "Agent, LLM, Tool, RAG, Condition, Loop, Parallel, Merge, Input, Output, and Webhook nodes.",
      },
      {
        icon: Terminal,
        title: "Code Executor",
        desc: "Run arbitrary Python or JavaScript in sandboxed containers directly within a workflow step.",
      },
    ],
  },
  {
    label: "Agent System",
    features: [
      {
        icon: Brain,
        title: "Multi-Agent Teams",
        desc: "Researcher, Planner, Executor, and Critic agents coordinate via a shared state graph.",
      },
      {
        icon: Zap,
        title: "LangGraph-Powered",
        desc: "Stateful agent graphs with cycle support, conditional edges, and interrupt-and-resume patterns.",
      },
      {
        icon: Wrench,
        title: "Tool Registry",
        desc: "Register HTTP tools, web search, file tools, or custom code tools. Agents call them autonomously.",
      },
    ],
  },
  {
    label: "Knowledge & Memory",
    features: [
      {
        icon: FileText,
        title: "RAG Knowledge Base",
        desc: "Upload PDFs, Docs, CSVs, and text. Agents retrieve relevant chunks automatically using vector similarity.",
      },
      {
        icon: Brain,
        title: "Persistent Memory",
        desc: "Short-term, long-term, and episodic memory layers. Agents build context across sessions.",
      },
      {
        icon: Zap,
        title: "Semantic Search",
        desc: "pgvector-backed embeddings with sub-100ms retrieval for real-time agent context injection.",
      },
    ],
  },
  {
    label: "Governance & Observability",
    features: [
      {
        icon: CheckSquare,
        title: "Human Approvals",
        desc: "Any workflow step can be flagged for human review before execution. Full approve/reject UI included.",
      },
      {
        icon: BarChart3,
        title: "Analytics Dashboard",
        desc: "Token usage, cost tracking, execution success rates, and per-agent performance metrics.",
      },
      {
        icon: Shield,
        title: "RBAC",
        desc: "Organization-level access control with role-based permissions for every resource.",
      },
      {
        icon: Users,
        title: "Multi-Tenancy",
        desc: "Full data isolation per organization. Invite teammates with granular permission scopes.",
      },
    ],
  },
];

export default function FeaturesPage() {
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
            Platform features
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-end">
            <div>
              <h1 className="text-5xl md:text-6xl font-800 tracking-tighter leading-none text-brown-900 mb-4">
                Everything you need
                <br />
                <span className="text-brown-500">to ship agents.</span>
              </h1>
            </div>
            <div>
              <p className="text-lg text-brown-600 leading-relaxed">
                NexusFlow covers the entire agent lifecycle — from visual
                workflow design to production observability. One platform, no
                glue code.
              </p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Feature groups */}
      <div className="pb-28">
        {FEATURE_GROUPS.map((group, groupIdx) => (
          <section
            key={group.label}
            className={
              groupIdx % 2 === 1
                ? "bg-brown-100 border-y border-brown-200 py-20"
                : "py-20 max-w-[1400px] mx-auto px-6"
            }
          >
            <div
              className={
                groupIdx % 2 === 1 ? "max-w-[1400px] mx-auto px-6" : ""
              }
            >
              <AnimatedSection className="mb-10">
                <div className="inline-flex items-center gap-2 bg-brown-200/60 border border-brown-300/40 rounded-full px-3.5 py-1.5 text-xs font-semibold text-brown-700 uppercase tracking-widest mb-4">
                  {group.label}
                </div>
              </AnimatedSection>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {group.features.map((f, i) => (
                  <AnimatedSection key={f.title}>
                    <motion.div
                      whileHover={{ y: -3 }}
                      transition={{
                        type: "spring",
                        stiffness: 300,
                        damping: 25,
                      }}
                      className="bg-brown-50 border border-brown-200 rounded-2xl p-6 h-full"
                    >
                      <div className="h-10 w-10 rounded-xl bg-brown-700/10 flex items-center justify-center mb-4">
                        <f.icon className="h-5 w-5 text-brown-700" />
                      </div>
                      <h3 className="text-base font-700 text-brown-900 mb-2 tracking-tight">
                        {f.title}
                      </h3>
                      <p className="text-sm text-brown-600 leading-relaxed">
                        {f.desc}
                      </p>
                    </motion.div>
                  </AnimatedSection>
                ))}
              </div>
            </div>
          </section>
        ))}
      </div>

      {/* CTA */}
      <section className="bg-brown-800 py-24">
        <div className="max-w-[1400px] mx-auto px-6 text-center">
          <AnimatedSection>
            <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-50 mb-5">
              All features. Free to start.
            </h2>
            <p className="text-brown-300 text-lg mb-10 max-w-[40ch] mx-auto">
              1,000 executions per month on the free tier. Upgrade when you need
              more.
            </p>
            <Link
              href="/register"
              className="inline-flex items-center gap-2 bg-brown-50 hover:bg-brown-100 text-brown-900 font-semibold px-8 py-3.5 rounded-full transition-all duration-200 active:scale-[0.98]"
            >
              Get started
              <ArrowRight className="h-4 w-4" />
            </Link>
          </AnimatedSection>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
}
