import React from 'react';
import type { Metadata } from 'next';
import './globals.css';
import AppShell from '../components/AppShell';

export const metadata: Metadata = {
  title: 'CareerOS.io — You apply. You wait. You hear nothing.',
  description: 'CareerOS improves your resume, finds matching jobs, and tailors your application documents to each role. Users get 3× more replies on average.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

