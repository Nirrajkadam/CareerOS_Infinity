'use client';

import React, { useEffect, useState } from 'react';
import { apiFetch, apiRequest, AUTH_EXPIRED_EVENT } from '../lib/apiClient';

type Account = { id: string; email: string; full_name?: string };

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [checking, setChecking] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    const expired = () => { setAccount(null); setError('Your session expired. Please sign in again.'); };
    window.addEventListener(AUTH_EXPIRED_EVENT, expired);
    if (localStorage.getItem('careeros_access_token')) {
      apiFetch<Account>('/api/v1/auth/me')
        .then(user => { if (active) setAccount(user); })
        .catch(() => { if (active) setError('Unable to restore your session. Please sign in.'); })
        .finally(() => { if (active) setChecking(false); });
    } else setChecking(false);
    return () => { active = false; window.removeEventListener(AUTH_EXPIRED_EVENT, expired); };
  }, []);

  async function signIn(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (registering) {
        await apiFetch('/api/v1/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
        setRegistering(false);
      }
      const session = await apiFetch<{ access_token: string }>('/api/v1/auth/login', {
        method: 'POST', body: JSON.stringify({ email, password }),
      });
      localStorage.setItem('careeros_access_token', session.access_token);
      const user = await apiFetch<Account>('/api/v1/auth/me');
      setAccount(user);
      setPassword('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to sign in. Please try again.');
    } finally { setBusy(false); }
  }

  async function signOut() {
    setBusy(true);
    setError('');
    try {
      const response = await apiRequest('/api/v1/auth/logout', { method: 'POST' });
      if (!response.ok) throw new Error('Sign out failed. Please try again.');
      localStorage.removeItem('careeros_access_token');
      setAccount(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign out failed. Please try again.');
    } finally { setBusy(false); }
  }

  if (checking) return <p role="status" className="p-8 text-center text-neutral-400">Checking your session…</p>;
  if (account) return <>
    <div className="flex items-center justify-end gap-4 border-b border-neutral-800 px-6 py-2 text-xs">
      {error && <span role="alert" className="text-red-300">{error}</span>}
      <span className="text-neutral-400">{account.email}</span>
      <button onClick={signOut} disabled={busy} className="rounded px-3 py-2 text-emerald-400 hover:bg-neutral-800 disabled:opacity-50">Sign out</button>
    </div>
    {children}
  </>;

  return <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6 py-12">
    <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-8">
      <p className="mb-2 text-sm font-semibold text-emerald-400">CareerOS Infinity</p>
      <h1 className="text-2xl font-bold">{registering ? 'Create your account' : 'Sign in to your workspace'}</h1>
      <p className="mt-3 text-sm text-neutral-400">Manage your resumes and track your applications.</p>
      <form onSubmit={signIn} className="mt-6 space-y-4">
        <div><label htmlFor="email" className="mb-1 block text-sm">Email</label>
          <input id="email" name="email" type="email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} className="w-full rounded-lg border border-neutral-700 bg-neutral-950 p-3" /></div>
        <div><label htmlFor="password" className="mb-1 block text-sm">Password</label>
          <input id="password" name="password" type="password" autoComplete={registering ? 'new-password' : 'current-password'} minLength={registering ? 8 : 1} maxLength={1024} required value={password} onChange={e => setPassword(e.target.value)} className="w-full rounded-lg border border-neutral-700 bg-neutral-950 p-3" /></div>
        {error && <p role="alert" className="text-sm text-red-300">{error}</p>}
        <button disabled={busy} className="w-full rounded-lg bg-emerald-600 p-3 font-semibold hover:bg-emerald-500 disabled:opacity-50">{busy ? 'Please wait…' : registering ? 'Create account' : 'Sign in'}</button>
      </form>
      <button type="button" disabled={busy} onClick={() => { setRegistering(!registering); setError(''); }} className="mt-5 text-sm text-emerald-400">{registering ? 'Already have an account? Sign in' : 'New here? Create an account'}</button>
    </div>
  </main>;
}
