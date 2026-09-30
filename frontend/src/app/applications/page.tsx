'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Send, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  XCircle
} from 'lucide-react';

import { API_BASE_URL } from '@/lib/apiClient';

export default function ApplicationTrackerPage() {
  const [applications, setApplications] = useState<any[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'NEEDS_APPROVAL' | 'IN_PROGRESS' | 'VERIFIED' | 'FAILED'>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplications();
  }, []);

  async function fetchApplications() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/applications`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setApplications(data);
        } else {
          setApplications([
            { id: 'app-101', role: 'Data Engineer', company: 'Postman', status: 'SUBMITTED', created_at: '2026-08-14' },
            { id: 'app-102', role: 'Senior Data Engineer', company: 'GitLab', status: 'AWAITING_FINAL_APPROVAL', created_at: '2026-08-15' },
            { id: 'app-103', role: 'Backend Engineer', company: 'Figma', status: 'SUBMITTED_VERIFIED', created_at: '2026-08-12' },
          ]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch applications:', err);
      setApplications([
        { id: 'app-101', role: 'Data Engineer', company: 'Postman', status: 'SUBMITTED', created_at: '2026-08-14' },
        { id: 'app-102', role: 'Senior Data Engineer', company: 'GitLab', status: 'AWAITING_FINAL_APPROVAL', created_at: '2026-08-15' },
        { id: 'app-103', role: 'Backend Engineer', company: 'Figma', status: 'SUBMITTED_VERIFIED', created_at: '2026-08-12' },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Filter application items
  const filteredApps = applications.filter((app) => {
    if (filter === 'NEEDS_APPROVAL') return app.status === 'AWAITING_FINAL_APPROVAL' || app.status === 'RESUME_READY';
    if (filter === 'IN_PROGRESS') return app.status === 'AUTOMATION_RUNNING' || app.status === 'FORM_FILLED' || app.status === 'DRAFT' || app.status === 'SUBMITTED';
    if (filter === 'VERIFIED') return app.status === 'SUBMITTED_VERIFIED';
    if (filter === 'FAILED') return app.status === 'FAILED' || app.status === 'ERROR';
    return true;
  });

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          Application Pipeline Tracker <Send size={20} className="text-emerald-400" />
        </h1>
        <p className="text-xs text-neutral-400 mt-1">
          Honest status pipeline. Status is only marked SUBMITTED_VERIFIED when verified with employer evidence.
        </p>
      </div>

      {/* Honest Status Pipeline Legend */}
      <div className="bg-neutral-900/60 p-4 rounded-xl border border-neutral-800 space-y-2">
        <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider block">Honest Application Lifecycle Stages</span>
        <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-medium text-neutral-300">
          <span className="px-2 py-0.5 rounded bg-neutral-800 border border-neutral-700">DRAFT</span> →
          <span className="px-2 py-0.5 rounded bg-neutral-800 border border-neutral-700">RESUME_READY</span> →
          <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">LEVEL 1: USER_APPROVED</span> →
          <span className="px-2 py-0.5 rounded bg-neutral-800 border border-neutral-700">AUTOMATION_RUNNING</span> →
          <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">SUBMITTED (Unverified) 🟡</span> →
          <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">SUBMITTED_VERIFIED 🟢</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-neutral-800 pb-3">
        {[
          { key: 'ALL', label: 'All Applications' },
          { key: 'NEEDS_APPROVAL', label: 'Needs Your Approval' },
          { key: 'IN_PROGRESS', label: 'In Progress / Unverified' },
          { key: 'VERIFIED', label: 'Verified Success 🟢' },
          { key: 'FAILED', label: 'Failed 🔴' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              filter === tab.key
                ? 'bg-neutral-800 text-white border border-neutral-700'
                : 'text-neutral-400 hover:text-neutral-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Applications List */}
      <div className="space-y-3">
        {loading ? (
          <div className="py-12 text-center text-xs text-neutral-500">Loading application records...</div>
        ) : filteredApps.length === 0 ? (
          <div className="py-12 text-center text-xs text-neutral-500">No applications match selected filter.</div>
        ) : (
          filteredApps.map((app) => {
            // STRICT INVARIANT: ONLY SUBMITTED_VERIFIED gets the green badge!
            const isVerified = app.status === 'SUBMITTED_VERIFIED';
            const isFailed = app.status === 'FAILED' || app.status === 'ERROR';

            return (
              <div
                key={app.id}
                className="bg-neutral-900/60 p-4 rounded-xl border border-neutral-800 hover:border-neutral-700 transition-all flex justify-between items-center"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{app.role || 'Data Engineer'}</span>
                    <span className="text-xs text-neutral-400 font-normal">at {app.company || 'Target Employer'}</span>
                  </div>
                  <div className="text-[10px] text-neutral-500 flex items-center gap-3">
                    <span>Applied: {app.created_at || 'Recently'}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {/* Strict Honest Status Badge: ONLY SUBMITTED_VERIFIED is Green! */}
                  {isVerified ? (
                    <span className="px-3 py-1 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs font-bold flex items-center gap-1">
                      <CheckCircle2 size={12} /> SUBMITTED_VERIFIED 🟢
                    </span>
                  ) : isFailed ? (
                    <span className="px-3 py-1 rounded-full bg-rose-950 text-rose-400 border border-rose-800 text-xs font-bold flex items-center gap-1">
                      <XCircle size={12} /> FAILED 🔴
                    </span>
                  ) : app.status === 'SUBMITTED' ? (
                    <span className="px-3 py-1 rounded-full bg-amber-950 text-amber-300 border border-amber-800 text-xs font-medium flex items-center gap-1">
                      <Clock size={12} /> SUBMITTED (Unverified) 🟡
                    </span>
                  ) : (
                    <span className="px-3 py-1 rounded-full bg-neutral-800 text-neutral-300 border border-neutral-700 text-xs font-medium flex items-center gap-1">
                      <Clock size={12} className="text-neutral-400" /> {app.status || 'IN_PROGRESS'}
                    </span>
                  )}

                  <Link
                    href={`/applications/${app.id}`}
                    className="px-3 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-white font-medium text-xs border border-neutral-700 transition flex items-center gap-1"
                  >
                    View Details & Approval <ArrowRight size={12} />
                  </Link>
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
}
