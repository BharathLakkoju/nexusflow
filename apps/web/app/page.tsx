import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Bot, Zap, GitBranch, BarChart3, ArrowRight, Star } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-purple-950/20 to-slate-950 text-white">
      {/* Nav */}
      <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="h-7 w-7 text-purple-400" />
          <span className="text-xl font-bold">NexusFlow AI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" className="text-white/70 hover:text-white">
              Sign In
            </Button>
          </Link>
          <Link href="/register">
            <Button className="bg-purple-600 hover:bg-purple-700">
              Get Started Free
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-6 py-24 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-purple-900/40 border border-purple-500/30 rounded-full px-4 py-1.5 text-sm text-purple-300 mb-6">
          <Star className="h-3.5 w-3.5" />
          Multi-Agent AI Orchestration Platform
        </div>
        <h1 className="text-5xl sm:text-6xl font-extrabold leading-tight mb-6 bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent">
          Build AI Workflows That Think Together
        </h1>
        <p className="text-xl text-white/60 mb-10 max-w-2xl mx-auto">
          Design, deploy, and monitor multi-agent AI systems with a visual
          workflow builder. Connect researcher, planner, executor, and critic
          agents — no code required.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register">
            <Button
              size="lg"
              className="bg-purple-600 hover:bg-purple-700 gap-2 text-base px-8"
            >
              Start Building Free <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/login">
            <Button
              size="lg"
              variant="outline"
              className="border-white/20 text-white hover:bg-white/5 text-base px-8"
            >
              Sign In
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 pb-24 max-w-5xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            icon: GitBranch,
            title: "Visual Workflow Builder",
            desc: "Drag-and-drop canvas with 11 node types. Build complex DAGs visually.",
          },
          {
            icon: Bot,
            title: "Multi-Agent Teams",
            desc: "Researcher + Planner + Executor + Critic agents work together autonomously.",
          },
          {
            icon: Zap,
            title: "RAG Knowledge Base",
            desc: "Upload PDFs, Docs, CSVs. Agents retrieve semantic context automatically.",
          },
          {
            icon: BarChart3,
            title: "Analytics Dashboard",
            desc: "Track token usage, costs, execution success rates, and agent performance.",
          },
        ].map((f) => (
          <div
            key={f.title}
            className="bg-white/5 border border-white/10 rounded-xl p-6 hover:bg-white/8 transition-colors"
          >
            <f.icon className="h-8 w-8 text-purple-400 mb-3" />
            <h3 className="font-semibold text-white mb-2">{f.title}</h3>
            <p className="text-sm text-white/50">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
