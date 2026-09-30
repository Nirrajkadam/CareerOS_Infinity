'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import Navigation from './Navigation';
import CommandPalette from './CommandPalette';
import VoiceAssistant from './VoiceAssistant';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLandingPage = pathname === '/';

  if (isLandingPage) {
    return (
      <div className="min-h-screen bg-[#fff8f5] text-neutral-900 selection:bg-orange-200">
        {children}
        <CommandPalette />
        <VoiceAssistant />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col">
      <Navigation />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
        <CommandPalette />
        <VoiceAssistant />
      </main>
    </div>
  );
}
