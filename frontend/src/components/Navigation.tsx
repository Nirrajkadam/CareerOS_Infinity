'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  FileText, 
  Briefcase, 
  Send, 
  UserCheck, 
  KeyRound, 
  Sliders, 
  ShieldCheck,
  Activity
} from 'lucide-react';

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Resumes', href: '/resume', icon: FileText },
    { name: 'Jobs Feed', href: '/jobs', icon: Briefcase },
    { name: 'Applications', href: '/applications', icon: Send },
    { name: 'Master Profile', href: '/profile', icon: UserCheck },
    { name: 'Vault', href: '/settings/credentials', icon: KeyRound },
    { name: 'Integrations', href: '/settings/integrations', icon: Sliders },
  ];

  return (
    <header className="w-full bg-neutral-900 border-b border-neutral-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-900/40">
              C
            </div>
            <div>
              <span className="font-bold text-white text-lg tracking-tight">CareerOS <span className="text-emerald-500 font-medium text-xs ml-1 px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-800">Infinity</span></span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-2 rounded-md text-xs font-medium transition-all flex items-center gap-1.5 ${
                    isActive
                      ? 'bg-neutral-800 text-emerald-400 font-semibold border border-neutral-700'
                      : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800/50'
                  }`}
                >
                  <Icon size={14} className={isActive ? 'text-emerald-400' : 'text-neutral-500'} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Trust Invariant Status */}
          <div className="hidden sm:flex items-center gap-2 bg-neutral-950 px-3 py-1.5 rounded-full border border-neutral-800 text-[11px]">
            <ShieldCheck size={14} className="text-emerald-500" />
            <span className="text-neutral-300 font-medium">TruthGuard Active</span>
          </div>

        </div>
        <nav aria-label="Mobile navigation" className="flex gap-2 overflow-x-auto pb-3 md:hidden">
          {navItems.map(item => <Link key={item.href} href={item.href} aria-current={pathname === item.href ? 'page' : undefined}
            className={`shrink-0 rounded-lg px-3 py-2 text-xs ${pathname === item.href ? 'bg-neutral-800 text-emerald-400' : 'text-neutral-400'}`}>
            {item.name}
          </Link>)}
        </nav>
      </div>
    </header>
  );
}
