import React from 'react';
import type { Metadata } from 'next';
import './globals.css';
import Navigation from '../components/Navigation';
import AuthGate from '../components/AuthGate';
import CommandPalette from '../components/CommandPalette';
import VoiceAssistant from '../components/VoiceAssistant';

export const metadata: Metadata = {
  title: 'CareerOS Infinity — Honest Job Hunter Platform',
  description: 'Enterprise AI-powered Career Operating System with TruthGuard safety',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-neutral-950 text-neutral-50 font-sans flex flex-col">
        
        <AuthGate>
        {/* Navigation Header Bar */}
        <Navigation />

        {/* Main Canvas Area */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
          
          {/* Global Command Palette interface */}
          <CommandPalette />

          {/* AI Voice Control Assistant */}
          <VoiceAssistant />
        </main>
        </AuthGate>
        
      </body>
    </html>
  );
}
