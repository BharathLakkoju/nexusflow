/**
 * useSSE: Hook for consuming Server-Sent Events from workflow execution stream.
 */
"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export interface SSEEvent {
  type: string;
  node_id?: string;
  node_type?: string;
  timestamp?: string;
  data?: Record<string, unknown>;
  output?: string;
  error?: string;
  status?: string;
}

export interface UseSSEResult {
  events: SSEEvent[];
  isConnected: boolean;
  isDone: boolean;
  error: string | null;
  clearEvents: () => void;
}

const TERMINAL_TYPES = new Set(["execution_complete", "execution_failed", "execution_rejected"]);
const API_BASE = process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") ?? "http://localhost:8000";

export function useSSE(executionId: string | null, token: string | null): UseSSEResult {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sourceRef = useRef<EventSource | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);
  const cursorRef = useRef(0);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setIsDone(false);
    setError(null);
    cursorRef.current = 0;
  }, []);

  useEffect(() => {
    if (!executionId || !token) return;

    clearEvents();
    setIsConnected(true);

    const streamUrl = `${API_BASE}/api/v1/stream/executions/${executionId}`;

    // Use polling fallback since EventSource doesn't support custom headers
    // We poll the backend which reads from Redis
    const poll = async () => {
      try {
        const res = await fetch(streamUrl, {
          headers: { Authorization: `Bearer ${token}` },
          signal: AbortSignal.timeout(30000),
        });

        if (!res.ok || !res.body) {
          setError(`Stream error: ${res.status}`);
          setIsConnected(false);
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim();
              if (!data) continue;
              try {
                const evt = JSON.parse(data) as SSEEvent;
                setEvents((prev) => [...prev, evt]);
                if (TERMINAL_TYPES.has(evt.type)) {
                  setIsDone(true);
                  setIsConnected(false);
                  reader.cancel();
                  return;
                }
              } catch {}
            }
          }
        }

        setIsConnected(false);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Connection failed";
        setError(msg);
        setIsConnected(false);
      }
    };

    poll();

    return () => {
      sourceRef.current?.close();
      if (pollRef.current) clearTimeout(pollRef.current);
    };
  }, [executionId, token, clearEvents]);

  return { events, isConnected, isDone, error, clearEvents };
}
