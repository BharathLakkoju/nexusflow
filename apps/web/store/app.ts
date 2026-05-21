/**
 * Zustand store for global app state (token, org, UI state).
 */
"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  token: string | null;
  orgId: string | null;
  orgName: string | null;
  setToken: (token: string | null) => void;
  setOrg: (id: string, name: string) => void;
  clearSession: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      token: null,
      orgId: null,
      orgName: null,
      setToken: (token) => set({ token }),
      setOrg: (id, name) => set({ orgId: id, orgName: name }),
      clearSession: () => set({ token: null, orgId: null, orgName: null }),
    }),
    {
      name: "nexusflow-app-state",
      partialize: (state) => ({ orgId: state.orgId, orgName: state.orgName }),
    }
  )
);
