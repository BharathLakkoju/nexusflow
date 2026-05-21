import { AuthView } from "@neondatabase/auth-ui";
import { authViewPaths } from "@neondatabase/auth-ui/server";
import { notFound, redirect } from "next/navigation";

const authPageRedirects = {
  [authViewPaths.SIGN_IN]: "/login",
  [authViewPaths.SIGN_UP]: "/register",
  [authViewPaths.FORGOT_PASSWORD]: "/forgot-password",
} as const;

const supportedAuthPaths = new Set(Object.values(authViewPaths));

export const dynamicParams = false;

export function generateStaticParams() {
  return Object.values(authViewPaths).map((path) => ({ path }));
}

export default async function AuthPage({
  params,
}: {
  params: Promise<{ path: string }>;
}) {
  const { path } = await params;

  if (!supportedAuthPaths.has(path)) {
    notFound();
  }

  const redirectPath =
    authPageRedirects[path as keyof typeof authPageRedirects];

  if (redirectPath) {
    redirect(redirectPath);
  }

  return (
    <main className="min-h-[100dvh] bg-brown-50 flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-sm">
        <AuthView path={path} />
      </div>
    </main>
  );
}
