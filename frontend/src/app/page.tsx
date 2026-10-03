'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import JobStepNavbar from '../components/JobStepNavbar';
import { 
  ArrowRight, 
  Star, 
  Sparkles, 
  CheckCircle2, 
  ShieldCheck, 
  Play, 
  Upload, 
  FileText, 
  Building2, 
  MapPin, 
  Send, 
  Layers, 
  Check, 
  Sliders, 
  Zap,
  LayoutDashboard
} from 'lucide-react';

export default function JobStepLandingPage() {
  // Darkest Obsidian theme by default
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Step 1 Resume Optimizer Interactive Demo State
  const [isOptimized, setIsOptimized] = useState(false);
  const [activeJobModal, setActiveJobModal] = useState<any | null>(null);

  const weeklyJobs = [
    {
      id: 'linear-1',
      company: 'Linear',
      role: 'Senior Product Desig...',
      fullRole: 'Senior Product Designer',
      location: 'Remote - EU',
      matchScore: 96,
      isTop: true,
      scoreColorDark: 'text-emerald-400 bg-emerald-950/60 border-emerald-800',
      scoreColorLight: 'text-[#059669] bg-[#ecfdf5] border-[#a7f3d0]',
      logoBg: 'bg-gradient-to-tr from-purple-700 to-indigo-500',
      logoText: 'L',
      skills: ['Figma', 'Design Systems', 'React', 'Product Strategy']
    },
    {
      id: 'spotify-1',
      company: 'Spotify',
      role: 'Design Lead',
      fullRole: 'Design Lead (Personalization)',
      location: 'Berlin',
      matchScore: 94,
      isTop: true,
      scoreColorDark: 'text-emerald-400 bg-emerald-950/60 border-emerald-800',
      scoreColorLight: 'text-[#059669] bg-[#ecfdf5] border-[#a7f3d0]',
      logoBg: 'bg-[#1ed760]',
      logoText: 'S',
      skills: ['UX Leadership', 'Music Tech', 'User Research', 'Figma']
    },
    {
      id: 'sap-1',
      company: 'SAP',
      role: 'Staff Product Designer',
      fullRole: 'Staff Product Designer (Enterprise UX)',
      location: 'Walldorf',
      matchScore: 92,
      isTop: true,
      scoreColorDark: 'text-emerald-400 bg-emerald-950/60 border-emerald-800',
      scoreColorLight: 'text-[#059669] bg-[#ecfdf5] border-[#a7f3d0]',
      logoBg: 'bg-[#0070f2]',
      logoText: 'SAP',
      skills: ['Enterprise SaaS', 'Design Systems', 'Accessibility', 'Prototyping']
    },
    {
      id: 'bmw-1',
      company: 'BMW Group',
      role: 'Senior UX Designer',
      fullRole: 'Senior UX Designer (In-Car Telematics)',
      location: 'Munich',
      matchScore: 89,
      isTop: false,
      scoreColorDark: 'text-amber-400 bg-amber-950/60 border-amber-800',
      scoreColorLight: 'text-[#d97706] bg-[#fffbeb] border-[#fde68a]',
      logoBg: 'bg-[#0066b1]',
      logoText: 'BMW',
      skills: ['HMI Design', 'Automotive UX', 'Voice UI', 'Figma']
    }
  ];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      isDarkMode 
        ? 'bg-[#070709] text-neutral-100 selection:bg-orange-500/30' 
        : 'bg-[#fff8f5] text-neutral-900 selection:bg-orange-200'
    }`}>
      
      {/* Hero Section */}
      <section className="relative pt-12 pb-20 px-4 max-w-6xl mx-auto flex flex-col items-center text-center">
        
        {/* Deep Glowing Ambient Aura */}
        <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-96 blur-3xl pointer-events-none -z-10 transition-opacity duration-500 ${
          isDarkMode 
            ? 'bg-gradient-to-b from-orange-500/15 via-purple-600/10 to-transparent opacity-80' 
            : 'bg-gradient-to-b from-orange-200/30 via-orange-100/10 to-transparent'
        }`} />

        {/* Trustpilot Social Proof Badge */}
        <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-8 transition-colors duration-200 shadow-sm ${
          isDarkMode 
            ? 'bg-[#111116]/90 border border-neutral-800 text-neutral-300' 
            : 'bg-white/95 border border-gray-200 text-neutral-700 shadow-[0_1px_4px_rgba(0,0,0,0.04)]'
        }`}>
          <span className={`font-semibold ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Excellent</span>
          <span>4.7 out of 5</span>
          <div className="flex items-center text-emerald-500 font-bold gap-0.5">
            <span className="font-extrabold text-sm">★</span>
            <span className="font-bold">Trustpilot</span>
          </div>
          <span className={isDarkMode ? 'text-neutral-600' : 'text-neutral-300'}>•</span>
          <span className={`font-normal ${isDarkMode ? 'text-neutral-400' : 'text-neutral-600'}`}>120,000+ CareerOS users</span>
        </div>

        {/* Big Bold Headline */}
        <h1 className={`text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.12] max-w-4xl ${
          isDarkMode ? 'text-white' : 'text-neutral-900'
        }`}>
          You apply. You wait. <br />
          <span className="relative inline-block mt-1 sm:mt-2">
            <span className={`absolute inset-0 rounded-2xl transform -rotate-0.5 scale-y-95 scale-x-105 -z-10 transition-all ${
              isDarkMode 
                ? 'bg-gradient-to-r from-orange-500/25 via-amber-500/30 to-orange-500/25 border border-orange-500/50 shadow-lg shadow-orange-950/40' 
                : 'bg-[#fed7aa] shadow-xs'
            }`} />
            <span className={`relative px-3.5 ${isDarkMode ? 'text-orange-200' : 'text-neutral-950'}`}>
              You hear nothing.
            </span>
          </span>
        </h1>

        {/* Subtitle */}
        <p className={`mt-6 text-lg sm:text-xl max-w-2xl font-normal leading-relaxed ${
          isDarkMode ? 'text-neutral-400' : 'text-neutral-600'
        }`}>
          CareerOS improves your resume, finds matching jobs, and tailors your application documents to each role. Users get 3× more replies on average.
        </p>

        {/* Primary CTA Button */}
        <div className="mt-8 flex flex-col sm:flex-row items-center gap-4">
          <Link
            href="/resume"
            className="px-8 py-4 rounded-full bg-[#eb5a28] hover:bg-[#d94e1d] text-white text-base sm:text-lg font-bold shadow-xl shadow-orange-950/50 transition-all transform hover:-translate-y-0.5 active:scale-95 flex items-center gap-2.5"
          >
            <span>Get started</span>
            <ArrowRight size={18} />
          </Link>
        </div>

        {/* STEP 1: Interactive Browser Mockup Window */}
        <div id="step1" className={`w-full max-w-4xl mt-14 rounded-2xl overflow-hidden text-left transition-all ${
          isDarkMode 
            ? 'bg-[#0d0d12] border border-neutral-800 shadow-[0_25px_80px_rgba(0,0,0,0.9)]' 
            : 'bg-white border border-gray-200/90 shadow-2xl'
        }`}>
          
          {/* macOS Browser Bar */}
          <div className={`px-4 py-3 flex items-center justify-between border-b ${
            isDarkMode 
              ? 'bg-[#09090d] border-neutral-800' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-[#ff5f56] inline-block border border-red-400/30" />
              <span className="w-3 h-3 rounded-full bg-[#ffbd2e] inline-block border border-yellow-400/30" />
              <span className="w-3 h-3 rounded-full bg-[#27c93f] inline-block border border-green-400/30" />
            </div>

            {/* Address Pill */}
            <div className={`rounded-full px-5 py-1 text-xs font-mono flex items-center gap-1.5 shadow-xs border ${
              isDarkMode 
                ? 'bg-[#14141b] border-neutral-800 text-neutral-400' 
                : 'bg-white border-gray-200/80 text-neutral-500'
            }`}>
              <span className="text-neutral-400">🔒</span>
              <span>app.careeros.io</span>
            </div>

            <div className="w-12" />
          </div>

          {/* Browser Content Area */}
          <div className={`p-6 sm:p-10 flex flex-col items-center text-center ${
            isDarkMode ? 'bg-[#0b0b10]' : 'bg-white'
          }`}>
            
            <div className="text-[#eb5a28] text-xs font-bold tracking-widest uppercase mb-1">
              STEP 1
            </div>

            <h2 className={`text-3xl sm:text-4xl font-extrabold tracking-tight ${
              isDarkMode ? 'text-white' : 'text-neutral-900'
            }`}>
              Optimize your resume
            </h2>

            {/* Interactive CV Score Gauge */}
            <div className={`mt-8 flex flex-col sm:flex-row items-center justify-center gap-8 w-full max-w-xl p-6 rounded-2xl border transition-colors ${
              isDarkMode 
                ? 'bg-[#111117] border-neutral-800 shadow-md' 
                : 'bg-gray-50/80 border-gray-200/70'
            }`}>
              
              {/* Circular Gauge */}
              <div className="relative w-28 h-28 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                    stroke={isDarkMode ? "#22222a" : "#e5e7eb"}
                    strokeWidth="8"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                    stroke={isOptimized ? "#10b981" : "#f59e0b"}
                    strokeWidth="8"
                    strokeDasharray="251.2"
                    strokeDashoffset={isOptimized ? "15" : "120"}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                </svg>

                <div className="absolute flex flex-col items-center justify-center text-center">
                  <span className={`text-3xl font-extrabold transition-colors ${
                    isOptimized ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {isOptimized ? '94' : '52'}
                  </span>
                  <span className="text-[10px] uppercase font-bold text-neutral-500 -mt-1">
                    CV score
                  </span>
                  <span className={`text-[10px] font-bold ${
                    isOptimized ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {isOptimized ? 'Strong' : 'Weak'}
                  </span>
                </div>
              </div>

              {/* Optimization State Details */}
              <div className="text-left flex-1 space-y-2">
                <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wide">
                  {isOptimized ? 'AI Tailored & TruthGuard Verified' : 'Baseline Resume Analysis'}
                </div>

                <div className={`space-y-1.5 text-xs ${isDarkMode ? 'text-neutral-300' : 'text-neutral-700'}`}>
                  <div className="flex items-center gap-2">
                    <span className={isOptimized ? 'text-emerald-400 font-bold' : 'text-neutral-500'}>
                      {isOptimized ? '✓' : '•'}
                    </span>
                    <span>ATS Keyword Match: <strong className={isOptimized ? 'text-emerald-400' : (isDarkMode ? 'text-white' : 'text-neutral-800')}>{isOptimized ? '94%' : '52%'}</strong></span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={isOptimized ? 'text-emerald-400 font-bold' : 'text-neutral-500'}>
                      {isOptimized ? '✓' : '•'}
                    </span>
                    <span>Action Verbs Impact: <strong className={isOptimized ? 'text-emerald-400' : (isDarkMode ? 'text-white' : 'text-neutral-800')}>{isOptimized ? 'High (8/8 improved)' : 'Needs Improvement'}</strong></span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={isOptimized ? 'text-emerald-400 font-bold' : 'text-neutral-500'}>
                      {isOptimized ? '✓' : '•'}
                    </span>
                    <span>TruthGuard Safety: <strong className="text-emerald-400">Zero Hallucinations</strong></span>
                  </div>
                </div>

                {/* Interactive Toggle Button */}
                <button
                  onClick={() => setIsOptimized(!isOptimized)}
                  className={`mt-3 px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 ${
                    isOptimized 
                      ? 'bg-emerald-950/80 text-emerald-300 hover:bg-emerald-900 border border-emerald-800' 
                      : 'bg-[#eb5a28] text-white hover:bg-[#d94e1d]'
                  }`}
                >
                  <Sparkles size={14} />
                  <span>{isOptimized ? 'Reset Baseline' : 'Simulate 1-Click AI Boost'}</span>
                </button>
              </div>

            </div>

            {/* Quick Upload CTA Bar */}
            <div className={`mt-8 pt-6 border-t flex flex-col sm:flex-row items-center justify-between w-full gap-4 ${
              isDarkMode ? 'border-neutral-850' : 'border-gray-100'
            }`}>
              <div className="text-xs text-neutral-400 text-left">
                Supports PDF, DOCX • Powered by CareerOS TruthGuard
              </div>
              <Link
                href="/resume"
                className={`px-6 py-2.5 rounded-full text-xs font-bold flex items-center gap-2 shadow-sm transition ${
                  isDarkMode 
                    ? 'bg-white hover:bg-neutral-200 text-black' 
                    : 'bg-neutral-900 hover:bg-neutral-800 text-white'
                }`}
              >
                <Upload size={14} />
                <span>Upload your real resume</span>
              </Link>
            </div>

          </div>

        </div>

      </section>

      {/* 2. Section: AI Job Search */}
      <section id="jobs" className={`py-20 px-4 max-w-6xl mx-auto border-t ${
        isDarkMode ? 'border-neutral-850' : 'border-gray-200/60'
      }`}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          
          {/* Left Text Column */}
          <div>
            <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4 border ${
              isDarkMode 
                ? 'bg-orange-500/10 border-orange-500/30 text-orange-400' 
                : 'bg-orange-50 border-orange-200/80 text-[#eb5a28]'
            }`}>
              <Sparkles size={13} />
              <span>AI JOB SEARCH</span>
            </div>

            <h2 className={`text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight leading-[1.15] ${
              isDarkMode ? 'text-white' : 'text-neutral-900'
            }`}>
              Weekly job suggestions — handpicked by AI
            </h2>

            <p className={`mt-5 text-base sm:text-lg leading-relaxed ${
              isDarkMode ? 'text-neutral-400' : 'text-neutral-600'
            }`}>
              Our AI scans thousands of new jobs every week and surfaces the best matches — each scored against your resume so you know how well it fits.
            </p>

            <div className="mt-8 flex items-center gap-4">
              <Link
                href="/jobs"
                className="px-6 py-3 rounded-full bg-[#eb5a28] hover:bg-[#d94e1d] text-white text-sm font-bold shadow-md shadow-orange-950/40 transition flex items-center gap-2"
              >
                <span>Browse matching jobs</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>

          {/* Right Cards Column */}
          <div className={`rounded-2xl p-5 border space-y-3 transition-colors ${
            isDarkMode 
              ? 'bg-[#0d0d12] border-neutral-800 shadow-xl' 
              : 'bg-white border-gray-200/90 shadow-sm'
          }`}>
            {weeklyJobs.map((job) => (
              <div
                key={job.id}
                onClick={() => setActiveJobModal(job)}
                className={`p-3.5 rounded-xl border transition-all flex items-center justify-between cursor-pointer group ${
                  isDarkMode 
                    ? 'bg-[#121218] border-neutral-800/80 hover:border-orange-500/50 hover:bg-[#171720]' 
                    : 'bg-white border-gray-100 hover:border-orange-300 hover:shadow-md'
                }`}
              >
                
                {/* Left: Logo & Info */}
                <div className="flex items-center gap-3.5">
                  <div className={`w-10 h-10 rounded-xl ${job.logoBg} flex items-center justify-center text-white font-extrabold text-xs shadow-xs`}>
                    {job.logoText}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`font-bold text-sm transition ${
                        isDarkMode ? 'text-neutral-100 group-hover:text-orange-400' : 'text-neutral-900 group-hover:text-[#eb5a28]'
                      }`}>
                        {job.role}
                      </span>
                      {job.isTop && (
                        <span className="bg-[#10b981] text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded-full flex items-center gap-0.5">
                          <span>★</span> TOP
                        </span>
                      )}
                    </div>
                    <div className={`text-xs mt-0.5 ${isDarkMode ? 'text-neutral-400' : 'text-neutral-500'}`}>
                      {job.location}
                    </div>
                  </div>
                </div>

                {/* Right: Match Score Pill */}
                <div className="flex items-center gap-2">
                  <div className={`px-2.5 py-1 rounded-full text-xs font-extrabold border flex items-center gap-1.5 ${
                    isDarkMode ? job.scoreColorDark : job.scoreColorLight
                  }`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-current inline-block" />
                    <span>{job.matchScore}%</span>
                  </div>
                </div>

              </div>
            ))}
          </div>

        </div>
      </section>

      {/* 3. Section: Dashboard / Kanban Application Tracking */}
      <section className={`py-20 px-4 max-w-6xl mx-auto border-t ${
        isDarkMode ? 'border-neutral-850' : 'border-gray-200/60'
      }`}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          
          {/* Left Text Column */}
          <div>
            <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4 border ${
              isDarkMode 
                ? 'bg-orange-500/10 border-orange-500/30 text-orange-400' 
                : 'bg-orange-50 border-orange-200/80 text-[#eb5a28]'
            }`}>
              <Layers size={13} />
              <span>DASHBOARD</span>
            </div>

            <h2 className={`text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight leading-[1.15] ${
              isDarkMode ? 'text-white' : 'text-neutral-900'
            }`}>
              Track all your Jobs & Documents in one Place
            </h2>

            <p className={`mt-5 text-base sm:text-lg leading-relaxed ${
              isDarkMode ? 'text-neutral-400' : 'text-neutral-600'
            }`}>
              Keep your resumes, cover letters, and job applications organized in a single dashboard. No more scattered files and lost versions.
            </p>

            <div className="mt-8 flex items-center gap-4">
              <Link
                href="/applications"
                className={`px-6 py-3 rounded-full text-sm font-bold shadow-md transition flex items-center gap-2 ${
                  isDarkMode 
                    ? 'bg-neutral-800 hover:bg-neutral-700 text-white border border-neutral-700' 
                    : 'bg-neutral-900 hover:bg-neutral-800 text-white'
                }`}
              >
                <span>Open application tracker</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>

          {/* Right Kanban Preview Board */}
          <div className={`p-4 rounded-2xl border grid grid-cols-2 sm:grid-cols-3 gap-3 overflow-hidden ${
            isDarkMode 
              ? 'bg-[#09090d] border-neutral-800' 
              : 'bg-gray-100/70 border-gray-200/80 shadow-inner'
          }`}>
            
            {/* Column 1: PREPARATION */}
            <div className="space-y-2.5">
              <div className={`text-[11px] font-extrabold tracking-wider uppercase px-1 ${
                isDarkMode ? 'text-neutral-400' : 'text-neutral-700'
              }`}>
                PREPARATION
              </div>

              {/* Item 1: New Application */}
              <div className={`p-3 rounded-xl border shadow-xs space-y-1 relative ${
                isDarkMode ? 'bg-[#121218] border-neutral-800' : 'bg-white border-gray-200/90'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="w-7 h-7 rounded-lg bg-orange-500/20 text-[#eb5a28] font-bold text-xs flex items-center justify-center">
                    CO
                  </div>
                  <span className="bg-[#eb5a28] text-white text-[9px] font-extrabold px-1.5 py-0.5 rounded-full uppercase">
                    New
                  </span>
                </div>
                <div className={`font-bold text-xs mt-2 ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>New Application</div>
                <div className="text-[10px] text-neutral-400">CareerOS</div>
              </div>

              {/* Item 2: Spotify */}
              <div className={`p-3 rounded-xl border shadow-xs space-y-1 ${
                isDarkMode ? 'bg-[#121218] border-neutral-800' : 'bg-white border-gray-200/90'
              }`}>
                <div className="w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center">
                  S
                </div>
                <div className={`font-bold text-xs mt-2 ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Example Position 1</div>
                <div className="text-[10px] text-neutral-400">Spotify</div>
              </div>

              {/* Item 3: Netflix */}
              <div className={`p-3 rounded-xl border shadow-xs space-y-1 ${
                isDarkMode ? 'bg-[#121218] border-neutral-800' : 'bg-white border-gray-200/90'
              }`}>
                <div className="w-7 h-7 rounded-lg bg-red-500/20 text-red-400 font-bold text-xs flex items-center justify-center">
                  N
                </div>
                <div className={`font-bold text-xs mt-2 ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Example Position 2</div>
                <div className="text-[10px] text-neutral-400">Netflix</div>
              </div>
            </div>

            {/* Column 2: APPLIED */}
            <div className="space-y-2.5">
              <div className={`text-[11px] font-extrabold tracking-wider uppercase px-1 ${
                isDarkMode ? 'text-neutral-400' : 'text-neutral-700'
              }`}>
                APPLIED
              </div>

              {/* Item: Google */}
              <div className={`p-3 rounded-xl border shadow-xs space-y-1 ${
                isDarkMode ? 'bg-[#121218] border-neutral-800' : 'bg-white border-gray-200/90'
              }`}>
                <div className="w-7 h-7 rounded-lg bg-blue-500/20 text-blue-400 font-bold text-xs flex items-center justify-center">
                  G
                </div>
                <div className={`font-bold text-xs mt-2 ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Example Position 3</div>
                <div className="text-[10px] text-neutral-400">Google</div>
              </div>
            </div>

            {/* Column 3: INTERVIEW (Peek) */}
            <div className="hidden sm:block space-y-2.5 opacity-60">
              <div className={`text-[11px] font-extrabold tracking-wider uppercase px-1 ${
                isDarkMode ? 'text-neutral-400' : 'text-neutral-700'
              }`}>
                INTERVIEW
              </div>
              <div className={`border border-dashed rounded-xl p-4 text-center text-[10px] ${
                isDarkMode ? 'border-neutral-800 text-neutral-500' : 'border-gray-300 text-neutral-400'
              }`}>
                + In review
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* 4. Section: Testimonials & Social Proof */}
      <section className={`py-20 px-4 max-w-6xl mx-auto border-t ${
        isDarkMode ? 'border-neutral-850' : 'border-gray-200/60'
      }`}>
        
        {/* Floating Bubble Accent */}
        <div className="flex justify-center mb-8">
          <div className="relative inline-block">
            <div className="bg-[#eb5a28] text-white font-bold text-xs sm:text-sm px-5 py-2.5 rounded-2xl shadow-xl shadow-orange-950/50 flex items-center gap-2">
              <span>&ldquo;My response rate went from 2% to 40%&rdquo;</span>
            </div>
            {/* Triangle pointer */}
            <div className="w-3 h-3 bg-[#eb5a28] transform rotate-45 absolute -bottom-1.5 left-1/2 -translate-x-1/2" />
          </div>
        </div>

        {/* Masonry / Grid of Review Cards & Real Proofs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 items-start">
          
          {/* Column 1: Reviews & Before/After Card */}
          <div className="space-y-5">
            {/* Before / After Resume Comparison Preview */}
            <div className={`p-4 rounded-2xl border relative overflow-hidden group ${
              isDarkMode ? 'bg-[#0d0d12] border-neutral-800 shadow-md' : 'bg-white border-gray-200/90 shadow-xs'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <span className={`text-[11px] font-bold ${isDarkMode ? 'text-white' : 'text-neutral-800'}`}>
                  Resume Redesign Preview
                </span>
                <span className="text-[10px] text-neutral-500">7 weeks ago</span>
              </div>
              <div className={`relative rounded-xl p-3 flex items-center justify-center overflow-hidden ${
                isDarkMode ? 'bg-[#15151c]' : 'bg-neutral-100'
              }`}>
                <div className="flex gap-2 opacity-90 scale-95">
                  <div className={`w-24 h-32 rounded shadow-xs border p-2 text-[6px] space-y-1 ${
                    isDarkMode ? 'bg-[#0a0a0e] border-neutral-800 text-neutral-500' : 'bg-white border-gray-200 text-neutral-400'
                  }`}>
                    <div className="w-8 h-1.5 bg-red-400 rounded-xs mb-1" />
                    <div className={`h-1 rounded-xs ${isDarkMode ? 'bg-neutral-800' : 'bg-gray-200'}`} />
                    <div className={`h-1 rounded-xs ${isDarkMode ? 'bg-neutral-800' : 'bg-gray-200'}`} />
                    <div className={`h-1 rounded-xs ${isDarkMode ? 'bg-neutral-850' : 'bg-gray-100'}`} />
                  </div>
                  <div className={`w-24 h-32 rounded shadow-sm border p-2 text-[6px] space-y-1 ${
                    isDarkMode ? 'bg-[#0d1612] border-emerald-800/80 text-emerald-300' : 'bg-white border-emerald-300 text-neutral-600'
                  }`}>
                    <div className="w-10 h-1.5 bg-emerald-500 rounded-xs mb-1" />
                    <div className={`h-1 rounded-xs ${isDarkMode ? 'bg-emerald-950' : 'bg-emerald-100'}`} />
                    <div className={`h-1 rounded-xs ${isDarkMode ? 'bg-emerald-950' : 'bg-emerald-100'}`} />
                    <div className={`h-1 rounded-xs ${isDarkMode ? 'bg-neutral-800' : 'bg-gray-200'}`} />
                  </div>
                </div>
                {/* Play Button Overlay */}
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-[1px]">
                  <div className="w-10 h-10 rounded-full bg-[#eb5a28] flex items-center justify-center shadow-lg group-hover:scale-110 transition cursor-pointer">
                    <Play size={16} className="text-white fill-white ml-0.5" />
                  </div>
                </div>
              </div>
              <div className="text-[11px] text-neutral-400 font-medium text-center mt-2.5">
                Side-by-side ATS layout breakdown
              </div>
            </div>

            {/* Review: bharath P (Trustpilot) */}
            <div className={`p-5 rounded-2xl border space-y-3 ${
              isDarkMode ? 'bg-[#0d0d12] border-neutral-800 text-neutral-300' : 'bg-white border-gray-200/90 text-neutral-700'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex text-emerald-500 text-xs">★★★★★</div>
                <span className="text-[11px] text-neutral-500">2 weeks ago</span>
              </div>
              <p className="text-xs leading-relaxed font-normal">
                &ldquo;nice and very useful to me and nice to search jobs easy&rdquo;
              </p>
              <div className={`pt-2 border-t flex items-center justify-between ${
                isDarkMode ? 'border-neutral-850' : 'border-gray-100'
              }`}>
                <span className="text-xs font-bold text-emerald-400">★ Trustpilot</span>
                <span className={`text-xs font-bold ${isDarkMode ? 'text-white' : 'text-neutral-800'}`}>bharath P</span>
              </div>
            </div>

            {/* Review: Raghul tlv (Trustpilot) */}
            <div className={`p-5 rounded-2xl border space-y-3 ${
              isDarkMode ? 'bg-[#0d0d12] border-neutral-800 text-neutral-300' : 'bg-white border-gray-200/90 text-neutral-700'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex text-emerald-500 text-xs">★★★★★</div>
                <span className="text-[11px] text-neutral-500">2 weeks ago</span>
              </div>
              <p className="text-xs leading-relaxed font-normal">
                &ldquo;Its good to build resume and update with the help of AI. Thanks.&rdquo;
              </p>
              <div className={`pt-2 border-t flex items-center justify-between ${
                isDarkMode ? 'border-neutral-850' : 'border-gray-100'
              }`}>
                <span className="text-xs font-bold text-emerald-400">★ Trustpilot</span>
                <span className={`text-xs font-bold ${isDarkMode ? 'text-white' : 'text-neutral-800'}`}>Raghul tlv</span>
              </div>
            </div>
          </div>

          {/* Column 2: Alexander Weiss & Real Center Resume Document */}
          <div className="space-y-5">
            {/* Review: Alexander Weiss (Google) */}
            <div className={`p-5 rounded-2xl border space-y-3 ${
              isDarkMode ? 'bg-[#0d0d12] border-neutral-800 text-neutral-300' : 'bg-white border-gray-200/90 text-neutral-700'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex text-amber-400 text-xs">★★★★★</div>
                <span className="text-[11px] text-neutral-500">3 days ago</span>
              </div>
              <p className="text-xs leading-relaxed font-normal">
                &ldquo;The improvement to my resume made such a huge difference!! So happy to have found you!! Thank you! I can really recommend this to everyone!&rdquo;
              </p>
              <div className={`pt-2 border-t flex items-center justify-between ${
                isDarkMode ? 'border-neutral-850' : 'border-gray-100'
              }`}>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-blue-400">G</span>
                  <span className={`text-xs font-bold ${isDarkMode ? 'text-white' : 'text-neutral-800'}`}>Alexander Weiss</span>
                </div>
              </div>
            </div>

            {/* Real Resume Document Showcase */}
            <div className={`p-6 rounded-2xl border space-y-3 text-left ${
              isDarkMode ? 'bg-[#101016] border-neutral-800 shadow-xl' : 'bg-white border-gray-200/90 shadow-md'
            }`}>
              <div className={`border-b pb-2 ${isDarkMode ? 'border-neutral-800' : 'border-gray-100'}`}>
                <div className={`text-xs font-extrabold uppercase ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Sarah Lefevre</div>
                <div className="text-[10px] text-neutral-400">Assistante Administrative • Paris</div>
              </div>

              <div>
                <div className="text-[9px] font-extrabold text-neutral-500 uppercase tracking-wider mb-1">
                  EXPERIENCE PROFESSIONNELLE
                </div>
                <div className={`space-y-1 text-[9px] ${isDarkMode ? 'text-neutral-300' : 'text-neutral-700'}`}>
                  <div className={`font-semibold ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Assistante Administrative (Stage) — Solvus Services</div>
                  <div className="text-neutral-400 text-[8px]">• Optimisation de la planification des rendez-vous et réduction du temps de coordination de 35%</div>
                  <div className="text-neutral-400 text-[8px]">• Gestion de la conformité documentaire (Normes ISO)</div>
                </div>
              </div>

              <div>
                <div className="text-[9px] font-extrabold text-neutral-500 uppercase tracking-wider mb-1">
                  FORMATION
                </div>
                <div className={`space-y-0.5 text-[9px] ${isDarkMode ? 'text-neutral-300' : 'text-neutral-700'}`}>
                  <div className={`font-semibold ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>Licence Économie & Gestion — Université Paris</div>
                  <div className="text-neutral-400 text-[8px]">Spécialité : Communication d’entreprise & Administration</div>
                </div>
              </div>

              <div>
                <div className="text-[9px] font-extrabold text-neutral-500 uppercase tracking-wider mb-1">
                  COMPÉTENCES CLÉS
                </div>
                <div className="flex flex-wrap gap-1">
                  <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                    isDarkMode ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    Pack Office 365
                  </span>
                  <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                    isDarkMode ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    Google Analytics
                  </span>
                  <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                    isDarkMode ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    Notion
                  </span>
                  <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                    isDarkMode ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    Social Media
                  </span>
                </div>
              </div>

              <div className={`pt-2 border-t flex items-center justify-between text-[10px] font-bold ${
                isDarkMode ? 'border-neutral-800 text-emerald-400' : 'border-gray-100 text-emerald-600'
              }`}>
                <span className="flex items-center gap-1">
                  <ShieldCheck size={12} /> TruthGuard 100% Verified
                </span>
                <span>Score: 94/100</span>
              </div>
            </div>
          </div>

          {/* Column 3: Magda, Nina from NL Reel & Nico */}
          <div className="space-y-5">
            {/* Review: Magda (Trustpilot) */}
            <div className={`p-5 rounded-2xl border space-y-3 ${
              isDarkMode ? 'bg-[#0d0d12] border-neutral-800 text-neutral-300' : 'bg-white border-gray-200/90 text-neutral-700'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex text-emerald-500 text-xs">★★★★★</div>
                <span className="text-[11px] text-neutral-500">2 weeks ago</span>
              </div>
              <p className="text-xs leading-relaxed font-normal">
                &ldquo;The application process was simple, clear, and user-friendly. The platform made it easy to navigate through each step and provided helpful guidance...&rdquo;
              </p>
              <div className={`pt-2 border-t flex items-center justify-between ${
                isDarkMode ? 'border-neutral-850' : 'border-gray-100'
              }`}>
                <span className="text-xs font-bold text-emerald-400">★ Trustpilot</span>
                <span className={`text-xs font-bold ${isDarkMode ? 'text-white' : 'text-neutral-800'}`}>Magda</span>
              </div>
            </div>

            {/* Video Reel Preview (Nina from NL) */}
            <div className="bg-gradient-to-br from-[#121218] to-[#0a0a0f] text-white rounded-2xl p-5 border border-neutral-800 shadow-xl relative overflow-hidden flex flex-col justify-between min-h-[200px]">
              <div className="flex items-center justify-between z-10">
                <span className="bg-black/80 backdrop-blur-md text-[10px] font-bold px-2.5 py-1 rounded-full border border-white/10">
                  Nina from NL
                </span>
                <span className="text-[10px] text-neutral-400 font-medium">Reel</span>
              </div>

              <div className="flex flex-col items-center justify-center my-4 z-10">
                <div className="w-12 h-12 rounded-full bg-[#eb5a28] flex items-center justify-center shadow-lg shadow-orange-950/60 group-hover:scale-110 transition cursor-pointer">
                  <Play size={18} className="text-white fill-white ml-0.5" />
                </div>
                <span className="text-[11px] font-semibold text-neutral-200 mt-2 text-center max-w-[200px]">
                  Waarom heeft niemand me dit verteld?? 😭
                </span>
              </div>
              
              <div className="text-[10px] text-neutral-400 z-10 flex items-center justify-between">
                <span>Verified Candidate</span>
                <span>40k views</span>
              </div>
            </div>

            {/* Review: Nico (Google) */}
            <div className={`p-5 rounded-2xl border space-y-3 ${
              isDarkMode ? 'bg-[#0d0d12] border-neutral-800 text-neutral-300' : 'bg-white border-gray-200/90 text-neutral-700'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex text-amber-400 text-xs">★★★★★</div>
                <span className="text-[11px] text-neutral-500">5 days ago</span>
              </div>
              <p className="text-xs leading-relaxed font-normal">
                &ldquo;Really great editing of the resume. Let&apos;s see if employers see it the same way&rdquo;
              </p>
              <div className={`pt-2 border-t flex items-center justify-between ${
                isDarkMode ? 'border-neutral-850' : 'border-gray-100'
              }`}>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-blue-400">G</span>
                  <span className={`text-xs font-bold ${isDarkMode ? 'text-white' : 'text-neutral-800'}`}>Nico</span>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Big Bottom CTA Button */}
        <div className="mt-14 flex flex-col items-center text-center">
          <Link
            href="/resume"
            className="px-10 py-4 rounded-full bg-[#eb5a28] hover:bg-[#d94e1d] text-white text-base sm:text-lg font-bold shadow-2xl shadow-orange-950/80 transition-all transform hover:scale-105 active:scale-95 flex items-center gap-2"
          >
            <span>Try CareerOS yourself</span>
            <ArrowRight size={18} />
          </Link>
          <div className="text-xs text-neutral-500 mt-3 font-normal">
            No credit card required • Ingest resumes & auto-apply across 27+ portals
          </div>
        </div>

      </section>

      {/* Footer & CareerOS Power Engine Link */}
      <footer className={`border-t py-12 px-4 ${
        isDarkMode ? 'bg-[#050508] border-neutral-850 text-neutral-400' : 'bg-white border-gray-200 text-neutral-600'
      }`}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-white text-black flex items-center justify-center font-black text-xs">
              C
            </div>
            <span className={`font-extrabold text-sm ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>CareerOS.io</span>
            <span className="text-xs text-neutral-500 ml-2">© 2026 CareerOS. All rights reserved.</span>
          </div>

          <div className="flex items-center gap-6 text-xs font-medium">
            <Link href="/resume" className={isDarkMode ? 'text-neutral-400 hover:text-white transition' : 'hover:text-neutral-900 transition'}>Resume Builder</Link>
            <Link href="/jobs" className={isDarkMode ? 'text-neutral-400 hover:text-white transition' : 'hover:text-neutral-900 transition'}>Job Search</Link>
            <Link href="/applications" className={isDarkMode ? 'text-neutral-400 hover:text-white transition' : 'hover:text-neutral-900 transition'}>Auto-Apply Bot</Link>
            <Link href="/profile" className={isDarkMode ? 'text-neutral-400 hover:text-white transition' : 'hover:text-neutral-900 transition'}>Knowledge Graph</Link>
            <Link 
              href="/jobs" 
              className={`px-3 py-1 rounded-full font-bold transition flex items-center gap-1 border ${
                isDarkMode 
                  ? 'bg-neutral-900 hover:bg-neutral-800 text-neutral-200 border-neutral-700' 
                  : 'bg-neutral-100 hover:bg-neutral-200 text-neutral-900 border-neutral-300'
              }`}
            >
              <LayoutDashboard size={12} />
              <span>CareerOS Engine</span>
            </Link>
          </div>
        </div>
      </footer>

      {/* Modal for Job Detail */}
      {activeJobModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className={`rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border animate-in fade-in zoom-in-95 duration-150 ${
            isDarkMode ? 'bg-[#111117] border-neutral-800 text-neutral-100' : 'bg-white border-gray-200 text-neutral-900'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl ${activeJobModal.logoBg} flex items-center justify-center text-white font-extrabold text-xs`}>
                  {activeJobModal.logoText}
                </div>
                <div>
                  <h3 className={`font-bold text-base ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>{activeJobModal.fullRole}</h3>
                  <div className="text-xs text-neutral-400">{activeJobModal.company} • {activeJobModal.location}</div>
                </div>
              </div>
              <button 
                onClick={() => setActiveJobModal(null)}
                className="text-neutral-400 hover:text-white text-sm font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className={`p-3 rounded-xl border flex items-center justify-between ${
              isDarkMode ? 'bg-emerald-950/60 border-emerald-800/80' : 'bg-emerald-50 border-emerald-100'
            }`}>
              <span className={`text-xs font-semibold ${isDarkMode ? 'text-emerald-300' : 'text-emerald-800'}`}>ATS Resume Fit Score</span>
              <span className={`text-sm font-black ${isDarkMode ? 'text-emerald-400' : 'text-emerald-700'}`}>{activeJobModal.matchScore}% Match</span>
            </div>

            <div>
              <div className="text-xs font-bold text-neutral-400 mb-1.5">Required Skills:</div>
              <div className="flex flex-wrap gap-1.5">
                {activeJobModal.skills.map((s: string) => (
                  <span key={s} className={`px-2 py-0.5 rounded-md text-[11px] font-medium border ${
                    isDarkMode ? 'bg-[#181822] text-neutral-200 border-neutral-700/60' : 'bg-neutral-100 text-neutral-800 border-neutral-200'
                  }`}>
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-2 flex items-center gap-3">
              <Link
                href="/applications"
                className="flex-1 py-2.5 rounded-full bg-[#eb5a28] hover:bg-[#d94e1d] text-white text-xs font-bold text-center shadow-md transition"
              >
                1-Click Autonomous Apply
              </Link>
              <button
                onClick={() => setActiveJobModal(null)}
                className={`px-4 py-2.5 rounded-full text-xs font-semibold transition border ${
                  isDarkMode ? 'border-neutral-700 text-neutral-300 hover:bg-neutral-800' : 'border-gray-300 hover:bg-gray-50'
                }`}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
