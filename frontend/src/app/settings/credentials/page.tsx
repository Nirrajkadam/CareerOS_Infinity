'use client';

import { apiFetch, apiRequest } from '../../../lib/apiClient';

import React, { useState, useEffect } from 'react';
import { 
  KeyRound, 
  Lock, 
  CheckCircle2, 
  Save, 
  LogIn
} from 'lucide-react';

export default function CredentialVaultPage() {
  const [portal, setPortal] = useState('naukri');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [saved, setSaved] = useState(false);
  const [testingLogin, setTestingLogin] = useState(false);
  const [loginTested, setLoginTested] = useState(false);

  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedCredentials, setSavedCredentials] = useState<{ portal: string; username: string; date?: string }[]>([]);

  useEffect(() => {
    apiFetch<{ credentials: Record<string, string> }>('/api/v1/applications/credentials')
      .then(data => setSavedCredentials(Object.entries(data.credentials).map(([portal, username]) => ({ portal, username }))))
      .catch(err => setError(err instanceof Error ? err.message : 'Unable to load credentials.'));
  }, []);

  async function handleSaveCredentials(e: React.FormEvent) {
    e.preventDefault();
    if (!username || !password) return;
    setSaving(true);
    setSaved(false);
    setError('');
    try {
      await apiFetch('/api/v1/applications/credentials', {
        method: 'POST', body: JSON.stringify({ portal, username: username.trim(), password }),
      });
      setSavedCredentials(prev => [
        { portal, username: username.trim(), date: new Date().toISOString().split('T')[0] },
        ...prev.filter(c => c.portal !== portal),
      ]);
      setPassword('');
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save credentials.');
    } finally { setSaving(false); }
  }

  async function handleTestLogin() {
    setTestingLogin(true);
    setLoginTested(false);
    setError('');
    try {
      const res = await apiRequest('/api/v1/applications/launch-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portal })
      });
      if (res.ok) {
        setLoginTested(true);
      } else {
        const data = await res.json();
        throw new Error(data.detail || 'Unable to launch session');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to launch session.');
    } finally {
      setTestingLogin(false);
    }
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          Portal Credential Vault <KeyRound size={20} className="text-emerald-400" />
        </h1>
        <p className="text-xs text-neutral-400 mt-1">
          Fernet encrypted portal login credentials. Passwords are never displayed in plaintext.
        </p>
      </div>

      {/* Encryption Banner */}
      <div className="bg-emerald-950/40 p-4 rounded-xl border border-emerald-800 flex items-center gap-3 text-xs text-emerald-300">
        <Lock size={18} className="text-emerald-400 shrink-0" />
        <span>Portal credentials are encrypted with Fernet. Shared desktop sessions are restricted to the configured operator.</span>
      </div>

      {error && <p role="alert" className="rounded-lg border border-red-900 bg-red-950/30 p-4 text-sm text-red-200">{error}</p>}
      {/* Form & Saved Vault Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Add/Edit Credentials Form */}
        <form onSubmit={handleSaveCredentials} className="bg-neutral-900/60 p-6 rounded-xl border border-neutral-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Save Portal Credentials</h2>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-neutral-300">Target Job Portal</label>
            <select
              value={portal}
              onChange={(e) => setPortal(e.target.value)}
              className="w-full px-3 py-2 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="naukri">Naukri.com</option>
              <option value="linkedin">LinkedIn</option>
              <option value="indeed">Indeed India</option>
              <option value="foundit">Foundit</option>
              <option value="apna">Apna</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-neutral-300">Portal Email / Username</label>
            <input
              type="email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="nirraj.official@gmail.com"
              className="w-full px-3 py-2 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-neutral-300">Portal Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3 py-2 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit" disabled={saving}
              className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition shadow-lg shadow-emerald-900/30 flex items-center justify-center gap-1.5"
            >
              <Save size={14} /> {saved ? 'Encrypted & Saved!' : 'Encrypt & Save'}
            </button>

            {/* Test Login Button */}
            <button
              type="button"
              onClick={handleTestLogin}
              className="px-4 py-2.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-semibold text-xs rounded-lg transition border border-neutral-700 flex items-center gap-1.5"
            >
              <LogIn size={14} /> {testingLogin ? 'Opening Chrome...' : 'Test Login Only'}
            </button>
          </div>

          {loginTested && (
            <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 size={12} /> Browser launch requested. Complete candidate login when the window opens.
            </span>
          )}
        </form>

        {/* Stored Credentials List */}
        <div className="bg-neutral-900/60 p-6 rounded-xl border border-neutral-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Encrypted Vault Entries</h2>

          <div className="space-y-3">
            {savedCredentials.map((cred, idx) => (
              <div key={idx} className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 space-y-1.5">
                <div className="flex justify-between items-center text-xs font-bold text-white">
                  <span>{cred.portal}</span>
                  <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                    Fernet encrypted
                  </span>
                </div>
                <div className="text-xs text-emerald-400 font-mono font-semibold">{cred.username}</div>
                <div className="text-[10px] text-neutral-500 flex justify-between items-center pt-1">
                  <span>Password: ••••••••</span>
                  <span>Saved: {cred.date || 'Previously saved'}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
