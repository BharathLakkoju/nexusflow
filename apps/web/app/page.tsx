"use client";

import Link from "next/link";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { MarketingNav } from "@/components/marketing/MarketingNav";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import {
  ArrowRight,
  GitBranch,
  Brain,
  Zap,
  BarChart3,
  CheckCircle,
  Users,
  Shield,
  Layers,
} from "lucide-react";

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.55,
      ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
    },
  }),
};

function AnimatedSection({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

const FEATURES = [
  {
    icon: GitBranch,
    title: "Visual Workflow Builder",
    desc: "Drag-and-drop canvas with 11 node types. Build DAGs visually without touching code.",
    color: "bg-brown-100",
  },
  {
    icon: Brain,
    title: "Persistent Agent Memory",
    desc: "Agents retain context across sessions. Build systems that genuinely learn from history.",
    color: "bg-brown-200/60",
  },
  {
    icon: Zap,
    title: "RAG Knowledge Base",
    desc: "Upload PDFs, Docs, CSVs. Agents pull semantic context automatically at runtime.",
    color: "bg-brown-100",
  },
  {
    icon: BarChart3,
    title: "Full Observability",
    desc: "Token costs, execution traces, success rates. Every agent run is auditable.",
    color: "bg-brown-200/60",
  },
];

const STATS = [
  { value: "11", label: "Node Types" },
  { value: "4", label: "Agent Roles" },
  { value: "99.3%", label: "Uptime SLA" },
  { value: "<2s", label: "Median Latency" },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Design Your Workflow",
    desc: "Use the visual canvas to connect Researcher, Planner, Executor, and Critic agents into a DAG.",
  },
  {
    step: "02",
    title: "Connect Knowledge",
    desc: "Upload documents into the RAG knowledge base. Agents retrieve relevant context automatically.",
  },
  {
    step: "03",
    title: "Deploy & Monitor",
    desc: "Trigger workflows via API or schedule. Watch real-time execution in the analytics dashboard.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-[100dvh] bg-brown-50 text-brown-900">
      <MarketingNav />

      {/* Hero */}
      <section className="min-h-[100dvh] flex items-center pt-16">
        <div className="max-w-[1400px] mx-auto px-6 w-full">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center py-20 lg:py-0">
            {/* Left */}
            <div>
              <motion.div
                custom={0}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                className="inline-flex items-center gap-2 bg-brown-100 border border-brown-200 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-700 mb-8"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-brown-500 animate-pulse" />
                Multi-Agent AI Orchestration
              </motion.div>

              <motion.h1
                custom={1}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                className="text-5xl md:text-6xl lg:text-7xl font-800 tracking-tighter leading-none text-brown-900 mb-6"
              >
                Build AI&nbsp;teams
                <br />
                <span className="text-brown-500">that think</span>
                <br />
                together.
              </motion.h1>

              <motion.p
                custom={2}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                className="text-lg text-brown-600 leading-relaxed max-w-[48ch] mb-10"
              >
                Design, deploy, and monitor multi-agent AI systems with a visual
                workflow builder. Connect research, planning, execution, and
                critique agents — without writing infrastructure.
              </motion.p>

              <motion.div
                custom={3}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                className="flex flex-col sm:flex-row gap-3"
              >
                <Link
                  href="/register"
                  className="inline-flex items-center justify-center gap-2 bg-brown-800 hover:bg-brown-900 text-brown-50 font-semibold px-7 py-3.5 rounded-full transition-all duration-200 active:scale-[0.98] text-sm"
                >
                  Start building free
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/features"
                  className="inline-flex items-center justify-center gap-2 bg-brown-100 hover:bg-brown-200 text-brown-800 font-medium px-7 py-3.5 rounded-full transition-all duration-200 text-sm border border-brown-200"
                >
                  See all features
                </Link>
              </motion.div>

              <motion.div
                custom={4}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                className="mt-12 flex items-center gap-6"
              >
                {[
                  "No credit card required",
                  "Free tier available",
                  "SOC 2 compliant",
                ].map((t) => (
                  <div
                    key={t}
                    className="flex items-center gap-1.5 text-xs text-brown-500"
                  >
                    <CheckCircle className="h-3.5 w-3.5 text-brown-400" />
                    {t}
                  </div>
                ))}
              </motion.div>
            </div>

            {/* Right — abstract workflow preview */}
            <motion.div
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{
                duration: 0.7,
                delay: 0.3,
                ease: [0.16, 1, 0.3, 1],
              }}
              className="hidden lg:block"
            >
              <div className="relative">
                {/* Outer card */}
                <div className="bg-brown-100 border border-brown-200 rounded-3xl p-8 shadow-[0_24px_64px_-16px_rgba(107,66,38,0.12)]">
                  <div className="text-xs font-medium text-brown-500 mb-5 uppercase tracking-widest">
                    Workflow Canvas
                  </div>
                  {/* Simulated node graph */}
                  <div className="space-y-3">
                    {[
                      {
                        label: "Researcher Agent",
                        color: "bg-brown-200",
                        w: "w-36",
                      },
                      {
                        label: "Planner Agent",
                        color: "bg-brown-300/60",
                        w: "w-28",
                      },
                      {
                        label: "Executor Agent",
                        color: "bg-brown-200",
                        w: "w-40",
                      },
                      {
                        label: "Critic Agent",
                        color: "bg-brown-300/60",
                        w: "w-32",
                      },
                    ].map((node, i) => (
                      <motion.div
                        key={node.label}
                        initial={{ opacity: 0, x: -12 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + i * 0.12, duration: 0.45 }}
                        className="flex items-center gap-3"
                      >
                        <div
                          className={`h-9 ${node.w} ${node.color} rounded-lg border border-brown-300/40 flex items-center px-3`}
                        >
                          <span className="text-xs font-medium text-brown-700 truncate">
                            {node.label}
                          </span>
                        </div>
                        {i < 3 && (
                          <div className="h-px flex-1 border-t border-dashed border-brown-300" />
                        )}
                      </motion.div>
                    ))}
                  </div>

                  {/* Stats row */}
                  <div className="mt-6 grid grid-cols-3 gap-3">
                    {[
                      { v: "247", l: "Runs today" },
                      { v: "98.7%", l: "Success" },
                      { v: "$0.042", l: "Avg cost" },
                    ].map((s) => (
                      <div
                        key={s.l}
                        className="bg-brown-50 rounded-xl p-3 border border-brown-200/60"
                      >
                        <div className="text-lg font-700 text-brown-800">
                          {s.v}
                        </div>
                        <div className="text-[10px] text-brown-500 mt-0.5">
                          {s.l}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Floating accent */}
                <motion.div
                  animate={{ y: [0, -8, 0] }}
                  transition={{
                    repeat: Infinity,
                    duration: 5,
                    ease: "easeInOut",
                  }}
                  className="absolute -top-4 -right-4 bg-brown-700 text-brown-50 rounded-2xl px-4 py-2.5 shadow-lg"
                >
                  <div className="text-xs font-semibold">Live execution</div>
                  <div className="text-[10px] text-brown-300 mt-0.5">
                    4 agents active
                  </div>
                </motion.div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="bg-brown-100 border-y border-brown-200">
        <div className="max-w-[1400px] mx-auto px-6 py-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {STATS.map((s) => (
              <AnimatedSection key={s.label} className="text-center">
                <div className="text-3xl font-800 text-brown-800 tracking-tight">
                  {s.value}
                </div>
                <div className="text-sm text-brown-500 mt-1">{s.label}</div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Features bento */}
      <section className="py-28 max-w-[1400px] mx-auto px-6">
        <AnimatedSection className="mb-16">
          <div className="inline-flex items-center gap-2 bg-brown-100 border border-brown-200 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-600 mb-5">
            Platform capabilities
          </div>
          <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900 mb-4">
            Everything your AI team needs
          </h2>
          <p className="text-brown-500 text-lg max-w-[52ch] leading-relaxed">
            One platform to design workflows, manage knowledge, and observe
            every decision your agents make.
          </p>
        </AnimatedSection>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {FEATURES.map((f, i) => (
            <AnimatedSection key={f.title}>
              <motion.div
                whileHover={{ y: -3 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                className={`${f.color} border border-brown-200 rounded-2xl p-8 h-full group cursor-default`}
              >
                <div className="h-11 w-11 rounded-xl bg-brown-700/10 flex items-center justify-center mb-5 group-hover:bg-brown-700/20 transition-colors">
                  <f.icon className="h-5 w-5 text-brown-700" />
                </div>
                <h3 className="text-xl font-700 text-brown-900 mb-3 tracking-tight">
                  {f.title}
                </h3>
                <p className="text-brown-600 text-sm leading-relaxed">
                  {f.desc}
                </p>
              </motion.div>
            </AnimatedSection>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-brown-100 py-28 border-y border-brown-200">
        <div className="max-w-[1400px] mx-auto px-6">
          <AnimatedSection className="mb-16">
            <div className="inline-flex items-center gap-2 bg-brown-200/60 border border-brown-300/50 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-700 mb-5">
              How it works
            </div>
            <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900">
              Three steps to production
            </h2>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {/* Connecting line */}
            <div className="absolute top-8 left-0 right-0 hidden md:block">
              <div className="h-px border-t border-dashed border-brown-300 mx-12" />
            </div>

            {HOW_IT_WORKS.map((step, i) => (
              <AnimatedSection key={step.step}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15, duration: 0.5 }}
                  className="relative bg-brown-50 border border-brown-200 rounded-2xl p-7"
                >
                  <div className="h-14 w-14 rounded-xl bg-brown-700 text-brown-50 flex items-center justify-center font-800 text-lg mb-6">
                    {step.step}
                  </div>
                  <h3 className="text-xl font-700 text-brown-900 mb-3 tracking-tight">
                    {step.title}
                  </h3>
                  <p className="text-brown-500 text-sm leading-relaxed">
                    {step.desc}
                  </p>
                </motion.div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Trust signals */}
      <section className="py-28 max-w-[1400px] mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <AnimatedSection>
            <div className="inline-flex items-center gap-2 bg-brown-100 border border-brown-200 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-600 mb-5">
              Built for scale
            </div>
            <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900 mb-6">
              Enterprise-grade
              <br />
              from day one.
            </h2>
            <p className="text-brown-500 text-base leading-relaxed mb-8 max-w-[48ch]">
              Role-based access, RBAC, human-in-the-loop approvals, and full
              audit logs ship out of the box — so your team can move fast
              without compromising control.
            </p>
            <div className="space-y-3">
              {[
                { icon: Shield, label: "RBAC & organization management" },
                { icon: Users, label: "Human-in-the-loop approval queues" },
                { icon: Layers, label: "Multi-tenant data isolation" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="flex items-center gap-3 text-sm text-brown-700"
                >
                  <div className="h-8 w-8 rounded-lg bg-brown-100 border border-brown-200 flex items-center justify-center shrink-0">
                    <item.icon className="h-4 w-4 text-brown-600" />
                  </div>
                  {item.label}
                </div>
              ))}
            </div>
          </AnimatedSection>

          <AnimatedSection>
            <div className="bg-brown-100 border border-brown-200 rounded-3xl p-8 space-y-4">
              {/* Simulated approval card */}
              <div className="text-xs text-brown-500 uppercase tracking-widest font-medium mb-6">
                Pending Approvals
              </div>
              {[
                {
                  task: "Send customer refund email",
                  agent: "Executor Agent",
                  time: "2m ago",
                },
                {
                  task: "Update production database",
                  agent: "Executor Agent",
                  time: "5m ago",
                },
              ].map((item) => (
                <div
                  key={item.task}
                  className="bg-brown-50 border border-brown-200 rounded-xl p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-sm font-medium text-brown-800">
                        {item.task}
                      </div>
                      <div className="text-xs text-brown-500 mt-1">
                        {item.agent} · {item.time}
                      </div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button className="text-xs font-medium bg-brown-700 text-brown-50 px-3 py-1.5 rounded-lg">
                        Approve
                      </button>
                      <button className="text-xs font-medium bg-brown-200 text-brown-700 px-3 py-1.5 rounded-lg">
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brown-800 py-24">
        <div className="max-w-[1400px] mx-auto px-6 text-center">
          <AnimatedSection>
            <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-50 mb-5">
              Start orchestrating today.
            </h2>
            <p className="text-brown-300 text-lg mb-10 max-w-[42ch] mx-auto">
              Free tier includes 1,000 agent executions per month. No credit
              card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                href="/register"
                className="inline-flex items-center justify-center gap-2 bg-brown-50 hover:bg-brown-100 text-brown-900 font-semibold px-8 py-3.5 rounded-full transition-all duration-200 active:scale-[0.98]"
              >
                Create free account
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center bg-brown-700/40 hover:bg-brown-700/60 text-brown-100 font-medium px-8 py-3.5 rounded-full transition-all duration-200 border border-brown-600"
              >
                Sign in
              </Link>
            </div>
          </AnimatedSection>
        </div>
      </section>

      <MarketingFooter />
    </div>
  );
}
