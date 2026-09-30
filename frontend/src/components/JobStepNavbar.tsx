'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { 
  Globe, 
  ChevronDown, 
  FileText, 
  Sparkles, 
  ShieldCheck, 
  Briefcase, 
  Send, 
  Sun,
  Moon,
  ArrowRight
} from 'lucide-react';

interface JobStepNavbarProps {
  isDarkMode?: boolean;
  onToggleTheme?: () => void;
}

export default function JobStepNavbar({ isDarkMode = true, onToggleTheme }: JobStepNavbarProps) {
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [selectedCountry, setSelectedCountry] = useState<'US' | 'IN' | 'UK' | 'EU'>('US');
  const [countryDropdownOpen, setCountryDropdownOpen] = useState(false);
  const navRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
        setCountryDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const countries = [
    { code: 'US', label: 'US (United States)' },
    { code: 'IN', label: 'IN (India)' },
    { code: 'UK', label: 'UK (United Kingdom)' },
    { code: 'EU', label: 'EU (European Union)' },
  ];

  return (
    <div ref={navRef} className="sticky top-0 z-50 w-full px-4 pt-4 pb-2 transition-all">
      <div className={`max-w-6xl mx-auto rounded-full px-5 py-2.5 flex items-center justify-between transition-colors duration-300 ${
        isDarkMode 
          ? 'bg-[#0d0d12]/90 backdrop-blur-xl border border-neutral-800 shadow-[0_4px_24px_rgba(0,0,0,0.6)] text-white' 
          : 'bg-white/95 backdrop-blur-md border border-gray-200/90 shadow-[0_2px_12px_rgba(0,0,0,0.06)] text-neutral-900'
      }`}>
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-extrabold text-xl tracking-tighter shadow-sm group-hover:scale-105 transition-transform ${
            isDarkMode ? 'bg-white text-black' : 'bg-black text-white'
          }`}>
            C
          </div>
          <span className={`font-extrabold text-xl tracking-tight flex items-center ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
            CareerOS<span className="text-neutral-500 font-medium text-base">.io</span>
          </span>
        </Link>

        {/* Center Nav Dropdowns */}
        <nav className={`hidden md:flex items-center gap-6 text-sm font-medium ${
          isDarkMode ? 'text-neutral-300' : 'text-neutral-700'
        }`}>
          
          {/* Resume Dropdown */}
          <div className="relative">
            <button
              onClick={() => setActiveDropdown(activeDropdown === 'resume' ? null : 'resume')}
              onMouseEnter={() => setActiveDropdown('resume')}
              className={`flex items-center gap-1 transition-colors py-1 cursor-pointer ${
                isDarkMode ? 'hover:text-white' : 'hover:text-neutral-950'
              }`}
            >
              <span>Resume</span>
              <ChevronDown size={14} className={`text-neutral-400 transition-transform ${activeDropdown === 'resume' ? 'rotate-180' : ''}`} />
            </button>

            {activeDropdown === 'resume' && (
              <div 
                onMouseLeave={() => setActiveDropdown(null)}
                className={`absolute top-full left-0 mt-3 w-64 rounded-2xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150 ${
                  isDarkMode 
                    ? 'bg-[#121217] border border-neutral-800 shadow-2xl text-neutral-200' 
                    : 'bg-white border border-gray-200 shadow-xl text-neutral-800'
                }`}
              >
                <Link
                  href="/resume"
                  className={`flex items-start gap-3 p-2.5 rounded-xl transition group ${
                    isDarkMode ? 'hover:bg-neutral-800/70' : 'hover:bg-orange-50/60'
                  }`}
                >
                  <div className="p-2 rounded-lg bg-orange-500/20 text-[#eb5a28] mt-0.5">
                    <FileText size={16} />
                  </div>
                  <div>
                    <div className={`font-semibold text-xs transition group-hover:text-[#eb5a28] ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
                      AI Resume Optimizer
                    </div>
                    <div className="text-[11px] text-neutral-400 leading-tight mt-0.5">Score CV & enhance bullet points to 90+ ATS match</div>
                  </div>
                </Link>

                <Link
                  href="/resume"
                  className={`flex items-start gap-3 p-2.5 rounded-xl transition group ${
                    isDarkMode ? 'hover:bg-neutral-800/70' : 'hover:bg-emerald-50/60'
                  }`}
                >
                  <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 mt-0.5">
                    <ShieldCheck size={16} />
                  </div>
                  <div>
                    <div className={`font-semibold text-xs transition group-hover:text-emerald-400 ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
                      TruthGuard Safety Check
                    </div>
                    <div className="text-[11px] text-neutral-400 leading-tight mt-0.5">Never hallucinate experience or fake skills</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* Job Application Dropdown */}
          <div className="relative">
            <button
              onClick={() => setActiveDropdown(activeDropdown === 'jobs' ? null : 'jobs')}
              onMouseEnter={() => setActiveDropdown('jobs')}
              className={`flex items-center gap-1 transition-colors py-1 cursor-pointer ${
                isDarkMode ? 'hover:text-white' : 'hover:text-neutral-950'
              }`}
            >
              <span>Job application</span>
              <ChevronDown size={14} className={`text-neutral-400 transition-transform ${activeDropdown === 'jobs' ? 'rotate-180' : ''}`} />
            </button>

            {activeDropdown === 'jobs' && (
              <div 
                onMouseLeave={() => setActiveDropdown(null)}
                className={`absolute top-full left-0 mt-3 w-68 rounded-2xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150 ${
                  isDarkMode 
                    ? 'bg-[#121217] border border-neutral-800 shadow-2xl text-neutral-200' 
                    : 'bg-white border border-gray-200 shadow-xl text-neutral-800'
                }`}
              >
                <Link
                  href="/jobs"
                  className={`flex items-start gap-3 p-2.5 rounded-xl transition group ${
                    isDarkMode ? 'hover:bg-neutral-800/70' : 'hover:bg-orange-50/60'
                  }`}
                >
                  <div className="p-2 rounded-lg bg-orange-500/20 text-[#eb5a28] mt-0.5">
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <div className={`font-semibold text-xs transition group-hover:text-[#eb5a28] ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
                      Weekly AI Suggestions
                    </div>
                    <div className="text-[11px] text-neutral-400 leading-tight mt-0.5">Handpicked roles matched to your background</div>
                  </div>
                </Link>

                <Link
                  href="/applications"
                  className={`flex items-start gap-3 p-2.5 rounded-xl transition group ${
                    isDarkMode ? 'hover:bg-neutral-800/70' : 'hover:bg-blue-50/60'
                  }`}
                >
                  <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400 mt-0.5">
                    <Send size={16} />
                  </div>
                  <div>
                    <div className={`font-semibold text-xs transition group-hover:text-blue-400 ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
                      Auto-Apply Bot (27+ Portals)
                    </div>
                    <div className="text-[11px] text-neutral-400 leading-tight mt-0.5">Autonomous direct submit with browser telemetry</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

          {/* Cover Letter Dropdown */}
          <div className="relative">
            <button
              onClick={() => setActiveDropdown(activeDropdown === 'cover' ? null : 'cover')}
              onMouseEnter={() => setActiveDropdown('cover')}
              className={`flex items-center gap-1 transition-colors py-1 cursor-pointer ${
                isDarkMode ? 'hover:text-white' : 'hover:text-neutral-950'
              }`}
            >
              <span>Cover letter</span>
              <ChevronDown size={14} className={`text-neutral-400 transition-transform ${activeDropdown === 'cover' ? 'rotate-180' : ''}`} />
            </button>

            {activeDropdown === 'cover' && (
              <div 
                onMouseLeave={() => setActiveDropdown(null)}
                className={`absolute top-full left-0 mt-3 w-64 rounded-2xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150 ${
                  isDarkMode 
                    ? 'bg-[#121217] border border-neutral-800 shadow-2xl text-neutral-200' 
                    : 'bg-white border border-gray-200 shadow-xl text-neutral-800'
                }`}
              >
                <Link
                  href="/resume"
                  className={`flex items-start gap-3 p-2.5 rounded-xl transition group ${
                    isDarkMode ? 'hover:bg-neutral-800/70' : 'hover:bg-orange-50/60'
                  }`}
                >
                  <div className="p-2 rounded-lg bg-orange-500/20 text-[#eb5a28] mt-0.5">
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <div className={`font-semibold text-xs transition group-hover:text-[#eb5a28] ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
                      Tailored Cover Letter
                    </div>
                    <div className="text-[11px] text-neutral-400 leading-tight mt-0.5">Custom company-specific narratives with zero fluff</div>
                  </div>
                </Link>
              </div>
            )}
          </div>

        </nav>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Dark / Light Mode Toggle Button */}
          {onToggleTheme && (
            <button
              onClick={onToggleTheme}
              title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Darkest Mode'}
              className={`p-1.5 sm:px-2.5 sm:py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition ${
                isDarkMode 
                  ? 'bg-neutral-800/80 hover:bg-neutral-700 text-amber-300 border border-neutral-700' 
                  : 'bg-gray-100 hover:bg-gray-200 text-neutral-700 border border-gray-300'
              }`}
            >
              {isDarkMode ? <Sun size={14} className="text-amber-400" /> : <Moon size={14} className="text-neutral-700" />}
              <span className="hidden sm:inline">{isDarkMode ? 'Light' : 'Dark'}</span>
            </button>
          )}

          {/* Country Selector */}
          <div className="relative">
            <button
              onClick={() => setCountryDropdownOpen(!countryDropdownOpen)}
              className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full transition ${
                isDarkMode 
                  ? 'text-neutral-300 hover:text-white hover:bg-neutral-800' 
                  : 'text-neutral-700 hover:text-neutral-950 hover:bg-gray-100'
              }`}
            >
              <Globe size={14} className={isDarkMode ? 'text-neutral-400' : 'text-neutral-600'} />
              <span>{selectedCountry}</span>
              <ChevronDown size={12} className="text-neutral-400" />
            </button>

            {countryDropdownOpen && (
              <div className={`absolute top-full right-0 mt-2 w-44 rounded-xl py-1 z-50 ${
                isDarkMode 
                  ? 'bg-[#121217] border border-neutral-800 shadow-2xl text-neutral-300' 
                  : 'bg-white border border-gray-200 shadow-lg text-neutral-700'
              }`}>
                {countries.map((c) => (
                  <button
                    key={c.code}
                    onClick={() => {
                      setSelectedCountry(c.code as any);
                      setCountryDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-1.5 text-xs font-medium transition flex items-center justify-between ${
                      selectedCountry === c.code 
                        ? 'text-[#eb5a28] font-bold bg-orange-500/10' 
                        : isDarkMode ? 'hover:bg-neutral-800 text-neutral-300' : 'hover:bg-orange-50 text-neutral-700'
                    }`}
                  >
                    <span>{c.label}</span>
                    {selectedCountry === c.code && <span className="text-xs">✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Log in Button */}
          <Link
            href="/jobs"
            className={`px-3 sm:px-4 py-1.5 rounded-full text-xs sm:text-sm font-semibold transition ${
              isDarkMode 
                ? 'border border-neutral-700 text-neutral-200 hover:bg-neutral-800' 
                : 'border border-gray-300 text-neutral-800 hover:bg-gray-50'
            }`}
          >
            Log in
          </Link>

          {/* Get started CTA Button */}
          <Link
            href="/resume"
            className="px-4 sm:px-5 py-1.5 sm:py-2 rounded-full bg-[#eb5a28] hover:bg-[#d94e1d] text-white text-xs sm:text-sm font-bold shadow-md shadow-orange-950/40 transition active:scale-95 flex items-center gap-1"
          >
            <span>Get started</span>
          </Link>

        </div>

      </div>
    </div>
  );
}
