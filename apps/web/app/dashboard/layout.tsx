"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/lib/auth/hooks";
import { Sidebar } from "@/components/layout/Sidebar";
import { authClient } from "@/lib/auth/client";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const user = useUser();
  const { isPending } = authClient.useSession();

  useEffect(() => {
    if (!isPending && !user) {
      router.replace("/login");
    }
  }, [user, isPending, router]);

  if (isPending) {
    return (
      <div className="min-h-screen bg-brown-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-brown-700 flex items-center justify-center animate-pulse">
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
          <p className="text-xs text-brown-500">Loading…</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-brown-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-brown-50">
        <div className="p-7">{children}</div>
      </main>
    </div>
  );
}
