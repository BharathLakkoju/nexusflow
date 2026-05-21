"use client";

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { MarketingNav } from "@/components/marketing/MarketingNav";
import { MarketingFooter } from "@/components/marketing/MarketingFooter";
import { ArrowRight, Target, Heart, Lightbulb, Users } from "lucide-react";
import Link from "next/link";

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

const VALUES = [
  {
    icon: Target,
    title: "Precision by default",
    desc: "Every agent decision is traceable. We believe in systems that show their reasoning — not black boxes.",
  },
  {
    icon: Heart,
    title: "Genuinely human-first",
    desc: "Automation should augment people, not replace them. Human-in-the-loop controls are baked into every workflow.",
  },
  {
    icon: Lightbulb,
    title: "Composable systems",
    desc: "We build primitives, not monoliths. Our platform is designed to fit into your existing infrastructure.",
  },
  {
    icon: Users,
    title: "Teams over tools",
    desc: "The best AI systems are built by teams. Collaboration, RBAC, and shared context are first-class.",
  },
];

const TEAM = [
  {
    name: "Marcelline Adeyemi",
    role: "Founder & CEO",
    img: "https://picsum.photos/seed/team_adeyemi/200/200",
    bio: "Ex-DeepMind. Built large-scale ML infrastructure for 7 years.",
  },
  {
    name: "Theo Kaltenbach",
    role: "CTO",
    img: "https://picsum.photos/seed/team_kaltenbach/200/200",
    bio: "Distributed systems engineer. Previously at Stripe and Vercel.",
  },
  {
    name: "Priya Venkataraman",
    role: "Head of Product",
    img: "https://picsum.photos/seed/team_venkataraman/200/200",
    bio: "Product leader with deep focus on developer experience.",
  },
  {
    name: "Osei Mensah",
    role: "Lead AI Engineer",
    img: "https://picsum.photos/seed/team_mensah/200/200",
    bio: "LLM researcher turned builder. Obsessed with agent reliability.",
  },
];

export default function AboutPage() {
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
            About NexusFlow
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-end">
            <div>
              <h1 className="text-5xl md:text-6xl font-800 tracking-tighter leading-none text-brown-900 mb-6">
                We build AI systems
                <br />
                <span className="text-brown-500">teams can trust.</span>
              </h1>
            </div>
            <div>
              <p className="text-lg text-brown-600 leading-relaxed">
                NexusFlow started from a simple frustration: existing AI tools
                were either too rigid for real workflows or too opaque to audit.
                We built the platform we always wanted — composable, observable,
                and genuinely collaborative.
              </p>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Mission */}
      <section className="bg-brown-800 py-24">
        <div className="max-w-[1400px] mx-auto px-6">
          <AnimatedSection>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              <div className="lg:col-span-1">
                <div className="text-xs font-semibold tracking-widest uppercase text-brown-400 mb-4">
                  Our Mission
                </div>
                <div className="h-px w-12 bg-brown-500 mb-6" />
              </div>
              <div className="lg:col-span-2">
                <blockquote className="text-3xl md:text-4xl font-600 text-brown-100 leading-relaxed tracking-tight">
                  "Make AI orchestration so transparent and controllable that
                  any team can ship reliable agents — not just the teams with ML
                  PhD engineers."
                </blockquote>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Values */}
      <section className="py-28 max-w-[1400px] mx-auto px-6">
        <AnimatedSection className="mb-16">
          <div className="inline-flex items-center gap-2 bg-brown-100 border border-brown-200 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-600 mb-5">
            What we stand for
          </div>
          <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900">
            Our values
          </h2>
        </AnimatedSection>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {VALUES.map((v, i) => (
            <motion.div
              key={v.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="bg-brown-100 border border-brown-200 rounded-2xl p-7"
            >
              <div className="h-10 w-10 rounded-xl bg-brown-700/10 flex items-center justify-center mb-5">
                <v.icon className="h-5 w-5 text-brown-700" />
              </div>
              <h3 className="text-xl font-700 text-brown-900 mb-3 tracking-tight">
                {v.title}
              </h3>
              <p className="text-brown-600 text-sm leading-relaxed">{v.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="bg-brown-100 border-y border-brown-200 py-28">
        <div className="max-w-[1400px] mx-auto px-6">
          <AnimatedSection className="mb-16">
            <div className="inline-flex items-center gap-2 bg-brown-200/60 border border-brown-300/50 rounded-full px-3.5 py-1.5 text-xs font-medium text-brown-700 mb-5">
              The team
            </div>
            <h2 className="text-4xl md:text-5xl font-800 tracking-tighter text-brown-900">
              People behind the platform
            </h2>
          </AnimatedSection>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {TEAM.map((member, i) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className="bg-brown-50 border border-brown-200 rounded-2xl p-5"
              >
                <div className="h-16 w-16 rounded-xl overflow-hidden mb-4 bg-brown-200">
                  <img
                    src={member.img}
                    alt={member.name}
                    className="h-full w-full object-cover"
                  />
                </div>
                <div className="font-700 text-brown-900 text-base">
                  {member.name}
                </div>
                <div className="text-xs text-brown-500 font-medium mt-0.5 mb-3">
                  {member.role}
                </div>
                <p className="text-xs text-brown-600 leading-relaxed">
                  {member.bio}
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
            Ready to build?
          </h2>
          <p className="text-brown-500 text-lg mb-10 max-w-[38ch] mx-auto">
            Join the teams already running production AI workflows on NexusFlow.
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
