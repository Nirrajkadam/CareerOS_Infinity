'use client';

import { apiFetch } from '../lib/apiClient';
import { ApplicationRecord, summarizeApplications, recentApplications, isVerifiedSubmission } from '../lib/dashboard';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  FileText, 
  Send, 
  Target, 
  TrendingUp, 
  Plus, 
  Search, 
  CheckCircle2, 
  Clock, 
  ShieldCheck, 
  ArrowRight,
  Sparkles
} from 'lucide-react';

export default function DashboardPage() {
  const [applications, setApplications] = useState<ApplicationRecord[] | null>(null);
  const [resumeCount, setResumeCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);
  const stats = applications ? summarizeApplications(applications) : null;
  const recentActivities = recentApplications(applications || []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    setApplications(null);
    setResumeCount(null);
    Promise.allSettled([
      apiFetch<ApplicationRecord[]>('/api/v1/applications'),
      apiFetch<unknown[]>('/api/v1/resumes'),
    ]).then(([apps, resumes]) => {
      if (!active) return;
      if (apps.status === 'fulfilled' && Array.isArray(apps.value)) setApplications(apps.value);
      if (resumes.status === 'fulfilled' && Array.isArray(resumes.value)) setResumeCount(resumes.value.length);
      if (apps.status === 'rejected' || resumes.status === 'rejected') {
        setError('Some dashboard data could not be loaded. Check your connection and try again.');
      }
      setLoading(false);
    });
    return () => { active = false; };
  }, [reload]);

  return (
    <div className="space-y-8">
      
      {/* Hero Welcome Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-neutral-900/60 p-6 rounded-2xl border border-neutral-800 backdrop-blur-md gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            CareerOS Intelligence Center <Sparkles size={18} className="text-emerald-400" />
          </h1>
          <p className="text-sm text-neutral-400 mt-1">
            Honest application tracking, TruthGuard resume tailoring, and candidate-controlled job discovery.
          </p>
        </div>

        {/* Quick Action Navigation Buttons */}
        <div className="flex items-center gap-3">
          <Link
            href="/resume"
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-900/30"
          >
            <Plus size={14} /> Upload Resume
          </Link>
          <Link
            href="/jobs"
            className="px-4 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-medium text-xs transition-all flex items-center gap-1.5 border border-neutral-700"
          >
            <Search size={14} /> Search Jobs
          </Link>
          <Link
            href="/applications"
            className="px-4 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-medium text-xs transition-all flex items-center gap-1.5 border border-neutral-700"
          >
            <Send size={14} /> Tracker
          </Link>
        </div>
      </div>

      {error && <div role="alert" className="flex items-center justify-between gap-4 rounded-lg border border-red-900 bg-red-950/30 p-4 text-sm text-red-200">
        <span>{error}</span><button onClick={() => setReload(value => value + 1)} className="rounded border border-red-800 px-3 py-2">Retry</button>
      </div>}
      {/* These metrics describe the loaded feed, which the API currently limits. */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-neutral-900/80 p-5 rounded-xl border border-neutral-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-neutral-400 font-semibold uppercase tracking-wider">Resumes in view</span>
            <div className="text-2xl font-bold text-white mt-1">{loading ? '…' : resumeCount ?? '—'}</div>
            <span className="text-[10px] text-emerald-400 mt-1 inline-block">Master & Tailored versions</span>
          </div>
          <div className="p-3 bg-neutral-800/80 rounded-lg text-emerald-400">
            <FileText size={22} />
          </div>
        </div>

        <div className="bg-neutral-900/80 p-5 rounded-xl border border-neutral-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-neutral-400 font-semibold uppercase tracking-wider">Active in feed</span>
            <div className="text-2xl font-bold text-white mt-1">{loading ? '…' : stats?.activeApplications ?? '—'}</div>
            <span className="text-[10px] text-emerald-400 mt-1 inline-block">Within loaded application feed</span>
          </div>
          <div className="p-3 bg-neutral-800/80 rounded-lg text-blue-400">
            <Send size={22} />
          </div>
        </div>

        <div className="bg-neutral-900/80 p-5 rounded-xl border border-neutral-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-neutral-400 font-semibold uppercase tracking-wider">Avg recorded ATS</span>
            <div className="text-2xl font-bold text-white mt-1">{loading ? '…' : stats?.avgAtsMatch == null ? '—' : `${stats.avgAtsMatch}%`}</div>
            <span className="text-[10px] text-emerald-400 mt-1 inline-block">Recorded ATS scores only</span>
          </div>
          <div className="p-3 bg-neutral-800/80 rounded-lg text-purple-400">
            <Target size={22} />
          </div>
        </div>

        <div className="bg-neutral-900/80 p-5 rounded-xl border border-neutral-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-neutral-400 font-semibold uppercase tracking-wider">Submitted · 7 days</span>
            <div className="text-2xl font-bold text-white mt-1">{loading ? '…' : stats?.appliesThisWeek ?? '—'}</div>
            <span className="text-[10px] text-emerald-400 mt-1 inline-block">Within loaded application feed</span>
          </div>
          <div className="p-3 bg-neutral-800/80 rounded-lg text-amber-400">
            <TrendingUp size={22} />
          </div>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div className="bg-neutral-900/60 rounded-xl border border-neutral-800 p-6 space-y-4">
        <div className="flex justify-between items-center border-b border-neutral-800 pb-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Clock size={16} className="text-emerald-400" /> Recent Applications (Latest 10)
          </h2>
          <Link href="/applications" className="text-xs text-emerald-400 hover:underline flex items-center gap-1 font-medium">
            View All Applications <ArrowRight size={12} />
          </Link>
        </div>

        {loading ? (
          <div className="py-8 text-center text-xs text-neutral-500">Loading applications...</div>
        ) : recentActivities.length === 0 ? (
          <div className="py-8 text-center text-xs text-neutral-500">{applications === null ? 'Application data is unavailable.' : 'No applications yet. Search jobs to get started.'}</div>
        ) : (
          <div className="divide-y divide-neutral-800/50">
            {recentActivities.map((act) => (
              <div key={act.id} className="py-3 flex justify-between items-center">
                <div className="space-y-0.5">
                  <div className="text-sm font-semibold text-white flex items-center gap-2">
                    {act.role || 'Role unavailable'} <span className="text-neutral-400 font-normal">at</span> {act.company || 'Company unavailable'}
                  </div>
                  <div className="text-[11px] text-neutral-500 flex items-center gap-2">
                    <span>Timestamp: {(act.submitted_at || act.applied_at || act.created_at) ? new Date(act.submitted_at || act.applied_at || act.created_at!).toLocaleString() : 'Unavailable'}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isVerifiedSubmission(act.status) ? (
                    <span className="px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-semibold flex items-center gap-1">
                      <CheckCircle2 size={10} /> Verified submission
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 rounded-full bg-neutral-800 text-neutral-400 border border-neutral-700 text-[10px] font-semibold">
                      {act.status || 'Unknown status'}
                    </span>
                  )}
                  <Link
                    href={`/applications/${act.id}`}
                    className="px-2.5 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-[11px] font-medium"
                  >
                    Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
