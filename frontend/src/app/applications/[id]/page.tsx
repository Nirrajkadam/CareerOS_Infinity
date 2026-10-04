import React from 'react';
import ApplicationDetailClient from './ApplicationDetailClient';

export function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: 'demo' },
    { id: 'app-101' },
    { id: 'app-102' },
    { id: 'app-103' },
  ];
}

export default function ApplicationDetailPage({ params }: { params: { id: string } }) {
  return <ApplicationDetailClient params={params} />;
}
