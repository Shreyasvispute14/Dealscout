import { useState } from "react";
import type { FormEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, LockKeyhole, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiPost } from "@/lib/api";
import type { LoginResponse } from "@/lib/types";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("student@sppu-project.local");
  const [password, setPassword] = useState("demo123");
  const login = useMutation({
    mutationFn: () => apiPost<LoginResponse>("/auth/login", { email, password }),
    onSuccess: () => navigate("/"),
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    login.mutate();
  }

  return (
    <main className="grid min-h-svh bg-[#f8fafc] text-[#0f172a] lg:grid-cols-[.9fr_1.1fr]">
      <section className="hidden flex-col justify-between bg-[#0f172a] p-10 text-white lg:flex" data-testid="login-intro-panel">
        <Link to="/" className="flex items-center gap-2 font-heading text-xl font-bold" data-testid="login-brand-link"><span className="grid size-9 place-items-center rounded-xl bg-emerald-500 text-[#0f172a]">D</span> dealscout</Link>
        <div className="max-w-md"><p className="mb-4 font-mono text-xs uppercase tracking-[0.2em] text-emerald-300">Project workspace</p><h1 className="font-heading text-5xl font-black leading-[.98]">Compare smarter. Explain your project better.</h1><p className="mt-6 text-lg leading-relaxed text-slate-300">Log in to see search data collected by your comparison engine and prepare your academic demonstration.</p></div>
        <p className="font-mono text-xs text-slate-400">SPPU • TYBSc Computer Science</p>
      </section>
      <section className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">
          <Link to="/" className="mb-8 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-950" data-testid="login-back-link"><ArrowLeft className="size-4" /> Back to DealScout</Link>
          <Card className="border-slate-200 bg-white shadow-xl shadow-slate-200/50" data-testid="login-card">
            <CardHeader className="space-y-3 p-8"><div className="grid size-11 place-items-center rounded-xl bg-emerald-100 text-emerald-700"><LockKeyhole className="size-5" /></div><CardTitle className="font-heading text-3xl font-black">Welcome back</CardTitle><p className="text-sm leading-relaxed text-slate-500">Use the demo account to open your collected data dashboard.</p></CardHeader>
            <CardContent className="p-8 pt-0"><form onSubmit={submit} className="space-y-5" data-testid="login-form"><label className="block text-sm font-semibold">Email<Input aria-label="Email" data-testid="login-email-input" className="mt-2 h-11" value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label><label className="block text-sm font-semibold">Password<Input aria-label="Password" data-testid="login-password-input" className="mt-2 h-11" value={password} onChange={(event) => setPassword(event.target.value)} type="password" required /></label>{login.error && <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" data-testid="login-error-message">{login.error instanceof Error ? login.error.message : "Login failed"}</p>}<Button type="submit" disabled={login.isPending} className="h-11 w-full bg-[#0f172a] text-white hover:bg-slate-800" data-testid="login-submit-button">{login.isPending ? "Signing in…" : "Sign in to project"}<UserRound className="ml-2 size-4" /></Button></form><div className="mt-6 rounded-lg border border-dashed border-emerald-200 bg-emerald-50 p-4 text-xs leading-relaxed text-emerald-900" data-testid="login-demo-credentials">Demo credentials<br /><strong>student@sppu-project.local</strong> · <strong>demo123</strong></div></CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}