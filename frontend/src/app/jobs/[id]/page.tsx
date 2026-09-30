import React, { Suspense } from 'react';
import JobDetailClient from './JobDetailClient';

export function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: 'demo' },
  ];
}

export default function JobDetailPage({ params }: { params: { id: string } }) {
  return (
    <Suspense fallback={<div className="p-8 text-neutral-400 text-xs font-mono">Loading job details...</div>}>
      <JobDetailClient params={params} />
    </Suspense>
  );
}
