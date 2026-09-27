'use client';

import { apiFetch } from '../../../lib/apiClient';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  ShieldCheck, 
  CheckCircle2, 
  Clock, 
  Terminal, 
  MailCheck, 
  ThumbsUp,
  Building2,
  AlertCircle
} from 'lucide-react';

export default function ApplicationDetailPage({ params }: { params: { id: string } }) {
  const [app, setApp] = useState<any>(null);
  const [verifyingEmail, setVerifyingEmail] = useState(false);
  const [emailSyncResult, setEmailSyncResult] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAppDetails();
  }, [params.id]);

  async function fetchAppDetails() {
    setLoading(true);
    setError('');
    try {
      const found = await apiFetch<any>(`/api/v1/applications/${encodeURIComponent(params.id)}`);
      setApp(found);
      setLogs(Array.isArray(found.logs) ? found.logs : []);
    } catch (err) {
      setApp(null);
      setError(err instanceof Error ? err.message : 'Unable to load this application.');
    } finally { setLoading(false); }
  }

  async function handleVerifyViaEmail() {
    setVerifyingEmail(true);
    setEmailSyncResult(null);
    try {
      await apiFetch(`/api/v1/applications/${encodeURIComponent(params.id)}/verify-email`, { method: 'POST' });
      const record = await apiFetch<any>(`/api/v1/applications/${encodeURIComponent(params.id)}`);
      setApp(record);
      setLogs(Array.isArray(record.logs) ? record.logs : []);
      setEmailSyncResult(record.status === 'SUBMITTED_VERIFIED'
        ? 'SUCCESS: Confirmation is recorded for this application.'
        : 'No confirmation is recorded for this application yet.');
    } catch (err) {
      setEmailSyncResult(err instanceof Error ? err.message : 'Unable to verify this application.');
    } finally { setVerifyingEmail(false); }
  }

  if (loading) return <p role="status" className="p-8 text-neutral-400">Loading application…</p>;
  if (!app) return <div className="space-y-4"><Link href="/applications" className="text-emerald-400">Back to applications</Link><p role="alert">{error || 'Application not found.'}</p></div>;

  // STRICT INVARIANT: ONLY SUBMITTED_VERIFIED gets the green verified badge!
  const isVerified = app?.status === 'SUBMITTED_VERIFIED';

  return (
    <div className="space-y-6">
      
      {/* Back Link */}
      <Link href="/applications" className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 font-medium">
        <ArrowLeft size={14} /> Back to Application Tracker
      </Link>

      {/* Header Info Banner */}
      <div className="bg-neutral-900/60 p-6 rounded-2xl border border-neutral-800 flex justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">{app?.role || 'Role unavailable'}</h1>
          <div className="flex items-center gap-4 text-xs text-neutral-400 mt-1">
            <span className="flex items-center gap-1"><Building2 size={14} className="text-emerald-400" /> {app?.company || 'Target Employer'}</span>
            <span>ID: {params.id}</span>
          </div>
        </div>

        {/* STRICT Honest Status Badge */}
        <div className="text-right">
          {isVerified ? (
            <span className="px-4 py-1.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold flex items-center gap-1.5">
              <CheckCircle2 size={16} /> SUBMITTED_VERIFIED 🟢
            </span>
          ) : app?.status === 'SUBMITTED' ? (
            <span className="px-4 py-1.5 rounded-full bg-amber-950 text-amber-300 border border-amber-800 text-xs font-medium flex items-center gap-1.5">
              <Clock size={16} /> SUBMITTED (Unverified - Awaiting Email Sync) 🟡
            </span>
          ) : (
            <span className="px-4 py-1.5 rounded-full bg-neutral-800 text-neutral-300 border border-neutral-700 text-xs font-medium flex items-center gap-1.5">
              <Clock size={16} className="text-neutral-400" /> {app?.status || 'AWAITING_APPROVAL'}
            </span>
          )}
        </div>
      </div>

      {/* Two-Level Approval UI Section */}
      <div className="bg-neutral-900/80 p-6 rounded-xl border border-neutral-800 space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <ShieldCheck size={18} className="text-emerald-400" /> Application status and evidence
        </h2>

        <p className="text-sm text-neutral-400">
          This view displays the recorded application status. Complete the application in the employer portal;
          opening a browser or verifying login does not submit an application.
        </p>

        {/* Real Email Verification Action (No mock setTimeout) */}
        <div className="pt-3 border-t border-neutral-800 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-neutral-400 font-semibold">Authentic IMAP Employer Confirmation Sync</span>
            <button
              onClick={handleVerifyViaEmail}
              disabled={verifyingEmail || isVerified}
              className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-emerald-400 text-xs font-semibold rounded-lg transition border border-neutral-700 flex items-center gap-1.5"
            >
              <MailCheck size={14} /> {verifyingEmail ? 'Querying Candidate IMAP Inbox...' : 'Verify via Employer Email Sync'}
            </button>
          </div>

          {emailSyncResult && (
            <div className={`p-3 rounded-lg text-xs font-medium border flex items-center gap-2 ${
              emailSyncResult.startsWith('SUCCESS') 
                ? 'bg-emerald-950 text-emerald-300 border-emerald-800' 
                : 'bg-neutral-950 text-neutral-300 border-neutral-800'
            }`}>
              <AlertCircle size={14} className={emailSyncResult.startsWith('SUCCESS') ? 'text-emerald-400' : 'text-amber-400'} />
              <span>{emailSyncResult}</span>
            </div>
          )}
        </div>
      </div>

      {/* Live Event Log Console */}
      <div className="bg-neutral-900/60 p-6 rounded-xl border border-neutral-800 space-y-3">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Terminal size={16} className="text-emerald-400" /> Live Automation Event Log Console
        </h3>

        <div className="p-4 bg-neutral-950 rounded-xl border border-neutral-800 font-mono text-xs text-emerald-300 space-y-1.5 max-h-64 overflow-y-auto">
          {logs.map((log, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-neutral-600 text-[10px] shrink-0">[{idx + 1}]</span>
              <span className="leading-relaxed">{log}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
