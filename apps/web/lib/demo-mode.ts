"use client";

const DEMO_MODE_KEY = "nexusflow.demoMode";

export function enableDemoMode() {
  localStorage.setItem(DEMO_MODE_KEY, "enabled");
}

export function isDemoMode() {
  return localStorage.getItem(DEMO_MODE_KEY) === "enabled";
}
