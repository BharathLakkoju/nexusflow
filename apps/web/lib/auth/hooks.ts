"use client";

import { authClient } from "./client";

type AuthTokenResponse = {
  data?: {
    token?: string | null;
  } | null;
};

/**
 * Drop-in replacement for Stack Auth's useUser().
 * Returns null when unauthenticated, otherwise a user object with
 * compatible shims for displayName, primaryEmail and getAuthJson().
 */
export function useUser() {
  const { data: session } = authClient.useSession();
  if (!session?.user) return null;
  const u = session.user;
  const sessionToken = session.session?.token;
  return {
    ...u,
    /** Stack Auth compat: maps to Better Auth `name` */
    displayName: u.name,
    /** Stack Auth compat: maps to Better Auth `email` */
    primaryEmail: u.email,
    /** Stack Auth compat: returns { accessToken } for bearer auth */
    getAuthJson: async (): Promise<{ accessToken: string } | null> => {
      if (sessionToken) return { accessToken: sessionToken };

      const result = (await authClient.token()) as AuthTokenResponse;
      return result.data?.token ? { accessToken: result.data.token } : null;
    },
  };
}
