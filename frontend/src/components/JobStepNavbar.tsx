'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
  UserCheck,
  KeyRound,
  Sliders,
  LayoutDashboard,
  Mic
} from 'lucide-react';

interface JobStepNavbarProps {
  isDarkMode?: boolean;
  onToggleTheme?: () => void;
}

export default function JobStepNavbar({ isDarkMode = true, onToggleTheme }: JobStepNavbarProps) {
  const pathname = usePathname();
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

  const mainNavItems = [
    { name: 'Home', href: '/', icon: LayoutDashboard },
    { name: 'Resumes', href: '/resume', icon: FileText },
    { name: 'Jobs', href: '/jobs', icon: Briefcase },
    { name: 'Applications', href: '/applications', icon: Send },
    { name: 'Interview', href: '/interview', icon: Mic },
    { name: 'Profile', href: '/profile', icon: UserCheck },
  ];

  return (
    <div ref={navRef} className="sticky top-0 z-50 w-full px-4 pt-4 pb-2 transition-all">
      <div className={`max-w-6xl mx-auto rounded-full px-5 py-2 flex items-center justify-between transition-colors duration-300 ${
        isDarkMode 
          ? 'bg-[#0d0d12]/90 backdrop-blur-xl border border-neutral-800 shadow-[0_4px_24px_rgba(0,0,0,0.6)] text-white' 
          : 'bg-white/95 backdrop-blur-md border border-gray-200/90 shadow-[0_2px_12px_rgba(0,0,0,0.06)] text-neutral-900'
      }`}>
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group shrink-0">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-extrabold text-xl tracking-tighter shadow-sm group-hover:scale-105 transition-transform ${
            isDarkMode ? 'bg-[#eb5a28] text-white' : 'bg-black text-white'
          }`}>
            C
          </div>
          <span className={`font-extrabold text-lg sm:text-xl tracking-tight flex items-center ${isDarkMode ? 'text-white' : 'text-neutral-900'}`}>
            CareerOS<span className="text-[#eb5a28] font-semibold text-sm sm:text-base">.io</span>
          </span>
        </Link>

        {/* Unified Navigation Links */}
        <nav className={`hidden lg:flex items-center gap-1.5 text-xs font-semibold ${
          isDarkMode ? 'text-neutral-300' : 'text-neutral-700'
        }`}>
          {mainNavItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-[#eb5a28] text-white font-bold shadow-md shadow-orange-950/40'
                    : isDarkMode 
                    ? 'hover:text-white hover:bg-neutral-800/80 text-neutral-300' 
                    : 'hover:text-neutral-950 hover:bg-gray-100 text-neutral-700'
                }`}
              >
                <Icon size={14} className={isActive ? 'text-white' : 'text-neutral-400'} />
                <span>{item.name}</span>
              </Link>
            );
          })}
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
          <div className="relative hidden sm:block">
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

          {/* TruthGuard Active Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 bg-[#111116] px-3 py-1 rounded-full border border-neutral-800 text-[11px] text-neutral-300 font-semibold">
            <ShieldCheck size={13} className="text-emerald-400" />
            <span className="text-emerald-400 font-bold">TruthGuard</span>
          </div>

          {/* Get started CTA Button */}
          <Link
            href="/resume"
            className="px-4 sm:px-5 py-1.5 sm:py-2 rounded-full bg-[#eb5a28] hover:bg-[#d94e1d] text-white text-xs sm:text-sm font-bold shadow-md shadow-orange-950/40 transition active:scale-95 flex items-center gap-1"
          >
            <span>Get Started</span>
          </Link>

        </div>

      </div>

      {/* Mobile Nav Menu */}
      <div className="lg:hidden flex items-center justify-center gap-2 mt-2 py-1.5 px-3 bg-[#0d0d12]/90 backdrop-blur-md border border-neutral-800 rounded-full max-w-md mx-auto overflow-x-auto text-xs">
        {mainNavItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`px-2.5 py-1 rounded-full whitespace-nowrap transition ${
                isActive ? 'bg-[#eb5a28] text-white font-bold' : 'text-neutral-400 hover:text-white'
              }`}
            >
              {item.name}
            </Link>
          );
        })}
      </div>

    </div>
  );
}
