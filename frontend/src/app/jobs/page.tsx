'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { 
  Search, 
  Briefcase, 
  MapPin, 
  Target, 
  ArrowRight, 
  Building2,
  Filter,
  SlidersHorizontal,
  X,
  RotateCcw,
  Sparkles
} from 'lucide-react';

export default function JobsFeedPage() {
  const [query, setQuery] = useState('Data Engineer');
  const [indiaOnly, setIndiaOnly] = useState(true);
  const [jobs, setJobs] = useState<any[]>([]);
  const [sourceHealth, setSourceHealth] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilterDrawer, setShowFilterDrawer] = useState(false);

  // Advanced Filter States
  const [selectedJobRole, setSelectedJobRole] = useState<string>('ALL');
  const [selectedCity, setSelectedCity] = useState<string>('ALL');
  const [selectedExperience, setSelectedExperience] = useState<string>('ALL');
  const [minMatchScore, setMinMatchScore] = useState<number>(0);
  const [selectedSource, setSelectedSource] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<string>('MATCH_DESC');

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

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (selectedJobRole !== 'ALL') count++;
    if (selectedCity !== 'ALL') count++;
    if (selectedExperience !== 'ALL') count++;
    if (minMatchScore > 0) count++;
    if (selectedSource !== 'ALL') count++;
    return count;
  }, [selectedJobRole, selectedCity, selectedExperience, minMatchScore, selectedSource]);

  function resetFilters() {
    setSelectedJobRole('ALL');
    setSelectedCity('ALL');
    setSelectedExperience('ALL');
    setMinMatchScore(0);
    setSelectedSource('ALL');
    setSortBy('MATCH_DESC');
  }

  // Filtered and Sorted Jobs Computation
  const filteredJobs = useMemo(() => {
    return jobs
      .filter((j) => {
        const title = (j.title || '').toLowerCase();
        const desc = (j.description || '').toLowerCase();

        // Job Role / Function Filter
        if (selectedJobRole !== 'ALL') {
          if (selectedJobRole === 'DATA_ENGINEER' && (!title.includes('data') && !title.includes('etl') && !title.includes('analytics'))) return false;
          if (selectedJobRole === 'BACKEND' && (!title.includes('backend') && !title.includes('system') && !title.includes('software engineer') && !title.includes('engineer') && !title.includes('developer'))) return false;
          if (selectedJobRole === 'AI_ML' && (!title.includes('ai') && !title.includes('ml') && !title.includes('machine learning') && !desc.includes('machine learning'))) return false;
          if (selectedJobRole === 'FULLSTACK_FRONTEND' && (!title.includes('frontend') && !title.includes('fullstack') && !title.includes('react') && !title.includes('web'))) return false;
          if (selectedJobRole === 'DEVOPS_CLOUD' && (!title.includes('devops') && !title.includes('cloud') && !title.includes('infra') && !title.includes('sre'))) return false;
          if (selectedJobRole === 'SECURITY' && (!title.includes('security') && !title.includes('audit') && !title.includes('compliance'))) return false;
          if (selectedJobRole === 'PRODUCT_MANAGER' && (!title.includes('product') && !title.includes('manager') && !title.includes('lead'))) return false;
        }

        // City / Region Filter
        if (selectedCity !== 'ALL') {
          const loc = (j.location || '').toLowerCase();
          if (selectedCity === 'REMOTE' && !loc.includes('remote')) return false;
          if (selectedCity === 'BENGALURU' && !loc.includes('bengaluru') && !loc.includes('bangalore')) return false;
          if (selectedCity === 'MUMBAI' && !loc.includes('mumbai')) return false;
          if (selectedCity === 'DELHI' && !loc.includes('delhi') && !loc.includes('noida') && !loc.includes('gurgaon')) return false;
          if (selectedCity === 'PUNE' && !loc.includes('pune')) return false;
          if (selectedCity === 'HYDERABAD' && !loc.includes('hyderabad')) return false;
        }

        // Experience Level Filter
        if (selectedExperience !== 'ALL') {
          if (selectedExperience === 'ENTRY' && (!title.includes('intern') && !title.includes('junior') && !title.includes('associate'))) return false;
          if (selectedExperience === 'MID' && (title.includes('senior') || title.includes('lead') || title.includes('principal') || title.includes('manager'))) return false;
          if (selectedExperience === 'SENIOR' && (!title.includes('senior') && !title.includes('lead') && !title.includes('principal') && !title.includes('manager'))) return false;
        }

        // Min Match Score Filter
        if (minMatchScore > 0 && (j.match_score || 0) < minMatchScore) {
          return false;
        }

        // Source Filter
        if (selectedSource !== 'ALL') {
          const src = (j.source || '').toLowerCase();
          if (selectedSource === 'COMPANY' && src !== 'company') return false;
          if (selectedSource === 'NAUKRI' && src !== 'naukri') return false;
          if (selectedSource === 'LINKEDIN' && src !== 'linkedin') return false;
          if (selectedSource === 'INDEED' && src !== 'indeed') return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'MATCH_DESC') return (b.match_score || 0) - (a.match_score || 0);
        if (sortBy === 'TITLE_ASC') return (a.title || '').localeCompare(b.title || '');
        if (sortBy === 'COMPANY_ASC') return (a.company || '').localeCompare(b.company || '');
        return 0;
      });
  }, [jobs, selectedJobRole, selectedCity, selectedExperience, minMatchScore, selectedSource, sortBy]);

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

      {/* Search & Main Filter Controls Bar */}
      <div className="space-y-3 bg-neutral-900/60 p-4 rounded-xl border border-neutral-800">
        <div className="flex flex-col sm:flex-row items-center gap-3">
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
            className={`px-3 py-2 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              indiaOnly 
                ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300' 
                : 'bg-neutral-950 border-neutral-800 text-neutral-400 hover:text-white'
            }`}
          >
            <MapPin size={14} className={indiaOnly ? 'text-emerald-400' : 'text-neutral-500'} />
            {indiaOnly ? '🇮🇳 India Jobs' : '🌐 Global Jobs'}
          </button>

          {/* Filter Drawer Trigger Button */}
          <button
            onClick={() => setShowFilterDrawer(!showFilterDrawer)}
            className={`px-3.5 py-2 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeFiltersCount > 0 || showFilterDrawer
                ? 'bg-neutral-800 border-emerald-500 text-emerald-400'
                : 'bg-neutral-950 border-neutral-800 text-neutral-300 hover:border-neutral-700'
            }`}
          >
            <SlidersHorizontal size={14} />
            Filters {activeFiltersCount > 0 && <span className="px-1.5 py-0.2 rounded-full bg-emerald-500 text-black text-[10px] font-bold">{activeFiltersCount}</span>}
          </button>

          <button
            onClick={fetchJobs}
            className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg transition-all flex items-center justify-center gap-1.5 w-full sm:w-auto"
          >
            <Search size={14} /> Search Live Jobs
          </button>
        </div>

        {/* Expandable Advanced Filter Panel */}
        {showFilterDrawer && (
          <div className="pt-3 border-t border-neutral-800/80 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 animate-in fade-in slide-in-from-top-2 duration-200">
            
            {/* Job Role Category Filter */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider block">Job Role Category</label>
              <select
                value={selectedJobRole}
                onChange={(e) => setSelectedJobRole(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="ALL">All Job Roles</option>
                <option value="DATA_ENGINEER">Data Engineer / Analytics</option>
                <option value="BACKEND">Backend & System Engineer</option>
                <option value="AI_ML">AI / ML / LLM Specialist</option>
                <option value="FULLSTACK_FRONTEND">Fullstack & Frontend Dev</option>
                <option value="DEVOPS_CLOUD">DevOps / Cloud / SRE</option>
                <option value="SECURITY">Security & Compliance</option>
                <option value="PRODUCT_MANAGER">Product & Project Lead</option>
              </select>
            </div>

            {/* City / Location Filter */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider block">City / Work Mode</label>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="ALL">All Locations / Cities</option>
                <option value="REMOTE">Remote Work Only</option>
                <option value="BENGALURU">Bengaluru / Bangalore</option>
                <option value="MUMBAI">Mumbai / Thane</option>
                <option value="DELHI">Delhi NCR / Noida / Gurgaon</option>
                <option value="PUNE">Pune</option>
                <option value="HYDERABAD">Hyderabad</option>
              </select>
            </div>

            {/* Experience Level Filter */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider block">Seniority / Experience</label>
              <select
                value={selectedExperience}
                onChange={(e) => setSelectedExperience(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="ALL">All Experience Levels</option>
                <option value="ENTRY">Entry Level / Internship</option>
                <option value="MID">Mid Level (2-5 Yrs)</option>
                <option value="SENIOR">Senior / Lead (5+ Yrs)</option>
              </select>
            </div>

            {/* Minimum ATS Match Score */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider block">Min ATS Score</label>
              <select
                value={minMatchScore}
                onChange={(e) => setMinMatchScore(Number(e.target.value))}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-emerald-500"
              >
                <option value={0}>All Match Scores (0%+)</option>
                <option value={70}>70%+ High Match</option>
                <option value={80}>80%+ Strong Match</option>
                <option value={90}>90%+ Perfect Match</option>
              </select>
            </div>

            {/* Sort Order */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider block">Sort Listings By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="MATCH_DESC">ATS Match Score (Highest First)</option>
                <option value="TITLE_ASC">Role Title (A-Z)</option>
                <option value="COMPANY_ASC">Company Name (A-Z)</option>
              </select>
            </div>

            {/* Reset Button */}
            {activeFiltersCount > 0 && (
              <div className="col-span-full flex justify-end">
                <button
                  onClick={resetFilters}
                  className="text-[11px] font-semibold text-neutral-400 hover:text-amber-400 flex items-center gap-1 transition"
                >
                  <RotateCcw size={12} /> Reset All Filters
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Results Header Info Bar */}
      <div className="flex justify-between items-center px-1 text-xs text-neutral-400 font-medium">
        <span>Showing <strong className="text-white">{filteredJobs.length}</strong> live job opportunities</span>
        {activeFiltersCount > 0 && (
          <span className="text-[11px] text-emerald-400 flex items-center gap-1 font-semibold">
            <Sparkles size={12} /> {activeFiltersCount} Active Filters Applied
          </span>
        )}
      </div>

      {/* Jobs List Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="py-12 text-center text-xs text-neutral-500">Querying authentic live job sources...</div>
        ) : filteredJobs.length === 0 ? (
          <div className="py-12 text-center text-xs text-neutral-500 space-y-2">
            <div>No job listings match your current filters.</div>
            {activeFiltersCount > 0 && (
              <button onClick={resetFilters} className="text-emerald-400 underline font-semibold">
                Reset filters to view all jobs
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredJobs.map((job, idx) => (
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
