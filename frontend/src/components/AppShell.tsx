'use client';

import React from 'react';
import JobStepNavbar from './JobStepNavbar';
import CommandPalette from './CommandPalette';
import VoiceAssistant from './VoiceAssistant';

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#070709] text-neutral-100 selection:bg-orange-500/30 font-sans antialiased flex flex-col">
      {/* Unified Floating Top Navigation Header */}
      <JobStepNavbar />

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {children}
      </main>

      {/* Global Command Palette & Voice Assistant */}
      <CommandPalette />
      <VoiceAssistant />
    </div>
  );
}
