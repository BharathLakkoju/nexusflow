"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "@/lib/auth/hooks";
import { authClient } from "@/lib/auth/client";
import {
  BarChart3,
  GitBranch,
  FileText,
  Brain,
  Wrench,
  Zap,
  CheckSquare,
  LogOut,
  Settings,
  Users,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview", icon: BarChart3 },
  { href: "/dashboard/workflows", label: "Workflows", icon: GitBranch },
  { href: "/dashboard/agents", label: "Agents", icon: Users },
  { href: "/dashboard/documents", label: "Knowledge Base", icon: FileText },
  { href: "/dashboard/memory", label: "Memory", icon: Brain },
  { href: "/dashboard/tools", label: "Tools", icon: Wrench },
  { href: "/dashboard/prompt-studio", label: "Prompt Studio", icon: Zap },
  { href: "/dashboard/approvals", label: "Approvals", icon: CheckSquare },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useUser();

  return (
    <aside className="w-60 h-screen bg-brown-900 border-r border-brown-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-brown-800">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="h-7 w-7 rounded-lg bg-brown-600 flex items-center justify-center">
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
          <span className="text-sm font-700 text-brown-100 tracking-tight">
            NexusFlow
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors relative",
                active
                  ? "bg-brown-700/50 text-brown-100"
                  : "text-brown-500 hover:text-brown-200 hover:bg-brown-800/60",
              )}
            >
              {active && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 bg-brown-700/50 rounded-lg"
                  transition={{ type: "spring", stiffness: 400, damping: 40 }}
                />
              )}
              <item.icon className="h-4 w-4 shrink-0 relative z-10" />
              <span className="relative z-10 font-medium">{item.label}</span>
              {active && (
                <ChevronRight className="h-3 w-3 ml-auto relative z-10 text-brown-400" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* User */}
      <div className="px-3 py-4 border-t border-brown-800">
        <div className="flex items-center gap-2.5 px-2 mb-3">
          <div className="h-7 w-7 rounded-full bg-brown-600 flex items-center justify-center text-brown-100 text-xs font-700 shrink-0">
            {user?.displayName?.[0]?.toUpperCase() ??
              user?.primaryEmail?.[0]?.toUpperCase() ??
              "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-brown-200 truncate">
              {user?.displayName ?? "User"}
            </p>
            <p className="text-[10px] text-brown-600 truncate">
              {user?.primaryEmail}
            </p>
          </div>
        </div>
        <button
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-brown-600 hover:text-brown-200 hover:bg-brown-800/60 transition-colors"
          onClick={() => authClient.signOut()}
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
