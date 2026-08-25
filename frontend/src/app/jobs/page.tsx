'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Search, 
  Briefcase, 
  MapPin, 
  Target, 
  ArrowRight, 
  Building2,
  ShieldCheck
} from 'lucide-react';

export default function JobsFeedPage() {
  const [query, setQuery] = useState('Data Engineer');
  const [indiaOnly, setIndiaOnly] = useState(true);
  const [jobs, setJobs] = useState<any[]>([]);
  const [sourceHealth, setSourceHealth] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchSourceHealth();
  }, [indiaOnly]);

  async function fetchSourceHealth() {
    try {
      const res = await fetch('http://localhost:8000/api/v1/jobs/source-health');
      if (res.ok) {
        const data = await res.json();
        setSourceHealth(data);
      }
    } catch (err) {
      console.error('Failed to fetch source health telemetry:', err);
    }
  }

  async function fetchJobs() {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/jobs/discover?query=${encodeURIComponent(query)}&india_only=${indiaOnly}`);
      if (res.ok) {
        const data = await res.json();
        setJobs(data);
      }
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      
      {/* Header */}
      <div className="border-b border-neutral-800 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            Authentic Job Discovery Feed <Briefcase size={20} className="text-emerald-400" />
          </h1>
          <p className="text-xs text-neutral-400 mt-1">
            Explore real live listings directly from company ATS endpoints and candidate browser sessions.
          </p>
        </div>
      </div>

      {/* Source Health Indicator Strip */}
      <div className="bg-neutral-900/60 p-4 rounded-xl border border-neutral-800 space-y-2">
        <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-wider block">Live Job Source Health Telemetry</span>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {sourceHealth.map((src, idx) => (
            <div key={idx} className="p-2.5 bg-neutral-950 rounded-lg border border-neutral-800 flex flex-col gap-1">
              <div className="flex justify-between items-center text-xs font-semibold text-white">
                <span>{src.name}</span>
              </div>
              <span className="text-[10px] font-medium text-emerald-400">{src.badge}</span>
              <span className="text-[9px] text-neutral-500">{src.reliability}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3 bg-neutral-900/60 p-4 rounded-xl border border-neutral-800">
        <div className="relative flex-1 w-full">
          <Search size={16} className="absolute left-3 top-3 text-neutral-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search target role (e.g. Data Engineer, Python Developer)..."
            className="w-full pl-9 pr-4 py-2 bg-neutral-950 border border-neutral-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Location Filter Toggle */}
        <button
          onClick={() => setIndiaOnly(!indiaOnly)}
          className={`px-3 py-2 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-all ${
            indiaOnly 
              ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300' 
              : 'bg-neutral-950 border-neutral-800 text-neutral-400 hover:text-white'
          }`}
        >
          <MapPin size={14} className={indiaOnly ? 'text-emerald-400' : 'text-neutral-500'} />
          {indiaOnly ? '🇮🇳 India Jobs Only' : '🌐 Global Jobs'}
        </button>

        <button
          onClick={fetchJobs}
          className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition-all flex items-center justify-center gap-1.5 w-full sm:w-auto"
        >
          <Search size={14} /> Search Live Jobs
        </button>
      </div>

      {/* Jobs List Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-neutral-500">Querying authentic live job sources...</div>
        ) : jobs.length === 0 ? (
          <div className="py-12 text-center text-xs text-neutral-500">No job listings found for "{query}".</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job, idx) => (
              <div key={job.id || idx} className="bg-neutral-900/60 p-5 rounded-xl border border-neutral-800 hover:border-neutral-700 transition-all flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <h3 className="text-sm font-bold text-white hover:text-emerald-400 transition">{job.title}</h3>
                    <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[9px] font-bold">
                      REAL DATA
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-xs text-neutral-400">
                    <span className="flex items-center gap-1"><Building2 size={12} className="text-neutral-500" /> {job.company}</span>
                    <span className="flex items-center gap-1"><MapPin size={12} className="text-neutral-500" /> {job.location || 'India'}</span>
                  </div>

                  <p className="text-xs text-neutral-400 line-clamp-2 leading-relaxed">
                    {job.description}
                  </p>

                  {/* Skills & AI Tailoring Breakdown */}
                  {job.matched_skills && job.matched_skills.length > 0 && (
                    <div className="pt-2 flex flex-wrap gap-1 items-center">
                      <span className="text-[10px] text-neutral-500 font-semibold mr-1">Matched:</span>
                      {job.matched_skills.slice(0, 3).map((sk: string, i: number) => (
                        <span key={i} className="px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 text-[9px] border border-emerald-900 font-mono">
                          {sk}
                        </span>
                      ))}
                      {job.missing_skills && job.missing_skills.length > 0 && (
                        <>
                          <span className="text-[10px] text-neutral-500 font-semibold mx-1">Missing:</span>
                          {job.missing_skills.slice(0, 2).map((sk: string, i: number) => (
                            <span key={i} className="px-1.5 py-0.5 rounded bg-amber-950/80 text-amber-400 text-[9px] border border-amber-900 font-mono">
                              {sk}
                            </span>
                          ))}
                        </>
                      )}
                    </div>
                  )}
                </div>

                <div className="flex justify-between items-center border-t border-neutral-800/60 pt-3">
                  <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                    <Target size={14} /> ATS Match: {job.match_score ? `${job.match_score}%` : 'Calculate...'}
                  </div>

                  {/* Honest UX Rule: No Quick Apply button! Only View & Prepare Application */}
                  <Link
                    href={`/jobs/${job.id || idx}?title=${encodeURIComponent(job.title)}&company=${encodeURIComponent(job.company)}&url=${encodeURIComponent(job.source_url || '')}`}
                    className="px-3.5 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-white font-medium text-xs border border-neutral-700 transition flex items-center gap-1"
                  >
                    View & Prepare <ArrowRight size={12} />
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
